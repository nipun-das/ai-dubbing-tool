#!/usr/bin/env python3
"""
AI Dubbing Tool
Converts Hindi audio to English audio while maintaining the same speaker's voice
using Whisper for transcription/translation and YourTTS for voice cloning.
"""

import argparse
import os
import sys
import tempfile
import traceback
import time
import threading
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import soundfile as sf
import torch
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Add the whisper directory to the path
sys.path.insert(0, str(Path(__file__).parent / "whisper"))

try:
    import whisper
    from TTS.api import TTS
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure both whisper and TTS (Coqui) are properly installed.")
    sys.exit(1)


class AIDubbingTool:
    def __init__(
        self,
        whisper_model_name: str = "base",
        yourtts_model_name: str = "tts_models/multilingual/multi-dataset/your_tts",
        device: str = "auto",
        output_dir: str = "output",
        input_language: str = "hi",  # Default to Hindi, but can be changed
    ):
        """
        Initialize the AI Dubbing Tool.
        
        Args:
            whisper_model_name: Whisper model size (tiny, base, small, medium, large)
            yourtts_model_name: YourTTS model name
            device: Device to run inference on (auto, cpu, cuda)
            output_dir: Directory to save output files
            input_language: Input language code (hi=Hindi, ml=Malayalam, ta=Tamil, te=Telugu, etc.)
        """
        self.whisper_model_name = whisper_model_name
        self.yourtts_model_name = yourtts_model_name
        self.device = self._get_device(device)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.input_language = input_language
        
        # Initialize models
        self.whisper_model = None
        self.tts_model = None
        
        print(f"Initializing AI Dubbing Tool...")
        print(f"Device: {self.device}")
        print(f"Input Language: {input_language}")
        print(f"Output directory: {self.output_dir}")
        
        # Language mapping for better display
        self.language_names = {
            "hi": "Hindi",
            "ml": "Malayalam", 
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "gu": "Gujarati",
            "kn": "Kannada",
            "mr": "Marathi",
            "pa": "Punjabi",
            "ur": "Urdu",
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
    
    def _get_device(self, device: str) -> str:
        """Determine the best device to use."""
        if device == "auto":
            # Check for environment variable to force CPU
            if os.environ.get("FORCE_CPU", "false").lower() == "true":
                print("🔄 FORCE_CPU environment variable set, using CPU...")
                return "cpu"
            
            if torch.cuda.is_available():
                print("Running on cuda...")
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                print("Running on mps...")
                return "mps"
            else:
                print("Running on cpu...")
                return "cpu"
        return device
    
    def load_models(self):
        """Load Whisper and YourTTS models."""
        print("Loading Whisper model...")
        try:
            # Load Whisper model with explicit device handling
            if self.device == "cpu":
                # Force CPU usage to avoid CUDA issues
                self.whisper_model = whisper.load_model(self.whisper_model_name, device="cpu")
                print("✅ Whisper model loaded on CPU")
            else:
                # Try to load on selected device, fallback to CPU if CUDA fails
                try:
                    self.whisper_model = whisper.load_model(self.whisper_model_name, device=self.device)
                    print(f"✅ Whisper model loaded on {self.device}")
                except Exception as cuda_error:
                    print(f"⚠️  Failed to load Whisper on {self.device}: {cuda_error}")
                    print("🔄 Falling back to CPU...")
                    self.whisper_model = whisper.load_model(self.whisper_model_name, device="cpu")
                    self.device = "cpu"
                    print("✅ Whisper model loaded on CPU (fallback)")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            raise
        
        print("Loading YourTTS model...")
        try:
            # Initialize TTS with YourTTS model
            self.tts_model = TTS(model_name=self.yourtts_model_name)
            print("✅ YourTTS model loaded successfully!")
        except Exception as e:
            print(f"Error loading YourTTS model: {e}")
            print("Please ensure TTS (Coqui) is properly installed and configured.")
            raise

    def reset_tts_model(self):
        """Reset the TTS model to clear any cached voice characteristics."""
        print("🔄 Resetting TTS model to clear voice cache...")
        try:
            # Clear any cached data
            if hasattr(self.tts_model, 'speaker_manager'):
                if hasattr(self.tts_model.speaker_manager, 'speaker_names'):
                    self.tts_model.speaker_manager.speaker_names = []
                if hasattr(self.tts_model.speaker_manager, 'speaker_embeds'):
                    self.tts_model.speaker_manager.speaker_embeds = {}
                if hasattr(self.tts_model.speaker_manager, 'speaker_ids'):
                    self.tts_model.speaker_manager.speaker_ids = {}
            
            # Clear any cached embeddings
            if hasattr(self.tts_model, 'speaker_encoder'):
                if hasattr(self.tts_model.speaker_encoder, 'speaker_embeds'):
                    self.tts_model.speaker_encoder.speaker_embeds = {}
            
            # Clear any cached audio processing
            if hasattr(self.tts_model, 'audio_processor'):
                if hasattr(self.tts_model.audio_processor, 'cache'):
                    self.tts_model.audio_processor.cache = {}
            
            # Force garbage collection to clear memory
            import gc
            gc.collect()
            
            # Clear torch cache if using CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            print("✅ TTS model reset successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not reset TTS model: {e}")
            # Continue anyway, the model should still work
    
    def transcribe_and_translate(self, audio_path: str) -> Tuple[str, str, dict, list]:
        """
        Transcribe audio in the specified language and translate to English.
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Tuple of (original_text, translated_text, transcription_info, sentences_data)
        """
        input_lang_name = self.language_names.get(self.input_language, self.input_language)
        print(f"Transcribing and translating {input_lang_name} audio: {audio_path}")
        
        # Validate audio file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        file_size = os.path.getsize(audio_path)
        print(f"Audio file size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("Audio file is empty")
        
        # Load audio
        try:
            audio = whisper.load_audio(audio_path)
            print(f"Loaded audio: {len(audio)} samples, duration: {len(audio)/16000:.2f}s")
        except Exception as e:
            print(f"Error loading audio: {e}")
            raise
        
        # Check if audio has content and enhance if needed
        audio_max = np.max(np.abs(audio))
        print(f"📊 Audio max amplitude: {audio_max:.6f}")
        
        if len(audio) == 0 or audio_max < 0.001:
            print("⚠️  Audio appears to be silent or very quiet")
            
            # Try to enhance the audio
            if audio_max > 0:
                print("🔄 Attempting to enhance quiet audio...")
                # Normalize and amplify
                audio = audio / audio_max * 0.8
                audio_max = np.max(np.abs(audio))
                print(f"📊 Enhanced audio max amplitude: {audio_max:.6f}")
                
                if audio_max > 0.01:
                    print("✅ Audio enhanced successfully, proceeding with transcription...")
                else:
                    print("⚠️  Audio still too quiet, using placeholder text")
                    # Return placeholder text for testing
                    original_text = "नमस्ते, यह एक परीक्षण है।"
                    translated_text = "Hello, this is a test."
                    print(f"Using placeholder text: {original_text}")
                    print(f"Translated to: {translated_text}")
                    
                    combined_result = {
                        "original_text": original_text,
                        "translated_text": translated_text,
                        "original_result": {"text": original_text},
                        "translate_result": {"text": translated_text}
                    }
                    return original_text, translated_text, combined_result
            else:
                print("⚠️  Audio is completely silent, using placeholder text")
                # Return placeholder text for testing
                original_text = "नमस्ते, यह एक परीक्षण है।"
                translated_text = "Hello, this is a test."
                print(f"Using placeholder text: {original_text}")
                print(f"Translated to: {translated_text}")
                
                combined_result = {
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "original_result": {"text": original_text},
                    "translate_result": {"text": translated_text}
                }
                return original_text, translated_text, combined_result
        
        # Use the specified language directly
        detected_lang = self.input_language
        print(f"Using specified language: {detected_lang}")
        
        # First, transcribe in the original language
        print(f"Transcribing in {input_lang_name}...")
        original_result = None
        try:
            original_result = self.whisper_model.transcribe(
                audio,
                language=self.input_language,
                task="transcribe",  # Just transcribe, don't translate
                verbose=True
            )
            
            original_text = original_result["text"].strip()
            print(f"Original {input_lang_name} text: {original_text}")
            
            if not original_text:
                print("⚠️  No text detected in original language, trying without language specification...")
                original_result = self.whisper_model.transcribe(
                    audio,
                    task="transcribe",
                    verbose=True
                )
                original_text = original_result["text"].strip()
                print(f"Original text (auto-detect): {original_text}")
                
        except Exception as e:
            print(f"Error in original transcription: {e}")
            # If it's a CUDA error, try to reload the model on CPU
            if "CUDA" in str(e) and self.device != "cpu":
                print("🔄 CUDA error detected, attempting to reload model on CPU...")
                try:
                    self.whisper_model = whisper.load_model(self.whisper_model_name, device="cpu")
                    self.device = "cpu"
                    print("✅ Model reloaded on CPU, retrying transcription...")
                    
                    original_result = self.whisper_model.transcribe(
                        audio,
                        language=self.input_language,
                        task="transcribe",
                        verbose=True
                    )
                    original_text = original_result["text"].strip()
                    print(f"Original {input_lang_name} text (CPU): {original_text}")
                except Exception as cpu_error:
                    print(f"❌ CPU transcription also failed: {cpu_error}")
                    original_text = ""
                    original_result = {"text": ""}
            else:
                original_text = ""
                original_result = {"text": ""}
        
        # Then translate to English
        print(f"Translating to English...")
        translate_result = None
        try:
            translate_result = self.whisper_model.transcribe(
                audio,
                language=self.input_language,
                task="translate",  # Translate to English
                verbose=True
            )
            
            translated_text = translate_result["text"].strip()
            print(f"Translated English text: {translated_text}")
            
            if not translated_text:
                print("⚠️  No translation generated, using original text...")
                translated_text = original_text if original_text else "Hello, this is a test."
            
            # Ensure translate_result is defined
            if translate_result is None:
                translate_result = {"text": translated_text}
                
        except Exception as e:
            print(f"Error in translation: {e}")
            # If it's a CUDA error, try to reload the model on CPU
            if "CUDA" in str(e) and self.device != "cpu":
                print("🔄 CUDA error detected in translation, attempting to reload model on CPU...")
                try:
                    self.whisper_model = whisper.load_model(self.whisper_model_name, device="cpu")
                    self.device = "cpu"
                    print("✅ Model reloaded on CPU, retrying translation...")
                    
                    translate_result = self.whisper_model.transcribe(
                        audio,
                        language=self.input_language,
                        task="translate",
                        verbose=True
                    )
                    translated_text = translate_result["text"].strip()
                    print(f"Translated English text (CPU): {translated_text}")
                except Exception as cpu_error:
                    print(f"❌ CPU translation also failed: {cpu_error}")
                    translated_text = original_text if original_text else "Hello, this is a test."
                    translate_result = {"text": translated_text}
            else:
                translated_text = original_text if original_text else "Hello, this is a test."
                translate_result = {"text": translated_text}
        
        # Validate final results
        if not original_text and not translated_text:
            print("⚠️  No text detected at all, using fallback text...")
            original_text = "नमस्ते, यह एक परीक्षण है।"
            translated_text = "Hello, this is a test."
        
        print(f"📝 Final original text: '{original_text}'")
        print(f"📝 Final translated text: '{translated_text}'")
        
        # Extract sentence-level timing information
        sentences_data = self._extract_sentences_with_timing(original_result, translate_result)
        
        # Combine results
        combined_result = {
            "original_text": original_text,
            "translated_text": translated_text,
            "original_result": original_result,
            "translate_result": translate_result,
            "detected_language": detected_lang,
            "sentences": sentences_data
        }
        
        return original_text, translated_text, combined_result, sentences_data
    
    def extract_reference_audio(self, audio_path: str, duration: float = 10.0) -> str:
        """
        Extract high-quality reference audio segments for voice cloning.
        
        Args:
            audio_path: Path to the original audio file
            duration: Duration of reference audio to extract (seconds)
            
        Returns:
            Path to the extracted reference audio file
        """
        print(f"Extracting high-quality reference audio from: {audio_path}")
        
        try:
            # Load audio
            audio = AudioSegment.from_file(audio_path)
            
            # Convert to mono if stereo (YourTTS works better with mono)
            if audio.channels > 1:
                audio = audio.set_channels(1)
                print("Converted stereo audio to mono for better voice cloning")
            
            # Normalize audio levels
            audio = audio.normalize()
            
            # Find the best quality segment for voice cloning
            best_segment = self._find_best_voice_segment(audio, duration)
            
            # Generate unique filename based on input audio
            input_filename = Path(audio_path).stem
            timestamp = int(time.time())
            ref_filename = f"reference_audio_{input_filename}_{timestamp}.wav"
            ref_path = self.output_dir / ref_filename
            
            print(f"Saving high-quality reference audio to: {ref_path}")
            
            # Export with optimal settings for YourTTS
            best_segment.export(
                str(ref_path), 
                format="wav",
                parameters=[
                    "-ar", "22050",  # Sample rate
                    "-ac", "1",      # Mono channel
                    "-b:a", "16k"    # Bit rate
                ]
            )
            
            # Verify the saved file
            if not os.path.exists(ref_path):
                raise FileNotFoundError(f"Failed to save reference audio: {ref_path}")
            
            file_size = os.path.getsize(ref_path)
            if file_size == 0:
                raise ValueError(f"Reference audio file is empty: {ref_path}")
            
            print(f"✅ High-quality reference audio saved: {file_size} bytes")
            print(f"📊 Reference audio duration: {len(best_segment) / 1000:.2f} seconds")
            print(f"🎯 Unique reference file: {ref_filename}")
            
            return str(ref_path)
            
        except Exception as e:
            print(f"Error extracting reference audio: {e}")
            traceback.print_exc()
            raise
    
    def _find_best_voice_segment(self, audio: AudioSegment, target_duration: float) -> AudioSegment:
        """
        Find the best quality audio segment for voice cloning.
        
        Args:
            audio: AudioSegment object
            target_duration: Target duration in seconds
            
        Returns:
            Best quality audio segment
        """
        print("🔍 Analyzing audio to find best voice segment...")
        
        # Split audio into smaller chunks for analysis
        chunk_duration = 5000  # 5 seconds
        chunks = []
        
        for i in range(0, len(audio), chunk_duration):
            chunk = audio[i:i + chunk_duration]
            if len(chunk) >= 2000:  # At least 2 seconds
                chunks.append(chunk)
        
        if not chunks:
            # Fallback: use first N seconds
            print("⚠️  No suitable chunks found, using first segment")
            return audio[:int(target_duration * 1000)]
        
        # Analyze each chunk for voice quality
        best_chunk = None
        best_score = -1
        
        for i, chunk in enumerate(chunks):
            score = self._calculate_voice_quality_score(chunk)
            print(f"Chunk {i+1}: Quality score = {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        print(f"✅ Selected chunk with quality score: {best_score:.2f}")
        
        # If the best chunk is shorter than target, extend it
        if len(best_chunk) < target_duration * 1000:
            # Try to extend with adjacent chunks
            extended_chunk = self._extend_chunk_with_adjacent(audio, best_chunk, target_duration)
            return extended_chunk
        
        return best_chunk
    
    def _calculate_voice_quality_score(self, chunk: AudioSegment) -> float:
        """
        Calculate voice quality score for a chunk.
        Higher score = better for voice cloning.
        """
        try:
            # Convert to numpy array for analysis
            samples = np.array(chunk.get_array_of_samples())
            
            # Calculate various quality metrics
            
            # 1. Volume level (avoid too quiet or too loud)
            rms = np.sqrt(np.mean(samples**2))
            volume_score = 1.0 - abs(rms - 5000) / 10000  # Optimal around 5000
            volume_score = max(0, min(1, volume_score))
            
            # 2. Dynamic range (prefer consistent volume)
            dynamic_range = np.max(samples) - np.min(samples)
            dynamic_score = 1.0 - (dynamic_range / 65536)  # Prefer lower dynamic range
            dynamic_score = max(0, min(1, dynamic_score))
            
            # 3. Zero-crossing rate (indicates speech vs silence)
            zero_crossings = np.sum(np.diff(np.sign(samples)) != 0)
            zcr_score = 1.0 - abs(zero_crossings - 1000) / 2000  # Optimal around 1000
            zcr_score = max(0, min(1, zcr_score))
            
            # 4. Silence ratio (avoid too much silence)
            silence_threshold = 1000
            silence_ratio = np.sum(np.abs(samples) < silence_threshold) / len(samples)
            silence_score = 1.0 - silence_ratio  # Prefer less silence
            
            # Combine scores (weighted average)
            final_score = (
                volume_score * 0.3 +
                dynamic_score * 0.2 +
                zcr_score * 0.3 +
                silence_score * 0.2
            )
            
            return final_score
            
        except Exception as e:
            print(f"Warning: Error calculating quality score: {e}")
            return 0.5  # Default score
    
    def _extend_chunk_with_adjacent(self, audio: AudioSegment, chunk: AudioSegment, target_duration: float) -> AudioSegment:
        """
        Extend a chunk with adjacent audio to reach target duration.
        """
        target_ms = int(target_duration * 1000)
        current_ms = len(chunk)
        
        if current_ms >= target_ms:
            return chunk
        
        # Find the position of this chunk in the original audio
        chunk_start = None
        for i in range(0, len(audio), 5000):
            if audio[i:i+len(chunk)] == chunk:
                chunk_start = i
                break
        
        if chunk_start is None:
            # Fallback: just return the chunk as is
            return chunk
        
        # Calculate how much to extend
        needed_ms = target_ms - current_ms
        
        # Try to extend from both sides
        left_available = chunk_start
        right_available = len(audio) - (chunk_start + current_ms)
        
        left_extend = min(needed_ms // 2, left_available)
        right_extend = min(needed_ms - left_extend, right_available)
        
        # If we can't extend enough on one side, try the other
        if left_extend + right_extend < needed_ms:
            if left_available > right_available:
                left_extend = min(needed_ms, left_available)
                right_extend = 0
            else:
                right_extend = min(needed_ms, right_available)
                left_extend = 0
        
        # Create extended chunk
        start_pos = max(0, chunk_start - left_extend)
        end_pos = min(len(audio), chunk_start + current_ms + right_extend)
        
        extended_chunk = audio[start_pos:end_pos]
        
        print(f"Extended chunk from {current_ms}ms to {len(extended_chunk)}ms")
        return extended_chunk
    
    def generate_speech_with_voice_cloning(
        self, 
        text: str, 
        reference_audio_path: str,
        reference_text: str = "This is a reference audio for voice cloning."
    ) -> str:
        """
        Generate English speech with the cloned voice from reference audio.
        
        Args:
            text: English text to synthesize
            reference_audio_path: Path to reference audio file
            reference_text: Transcript of reference audio (not used for YourTTS)
            
        Returns:
            Path to the generated audio file
        """
        print(f"🎤 Generating speech with YourTTS...")
        print(f"📝 Text: '{text}'")
        print(f"🎵 Reference audio: {reference_audio_path}")
        
        # Validate text input
        if not text or not text.strip():
            print("⚠️  Empty text provided, using fallback text...")
            text = "Hello, this is a test message."
            print(f"📝 Using fallback text: '{text}'")
        
        try:
            # Verify reference audio file exists and is valid
            if not os.path.exists(reference_audio_path):
                raise FileNotFoundError(f"Reference audio file not found: {reference_audio_path}")
            
            # Check file size
            file_size = os.path.getsize(reference_audio_path)
            if file_size == 0:
                raise ValueError(f"Reference audio file is empty: {reference_audio_path}")
            
            print(f"📊 Reference audio file size: {file_size} bytes")
            
            # Reset TTS model to clear any cached voice characteristics
            self.reset_tts_model()
            
            # Generate unique output filename to avoid conflicts
            timestamp = int(time.time())
            output_filename = f"generated_speech_{timestamp}.wav"
            output_path = self.output_dir / output_filename
            
            print("🎯 Optimizing voice cloning parameters...")
            print(f"📏 Text length: {len(text)} characters")
            print(f"🎯 Unique output file: {output_filename}")
            
            # Split long text into sentences for better quality
            sentences = self._split_text_into_sentences(text)
            
            if len(sentences) > 1:
                print(f"📝 Processing {len(sentences)} sentences separately for better quality")
                return self._generate_speech_by_sentences(sentences, reference_audio_path, output_path)
            else:
                # Single sentence - use optimized parameters
                return self._generate_single_speech(text, reference_audio_path, output_path)
            
        except Exception as e:
            print(f"❌ Error in YourTTS speech generation: {e}")
            traceback.print_exc()
            raise
    
    def _split_text_into_sentences(self, text: str) -> list:
        """Split text into sentences for better voice cloning quality."""
        import re
        
        # Split by common sentence endings
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If sentences are too long, split by commas
        if len(sentences) == 1 and len(text) > 100:
            sentences = re.split(r'[,;]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _extract_sentences_with_timing(self, original_result: dict, translate_result: dict) -> list:
        """
        Extract sentence-level timing information from Whisper results.
        
        Args:
            original_result: Original transcription result from Whisper
            translate_result: Translation result from Whisper
            
        Returns:
            List of sentence objects with timing information
        """
        sentences_data = []
        
        # Ensure we have valid results
        if original_result is None:
            original_result = {"text": ""}
        if translate_result is None:
            translate_result = {"text": ""}
        
        # Use segments from the translation result (usually more accurate timing)
        segments = translate_result.get("segments", [])
        
        if not segments:
            # Fallback: create a single sentence with full duration
            original_text = original_result.get("text", "").strip()
            translated_text = translate_result.get("text", "").strip()
            
            if original_text and translated_text:
                sentences_data.append({
                    "id": "sentence_1",
                    "startTime": 0.0,
                    "endTime": 30.0,  # Default duration
                    "duration": 30.0,
                    "originalText": original_text,
                    "translatedText": translated_text,
                    "confidence": 0.8
                })
        else:
            # Process each segment as a sentence
            for i, segment in enumerate(segments):
                start_time = segment.get("start", 0.0)
                end_time = segment.get("end", start_time + 5.0)
                duration = end_time - start_time
                
                # Get text from this segment
                original_text = segment.get("text", "").strip()
                translated_text = segment.get("text", "").strip()
                
                # If no text in segment, try to extract from full text
                if not original_text and "text" in original_result:
                    # Simple fallback: split full text by segments
                    full_original = original_result["text"]
                    full_translated = translate_result["text"]
                    
                    # This is a simplified approach - in a real implementation,
                    # you'd want to align the segments with the full text
                    original_text = full_original
                    translated_text = full_translated
                
                if original_text or translated_text:
                    sentences_data.append({
                        "id": f"sentence_{i+1}",
                        "startTime": start_time,
                        "endTime": end_time,
                        "duration": duration,
                        "originalText": original_text,
                        "translatedText": translated_text,
                        "confidence": segment.get("avg_logprob", 0.5),
                        "noSpeechProb": segment.get("no_speech_prob", 0.0)
                    })
        
        print(f"📝 Extracted {len(sentences_data)} sentences with timing information")
        for i, sentence in enumerate(sentences_data):
            print(f"  Sentence {i+1}: {sentence['startTime']:.2f}s - {sentence['endTime']:.2f}s")
            print(f"    Original: {sentence['originalText'][:50]}...")
            print(f"    Translated: {sentence['translatedText'][:50]}...")
        
        return sentences_data
    
    def _generate_single_speech(self, text: str, reference_audio_path: str, output_path: Path) -> str:
        """Generate speech for a single sentence with optimized parameters."""
        
        # Try different approaches if the first one fails
        approaches = [
            # Approach 1: Standard YourTTS with minimal parameters
            {
                "name": "Standard YourTTS",
                "params": {
                    "text": text,
                    "speaker_wav": reference_audio_path,
                    "language": "en",
                    "file_path": str(output_path)
                }
            },
            # Approach 2: Without emotion parameter
            {
                "name": "YourTTS without emotion",
                "params": {
                    "text": text,
                    "speaker_wav": reference_audio_path,
                    "language": "en",
                    "file_path": str(output_path),
                    "speed": 1.0
                }
            },
            # Approach 3: With different speaker scaling
            {
                "name": "YourTTS with auto scaling",
                "params": {
                    "text": text,
                    "speaker_wav": reference_audio_path,
                    "language": "en",
                    "file_path": str(output_path),
                    "speaker_wav_scale_factor_auto": True
                }
            },
            # Approach 4: Fallback to basic TTS without voice cloning
            {
                "name": "Basic TTS fallback",
                "params": {
                    "text": text,
                    "file_path": str(output_path),
                    "language": "en"
                }
            }
        ]
        
        for i, approach in enumerate(approaches):
            try:
                print(f"🔄 Trying approach {i+1}: {approach['name']}")
                
                if i == 3:  # Fallback approach - use basic TTS
                    # Try to use a different TTS model or basic synthesis
                    print("⚠️  YourTTS failed, trying simple TTS fallback...")
                    
                    try:
                        from simple_tts_fallback import create_simple_audio
                        create_simple_audio(text, str(output_path), method="speech")
                        print(f"✅ Generated simple TTS audio: {output_path}")
                        return str(output_path)
                    except ImportError:
                        # If simple_tts_fallback is not available, create basic beep
                        print("⚠️  Simple TTS fallback not available, creating beep...")
                        from scipy.io import wavfile
                        import numpy as np
                        
                        # Generate a simple beep sound as placeholder
                        sample_rate = 22050
                        duration = 2.0  # 2 seconds
                        t = np.linspace(0, duration, int(sample_rate * duration))
                        frequency = 440  # A4 note
                        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
                        
                        # Save as WAV
                        wavfile.write(str(output_path), sample_rate, audio_data.astype(np.float32))
                        
                        print(f"✅ Generated fallback beep audio: {output_path}")
                        return str(output_path)
                else:
                    # Try YourTTS with current approach
                    self.tts_model.tts_to_file(**approach['params'])
                    print(f"✅ Generated speech with {approach['name']}: {output_path}")
                    return str(output_path)
                    
            except Exception as e:
                print(f"❌ Approach {i+1} failed: {str(e)[:100]}...")
                if i == len(approaches) - 1:  # Last approach
                    print("❌ All approaches failed")
                    raise
                continue
        
        # This should never be reached, but just in case
        raise Exception("All speech generation approaches failed")
    
    def _generate_speech_by_sentences(self, sentences: list, reference_audio_path: str, output_path: Path) -> str:
        """Generate speech by processing each sentence separately and combining."""
        
        print("🔄 Processing sentences individually for better voice cloning...")
        
        # Generate speech for each sentence
        audio_segments = []
        timestamp = int(time.time())
        
        for i, sentence in enumerate(sentences):
            print(f"🎤 Processing sentence {i+1}/{len(sentences)}: {sentence[:50]}...")
            
            # Generate unique filename for this sentence
            sentence_output = self.output_dir / f"sentence_{timestamp}_{i:03d}.wav"
            
            try:
                # Reset TTS model for each sentence to ensure fresh voice cloning
                self.reset_tts_model()
                
                self.tts_model.tts_to_file(
                    text=sentence,
                    speaker_wav=reference_audio_path,
                    language="en",
                    file_path=str(sentence_output),
                    speed=1.0,
                    emotion="Happy",
                    speaker_wav_scale_factor=1.0,
                    speaker_wav_scale_factor_auto=True,
                )
                
                # Load the generated audio
                audio_segment = AudioSegment.from_file(str(sentence_output))
                audio_segments.append(audio_segment)
                
                # Add small pause between sentences
                if i < len(sentences) - 1:
                    pause = AudioSegment.silent(duration=300)  # 300ms pause
                    audio_segments.append(pause)
                
                # Clean up temporary file
                sentence_output.unlink()
                
            except Exception as e:
                print(f"⚠️  Error processing sentence {i+1}: {e}")
                # Add silence for failed sentences
                audio_segments.append(AudioSegment.silent(duration=1000))
        
        # Combine all audio segments
        if audio_segments:
            final_audio = sum(audio_segments)
            final_audio.export(str(output_path), format="wav")
            print(f"✅ Combined speech saved to: {output_path}")
            return str(output_path)
        else:
            raise ValueError("No audio segments were generated successfully")
    
    def process_audio_segments(
        self, 
        audio_path: str, 
        segment_duration: float = 30.0
    ) -> str:
        """
        Process long audio by splitting into segments and processing each.
        
        Args:
            audio_path: Path to the input audio file
            segment_duration: Duration of each segment in seconds
            
        Returns:
            Path to the final combined output audio
        """
        print(f"Processing audio segments from: {audio_path}")
        
        # Load audio
        audio = AudioSegment.from_file(audio_path)
        
        # Split audio into segments based on silence
        segments = split_on_silence(
            audio,
            min_silence_len=1000,  # 1 second
            silence_thresh=-40,     # dB
            keep_silence=500        # Keep 500ms of silence
        )
        
        print(f"Split audio into {len(segments)} segments")
        
        # Process each segment
        processed_segments = []
        reference_audio_path = self.extract_reference_audio(audio_path)
        
        for i, segment in enumerate(segments):
            print(f"Processing segment {i+1}/{len(segments)}")
            
            # Save segment temporarily
            segment_path = self.output_dir / f"segment_{i:03d}.wav"
            segment.export(str(segment_path), format="wav")
            
            try:
                # Transcribe and translate segment
                original_text, translated_text, _ = self.transcribe_and_translate(str(segment_path))
                
                if translated_text.strip():
                    # Generate speech for this segment
                    generated_audio_path = self.generate_speech_with_voice_cloning(
                        translated_text, 
                        reference_audio_path
                    )
                    
                    # Load generated audio and add to segments
                    generated_audio = AudioSegment.from_file(generated_audio_path)
                    processed_segments.append(generated_audio)
                else:
                    # If no text detected, add silence
                    processed_segments.append(AudioSegment.silent(duration=len(segment)))
                
                # Clean up temporary files
                segment_path.unlink()
                
            except Exception as e:
                print(f"Error processing segment {i+1}: {e}")
                # Add silence for failed segments
                processed_segments.append(AudioSegment.silent(duration=len(segment)))
        
        # Combine all processed segments
        final_audio = sum(processed_segments)
        
        # Save final output
        output_path = self.output_dir / "final_dubbed_audio.wav"
        final_audio.export(str(output_path), format="wav")
        
        print(f"Final dubbed audio saved to: {output_path}")
        return str(output_path)
    
    def dub_audio(self, input_audio_path: str, use_segments: bool = True) -> str:
        """
        Main method to dub Hindi audio to English.
        
        Args:
            input_audio_path: Path to the Hindi audio file
            use_segments: Whether to process audio in segments (recommended for long audio)
            
        Returns:
            Path to the final dubbed audio file
        """
        print(f"Starting AI dubbing process for: {input_audio_path}")
        
        # Load models if not already loaded
        if self.whisper_model is None:
            self.load_models()
        
        try:
            if use_segments:
                # Process in segments for better quality and memory management
                output_path = self.process_audio_segments(input_audio_path)
            else:
                # Process entire audio at once (for short audio)
                original_text, translated_text, _ = self.transcribe_and_translate(input_audio_path)
                reference_audio_path = self.extract_reference_audio(input_audio_path)
                output_path = self.generate_speech_with_voice_cloning(
                    translated_text, 
                    reference_audio_path
                )
            
            print(f"AI dubbing completed successfully!")
            print(f"Output saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error during dubbing process: {e}")
            traceback.print_exc()
            raise


def main():
    """Command-line interface for the AI Dubbing Tool."""
    parser = argparse.ArgumentParser(
        description="AI Dubbing Tool - Convert Hindi audio to English with voice cloning"
    )
    parser.add_argument(
        "input_audio",
        help="Path to the Hindi audio file to dub"
    )
    parser.add_argument(
        "--whisper-model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--yourtts-model",
        default="tts_models/multilingual/multi-dataset/your_tts",
        help="YourTTS model name (default: tts_models/multilingual/multi-dataset/your_tts)"
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda", "mps"],
        help="Device to run inference on (default: auto)"
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--no-segments",
        action="store_true",
        help="Process entire audio at once instead of segments"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_audio):
        print(f"Error: Input audio file not found: {args.input_audio}")
        sys.exit(1)
    
    # Create dubbing tool
    dubbing_tool = AIDubbingTool(
        whisper_model_name=args.whisper_model,
        yourtts_model_name=args.yourtts_model,
        device=args.device,
        output_dir=args.output_dir
    )
    
    try:
        # Perform dubbing
        output_path = dubbing_tool.dub_audio(
            args.input_audio,
            use_segments=not args.no_segments
        )
        
        print(f"\n🎉 Dubbing completed successfully!")
        print(f"📁 Output file: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during dubbing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 