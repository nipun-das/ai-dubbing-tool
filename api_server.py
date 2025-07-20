#!/usr/bin/env python3
"""
Flask API server for AI Dubbing Tool
Handles requests from the React frontend.
"""

import os
import sys
import json
import tempfile
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import traceback

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        print("📄 Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")

# Load .env file at startup
load_env_file()

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_dubbing_tool import AIDubbingTool

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'mp4', 'avi', 'mov', 'mkv', 'webm'}

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_audio_from_video(video_path):
    """Extract audio from video file using multiple methods."""
    print(f"🎬 Extracting audio from video: {video_path}")
    
    # Validate input video file
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    video_size = os.path.getsize(video_path)
    print(f"📊 Video file size: {video_size} bytes")
    
    if video_size == 0:
        raise ValueError("Video file is empty")
    
    audio_path = os.path.join(app.config['OUTPUT_FOLDER'], 'extracted_audio.wav')
    
    # Method 1: Try pydub (works with many formats)
    try:
        print("🔄 Method 1: Trying pydub...")
        from pydub import AudioSegment
        
        audio = AudioSegment.from_file(video_path)
        print(f"✅ Pydub loaded audio: {len(audio)}ms, {audio.channels} channels, {audio.frame_rate}Hz")
        
        # Convert to mono and normalize
        if audio.channels > 1:
            audio = audio.set_channels(1)
            print("🔄 Converted to mono")
        
        # Normalize audio
        audio = audio.normalize()
        
        # Export with optimal settings for Whisper
        audio.export(
            audio_path, 
            format='wav',
            parameters=[
                "-ar", "16000",  # Whisper expects 16kHz
                "-ac", "1",      # Mono
                "-b:a", "16k"    # 16-bit
            ]
        )
        
        # Validate extracted audio
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            print(f"✅ Pydub extraction successful: {os.path.getsize(audio_path)} bytes")
            return audio_path
        else:
            raise Exception("Pydub extraction failed - empty output file")
            
    except Exception as e:
        print(f"❌ Pydub failed: {e}")
    
    # Method 2: Try ffmpeg with different commands
    ffmpeg_commands = [
        # Command 1: Standard extraction
        [
            'ffmpeg', '-i', video_path, 
            '-vn', '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1', 
            audio_path, '-y'
        ],
        # Command 2: More compatible extraction
        [
            'ffmpeg', '-i', video_path, 
            '-vn', '-acodec', 'pcm_s16le', 
            '-ar', '22050', '-ac', '1', 
            '-f', 'wav',
            audio_path, '-y'
        ],
        # Command 3: Force audio stream
        [
            'ffmpeg', '-i', video_path, 
            '-map', '0:a:0',  # Force first audio stream
            '-vn', '-acodec', 'pcm_s16le', 
            '-ar', '16000', '-ac', '1', 
            audio_path, '-y'
        ]
    ]
    
    for i, cmd in enumerate(ffmpeg_commands):
        try:
            print(f"🔄 Method 2.{i+1}: Trying ffmpeg command {i+1}...")
            print(f"Command: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Validate extracted audio
                if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                    print(f"✅ FFmpeg extraction successful: {os.path.getsize(audio_path)} bytes")
                    return audio_path
                else:
                    print("❌ FFmpeg succeeded but output file is empty")
                    continue
            else:
                print(f"❌ FFmpeg failed: {result.stderr}")
                continue
                
        except subprocess.TimeoutExpired:
            print(f"❌ FFmpeg command {i+1} timed out")
            continue
        except Exception as e:
            print(f"❌ FFmpeg command {i+1} error: {e}")
            continue
    
    # Method 3: Try moviepy as last resort
    try:
        print("🔄 Method 3: Trying moviepy...")
        from moviepy.editor import VideoFileClip
        
        video = VideoFileClip(video_path)
        if video.audio is not None:
            audio = video.audio
            audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                print(f"✅ MoviePy extraction successful: {os.path.getsize(audio_path)} bytes")
                return audio_path
        else:
            print("❌ No audio track found in video")
            video.close()
            
    except Exception as e:
        print(f"❌ MoviePy failed: {e}")
    
    # If all methods fail, create a test audio file
    print("⚠️  All extraction methods failed, creating test audio...")
    try:
        from simple_tts_fallback import SimpleTTSFallback
        tts = SimpleTTSFallback()
        tts.create_beep_audio("Test audio", audio_path, duration=5.0)
        print(f"✅ Created test audio: {audio_path}")
        return audio_path
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        raise Exception("All audio extraction methods failed")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Dubbing Tool API is running'
    })

@app.route('/api/dub', methods=['POST'])
def dub_audio():
    """Main dubbing endpoint."""
    try:
        # Check if audio file is present
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get settings
        settings = {}
        if 'settings' in request.form:
            try:
                settings = json.loads(request.form['settings'])
            except json.JSONDecodeError:
                settings = {}
        
        # Set default settings
        default_settings = {
            'inputLanguage': 'hi',
            'whisperModel': 'base',
            'device': 'auto',
            'referenceDuration': 15.0,
            'voiceQualityMode': 'high_quality',
            'useSegments': True
        }
        
        settings = {**default_settings, **settings}
        
        # Save uploaded file
        filename = secure_filename(audio_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(file_path)
        
        # Check if it's a video file and extract audio
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            print(f"🎬 Video file detected: {filename}")
            audio_path = extract_audio_from_video(file_path)
            
            # Validate extracted audio
            if not os.path.exists(audio_path):
                raise Exception("Audio extraction failed - no output file")
            
            audio_size = os.path.getsize(audio_path)
            print(f"📊 Extracted audio size: {audio_size} bytes")
            
            if audio_size == 0:
                raise Exception("Audio extraction failed - empty output file")
            
            print(f"✅ Audio extraction successful: {audio_path}")
        else:
            print(f"🎵 Audio file detected: {filename}")
            audio_path = file_path
        
        # Initialize dubbing tool
        print("Initializing AI Dubbing Tool...")
        dubbing_tool = AIDubbingTool(
            whisper_model_name=settings['whisperModel'],
            input_language=settings['inputLanguage'],
            device=settings['device'],
            output_dir=app.config['OUTPUT_FOLDER']
        )
        
        # Load models
        print("Loading models...")
        dubbing_tool.load_models()
        
        # Process dubbing
        print("Processing dubbing...")
        original_text, translated_text, info, sentences_data = dubbing_tool.transcribe_and_translate(audio_path)
        
        # Extract reference audio
        print("Extracting reference audio...")
        reference_audio_path = dubbing_tool.extract_reference_audio(
            audio_path, 
            duration=settings['referenceDuration']
        )
        
        # Generate dubbed audio
        print("Generating dubbed audio...")
        output_path = dubbing_tool.generate_speech_with_voice_cloning(
            translated_text,
            reference_audio_path
        )
        
        # Ensure the output path is relative to the output folder
        if os.path.isabs(output_path):
            output_filename = os.path.basename(output_path)
        else:
            # Remove 'output/' prefix if present
            output_filename = os.path.basename(output_path)
            if output_filename.startswith('output/'):
                output_filename = output_filename[7:]  # Remove 'output/' prefix
        
        # Return results
        result = {
            'original_text': original_text,
            'translated_text': translated_text,
            'output_audio_path': output_filename,
            'reference_audio_path': os.path.basename(reference_audio_path),
            'sentences': sentences_data,
            'status': '✅ Dubbing completed successfully!',
            'settings_used': settings
        }
        
        print("Dubbing completed successfully!")
        print(f"Output audio path: {output_path}")
        print(f"Output filename: {os.path.basename(output_path)}")
        print(f"Output path type: {type(output_path)}")
        print(f"Output path string: {str(output_path)}")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in dubbing process: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': '❌ Dubbing failed'
        }), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated files."""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_final_audio():
    """Export final edited audio with sentence modifications."""
    try:
        data = request.get_json()
        sentences = data.get('sentences', [])
        reference_audio_filename = data.get('reference_audio_path', '')
        
        if not sentences:
            return jsonify({'error': 'No sentences provided'}), 400
        
        # Construct full path to reference audio
        reference_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], reference_audio_filename)
        
        print(f"Looking for reference audio at: {reference_audio_path}")
        print(f"Reference audio filename: {reference_audio_filename}")
        print(f"Output folder contents: {os.listdir(app.config['OUTPUT_FOLDER'])}")
        
        if not os.path.exists(reference_audio_path):
            return jsonify({'error': f'Reference audio file not found: {reference_audio_path}'}), 400
        
        # Import AudioSegment at the top level
        from pydub import AudioSegment
        
        # Initialize dubbing tool
        dubbing_tool = AIDubbingTool(
            output_dir=app.config['OUTPUT_FOLDER']
        )
        
        # Load models
        dubbing_tool.load_models()
        
        # Generate speech for each sentence with updated text
        audio_segments = []
        
        for i, sentence in enumerate(sentences):
            print(f"Generating speech for sentence {i+1}: {sentence.get('translatedText', '')[:50]}...")
            
            try:
                # Generate speech for this sentence
                sentence_audio_path = dubbing_tool.generate_speech_with_voice_cloning(
                    sentence.get('translatedText', ''),
                    reference_audio_path
                )
                
                # Load the generated audio
                audio_segment = AudioSegment.from_file(sentence_audio_path)
                
                # Add silence before this sentence to match timing
                silence_duration = (sentence.get('startTime', 0) - sum(s.get('duration', 0) for s in sentences[:i])) * 1000
                if silence_duration > 0:
                    silence = AudioSegment.silent(duration=silence_duration)
                    audio_segments.append(silence)
                
                audio_segments.append(audio_segment)
                
                # Clean up temporary file
                os.remove(sentence_audio_path)
                
            except Exception as e:
                print(f"Error generating speech for sentence {i+1}: {e}")
                # Add silence for failed sentences
                audio_segments.append(AudioSegment.silent(duration=1000))
        
        # Combine all audio segments
        if audio_segments:
            final_audio = sum(audio_segments)
            
            # Save final output
            output_filename = f"final_edited_audio_{int(time.time())}.wav"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            final_audio.export(output_path, format="wav")
            
            print(f"Final edited audio saved to: {output_path}")
            
            return jsonify({
                'success': True,
                'output_filename': output_filename,
                'message': 'Final audio exported successfully'
            })
        else:
            return jsonify({'error': 'No audio segments generated'}), 500
            
    except Exception as e:
        print(f"Error in export process: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': '❌ Export failed'
        }), 500

@app.route('/api/refine-dialogue', methods=['POST'])
def refine_dialogue():
    """Refine dialogue using Gemini API with timing constraints."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        original_text = data.get('originalText', '')
        current_text = data.get('currentText', '')
        refinement_prompt = data.get('refinementPrompt', '')
        style = data.get('style', 'natural')
        start_time = data.get('startTime', 0)
        duration = data.get('duration', 0)
        context = data.get('context', '')
        
        if not refinement_prompt:
            return jsonify({'error': 'Refinement prompt is required'}), 400
        
        # Create the prompt for Gemini
        system_prompt = f"""You are an expert dialogue editor for video dubbing. Your task is to refine dialogue while maintaining strict timing constraints.

CONTEXT:
- Original text: "{original_text}"
- Current dubbed text: "{current_text}"
- Timing: {duration:.2f} seconds (start: {start_time:.2f}s)
- Style preference: {style}
- User request: "{refinement_prompt}"

CONSTRAINTS:
1. The refined text MUST fit within {duration:.2f} seconds when spoken
2. Maintain the same meaning and key information as the original
3. Keep the emotional tone and context appropriate
4. Ensure natural speech flow and pronunciation
5. Consider the timing constraints - shorter is better if it fits the duration

STYLE GUIDELINES:
- Natural: Conversational, flowing, easy to speak
- Formal: Professional, structured, clear
- Casual: Relaxed, informal, friendly
- Emotional: Expressive, dramatic, engaging
- Concise: Short, direct, to the point
- Detailed: Descriptive, elaborate, comprehensive

Return ONLY the refined text, nothing else. Make it ready for voice synthesis."""

        # Try to use Gemini API (free tier)
        try:
            import google.generativeai as genai
            
            # You can get a free API key from https://makersuite.google.com/app/apikey
            # For now, we'll use a fallback approach
            api_key = os.getenv('GEMINI_API_KEY')
            
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                response = model.generate_content(system_prompt)
                refined_text = response.text.strip()
                
                # Clean up the response
                refined_text = refined_text.replace('"', '').replace('"', '')
                if refined_text.startswith('"') and refined_text.endswith('"'):
                    refined_text = refined_text[1:-1]
                
                return jsonify({
                    'refinedText': refined_text,
                    'originalText': original_text,
                    'style': style,
                    'duration': duration
                })
            else:
                # Fallback to local refinement logic
                raise Exception("No Gemini API key configured")
                
        except Exception as e:
            print(f"Gemini API failed: {e}")
            # Fallback refinement logic
            refined_text = apply_local_refinement(
                original_text, current_text, refinement_prompt, style, duration
            )
            
            return jsonify({
                'refinedText': refined_text,
                'originalText': original_text,
                'style': style,
                'duration': duration,
                'note': 'Used local refinement (Gemini API not available)'
            })
            
    except Exception as e:
        print(f"Error in dialogue refinement: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Failed to refine dialogue: {str(e)}'}), 500

def apply_local_refinement(original_text, current_text, refinement_prompt, style, duration):
    """Local fallback for dialogue refinement without external API."""
    
    # Estimate words per second (average speaking rate)
    words_per_second = 2.5  # Conservative estimate
    max_words = int(duration * words_per_second)
    
    # Style-based transformations
    style_transformations = {
        'natural': {
            'additions': ['you know', 'well', 'actually', 'basically'],
            'contractions': True,
            'filler_words': True
        },
        'formal': {
            'additions': [],
            'contractions': False,
            'filler_words': False
        },
        'casual': {
            'additions': ['hey', 'so', 'like', 'right'],
            'contractions': True,
            'filler_words': True
        },
        'emotional': {
            'additions': ['really', 'absolutely', 'incredibly', 'amazingly'],
            'contractions': True,
            'filler_words': True
        },
        'concise': {
            'additions': [],
            'contractions': True,
            'filler_words': False
        },
        'detailed': {
            'additions': ['specifically', 'in detail', 'precisely', 'exactly'],
            'contractions': False,
            'filler_words': False
        }
    }
    
    # Get current word count
    current_words = len(current_text.split())
    
    # Apply refinement based on prompt keywords
    refined_text = current_text
    
    # Handle common refinement requests
    if 'shorter' in refinement_prompt.lower() or 'concise' in refinement_prompt.lower():
        # Make it shorter
        words = current_text.split()
        if len(words) > max_words:
            refined_text = ' '.join(words[:max_words])
    
    elif 'longer' in refinement_prompt.lower() or 'detailed' in refinement_prompt.lower():
        # Add more detail if there's time
        if current_words < max_words * 0.8:
            style_config = style_transformations.get(style, style_transformations['natural'])
            if style_config['additions']:
                refined_text = f"{style_config['additions'][0]} {current_text}"
    
    elif 'natural' in refinement_prompt.lower():
        # Make it more natural
        style_config = style_transformations['natural']
        if style_config['contractions']:
            refined_text = refined_text.replace(" do not ", " don't ")
            refined_text = refined_text.replace(" cannot ", " can't ")
            refined_text = refined_text.replace(" will not ", " won't ")
    
    elif 'formal' in refinement_prompt.lower():
        # Make it more formal
        refined_text = refined_text.replace(" don't ", " do not ")
        refined_text = refined_text.replace(" can't ", " cannot ")
        refined_text = refined_text.replace(" won't ", " will not ")
    
    # Ensure it fits within duration
    words = refined_text.split()
    if len(words) > max_words:
        refined_text = ' '.join(words[:max_words])
    
    return refined_text

@app.route('/api/reprocess-sentence', methods=['POST'])
def reprocess_sentence():
    """Reprocess a single sentence with refined text and replace it in the original audio."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        sentence_id = data.get('sentenceId')
        original_text = data.get('originalText', '')
        refined_text = data.get('refinedText', '')
        start_time = data.get('startTime', 0)
        duration = data.get('duration', 0)
        reference_audio_path = data.get('referenceAudioPath', '')
        use_voice_cloning = data.get('useVoiceCloning', True)
        original_audio_path = data.get('originalAudioPath', '')  # Path to original full audio
        
        if not refined_text:
            return jsonify({'error': 'Refined text is required'}), 400
        
        print(f"🔄 Reprocessing sentence {sentence_id}")
        print(f"📝 Original text: {original_text}")
        print(f"✨ Refined text: {refined_text}")
        print(f"⏱️ Start time: {start_time}s, Duration: {duration}s")
        print(f"🎵 Original audio: {original_audio_path}")
        
        # Construct full path to reference audio
        full_reference_path = os.path.join(app.config['OUTPUT_FOLDER'], reference_audio_path)
        
        if not os.path.exists(full_reference_path):
            print(f"❌ Reference audio file not found: {full_reference_path}")
            print(f"📁 Available files: {os.listdir(app.config['OUTPUT_FOLDER'])}")
            
            # Try to find reference audio with different names
            possible_names = ['reference_audio.wav', 'reference.wav', 'ref_audio.wav']
            for name in possible_names:
                test_path = os.path.join(app.config['OUTPUT_FOLDER'], name)
                if os.path.exists(test_path):
                    print(f"✅ Found alternative reference audio: {test_path}")
                    full_reference_path = test_path
                    break
            else:
                return jsonify({'error': f'Reference audio file not found: {full_reference_path}'}), 400
        
        print(f"🎵 Reference audio: {full_reference_path}")
        
        # Debug: List files in output directory
        print(f"📁 Output directory contents: {os.listdir(app.config['OUTPUT_FOLDER'])}")
        
        # Initialize dubbing tool
        dubbing_tool = AIDubbingTool(
            output_dir=app.config['OUTPUT_FOLDER']
        )
        
        # Load models
        print("🔧 Loading AI models...")
        dubbing_tool.load_models()
        
        # Generate new audio for the refined text using voice cloning
        print(f"🎤 Generating speech with voice cloning for: '{refined_text}'")
        
        try:
            sentence_audio_path = dubbing_tool.generate_speech_with_voice_cloning(
                refined_text,
                full_reference_path
            )
            
            # Verify the generated audio is valid
            if not os.path.exists(sentence_audio_path):
                raise Exception("Voice cloning failed - no output file generated")
            
            audio_size = os.path.getsize(sentence_audio_path)
            if audio_size < 1000:  # Less than 1KB is suspicious
                raise Exception("Voice cloning failed - generated audio too small")
            
            print(f"✅ Voice cloning successful: {sentence_audio_path} ({audio_size} bytes)")
            
        except Exception as voice_error:
            print(f"⚠️ Voice cloning failed: {voice_error}")
            print("🔄 Falling back to basic TTS...")
            
            # Fallback to basic TTS without voice cloning
            try:
                from TTS.api import TTS
                basic_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                
                # Create temporary file for basic TTS
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    basic_tts.tts_to_file(text=refined_text, file_path=tmp_file.name)
                    sentence_audio_path = tmp_file.name
                
                print(f"✅ Basic TTS fallback successful: {sentence_audio_path}")
                
            except Exception as basic_error:
                print(f"❌ Basic TTS also failed: {basic_error}")
                # Try YourTTS with default speaker as last resort
                try:
                    print("🔄 Trying YourTTS with default speaker...")
                    from TTS.api import TTS
                    yourtts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
                    
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                        yourtts.tts_to_file(
                            text=refined_text, 
                            file_path=tmp_file.name,
                            speaker="ljspeech",
                            language="en"
                        )
                        sentence_audio_path = tmp_file.name
                    
                    print(f"✅ YourTTS with default speaker successful: {sentence_audio_path}")
                    
                except Exception as yourtts_error:
                    print(f"❌ YourTTS with default speaker also failed: {yourtts_error}")
                    # Create a simple beep as last resort
                    import numpy as np
                    from scipy.io import wavfile
                    
                    sample_rate = 22050
                    duration_sec = max(2.0, len(refined_text.split()) * 0.5)  # 0.5s per word
                    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec))
                    frequency = 440  # A4 note
                    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
                    
                    sentence_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], f"fallback_{sentence_id}.wav")
                    wavfile.write(sentence_audio_path, sample_rate, audio_data.astype(np.float32))
                    print(f"⚠️ Using fallback beep: {sentence_audio_path}")
        
        # Now replace the sentence in the original audio
        if original_audio_path:
            print("🎵 Replacing sentence in original audio...")
            # Construct full path to original audio
            full_original_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], original_audio_path)
            
            if not os.path.exists(full_original_audio_path):
                print(f"❌ Original audio file not found: {full_original_audio_path}")
                # Just return the individual sentence audio
                sentence_filename = os.path.basename(sentence_audio_path)
                return jsonify({
                    'success': True,
                    'sentenceId': sentence_id,
                    'refinedText': refined_text,
                    'audioPath': sentence_filename,
                    'audioUrl': f'/api/download/{sentence_filename}',
                    'message': 'Sentence audio reprocessed successfully (original audio not found)'
                })
            
            modified_audio_path = replace_sentence_in_audio(
                full_original_audio_path,
                sentence_id,
                sentence_audio_path,
                start_time,
                duration
            )
            
            # Return both individual sentence and modified full audio
            sentence_filename = os.path.basename(sentence_audio_path)
            modified_audio_filename = os.path.basename(modified_audio_path)
            
            return jsonify({
                'success': True,
                'sentenceId': sentence_id,
                'refinedText': refined_text,
                'sentenceAudioPath': sentence_filename,
                'sentenceAudioUrl': f'/api/download/{sentence_filename}',
                'modifiedAudioPath': modified_audio_filename,
                'modifiedAudioUrl': f'/api/download/{modified_audio_filename}',
                'message': 'Sentence reprocessed and replaced in original audio'
            })
        else:
            # Just return the individual sentence audio
            sentence_filename = os.path.basename(sentence_audio_path)
            
            return jsonify({
                'success': True,
                'sentenceId': sentence_id,
                'refinedText': refined_text,
                'audioPath': sentence_filename,
                'audioUrl': f'/api/download/{sentence_filename}',
                'message': 'Sentence audio reprocessed successfully'
            })
        
    except Exception as e:
        print(f"❌ Error reprocessing sentence: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': '❌ Sentence reprocessing failed'
        }), 500

def replace_sentence_in_audio(original_audio_path, sentence_id, new_sentence_audio_path, start_time, duration):
    """Replace a specific sentence in the original audio with new audio."""
    try:
        from pydub import AudioSegment
        
        print(f"🎵 Replacing sentence {sentence_id} in original audio...")
        print(f"📁 Original audio: {original_audio_path}")
        print(f"📁 New sentence audio: {new_sentence_audio_path}")
        print(f"⏱️ Start time: {start_time}s, Duration: {duration}s")
        
        # Load the original audio
        original_audio = AudioSegment.from_file(original_audio_path)
        print(f"📊 Original audio: {len(original_audio)}ms")
        
        # Load the new sentence audio
        new_sentence_audio = AudioSegment.from_file(new_sentence_audio_path)
        print(f"📊 New sentence audio: {len(new_sentence_audio)}ms")
        
        # Convert times to milliseconds
        start_ms = int(start_time * 1000)
        duration_ms = int(duration * 1000)
        end_ms = start_ms + duration_ms
        
        print(f"⏱️ Replacing audio from {start_ms}ms to {end_ms}ms")
        
        # Split the original audio into three parts
        before_sentence = original_audio[:start_ms]
        after_sentence = original_audio[end_ms:]
        
        print(f"📊 Before sentence: {len(before_sentence)}ms")
        print(f"📊 After sentence: {len(after_sentence)}ms")
        
        # Combine the parts: before + new_sentence + after
        modified_audio = before_sentence + new_sentence_audio + after_sentence
        
        print(f"📊 Modified audio: {len(modified_audio)}ms")
        
        # Save the modified audio
        modified_audio_filename = f"modified_audio_sentence_{sentence_id}_{int(time.time())}.wav"
        modified_audio_path = os.path.join(app.config['OUTPUT_FOLDER'], modified_audio_filename)
        
        modified_audio.export(modified_audio_path, format="wav")
        print(f"✅ Modified audio saved: {modified_audio_path}")
        
        return modified_audio_path
        
    except Exception as e:
        print(f"❌ Error replacing sentence in audio: {e}")
        traceback.print_exc()
        raise

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get available settings and options."""
    return jsonify({
        'languages': [
            {'value': 'hi', 'label': 'Hindi'},
            {'value': 'ml', 'label': 'Malayalam'},
            {'value': 'ta', 'label': 'Tamil'},
            {'value': 'te', 'label': 'Telugu'},
            {'value': 'bn', 'label': 'Bengali'},
            {'value': 'gu', 'label': 'Gujarati'},
            {'value': 'kn', 'label': 'Kannada'},
            {'value': 'mr', 'label': 'Marathi'},
            {'value': 'pa', 'label': 'Punjabi'},
            {'value': 'ur', 'label': 'Urdu'},
            {'value': 'en', 'label': 'English'},
            {'value': 'es', 'label': 'Spanish'},
            {'value': 'fr', 'label': 'French'},
            {'value': 'de', 'label': 'German'},
            {'value': 'it', 'label': 'Italian'},
            {'value': 'pt', 'label': 'Portuguese'},
            {'value': 'ru', 'label': 'Russian'},
            {'value': 'ja', 'label': 'Japanese'},
            {'value': 'ko', 'label': 'Korean'},
            {'value': 'zh', 'label': 'Chinese'}
        ],
        'whisper_models': [
            {'value': 'tiny', 'label': 'Tiny (39MB)', 'description': 'Fastest, good quality'},
            {'value': 'base', 'label': 'Base (74MB)', 'description': 'Fast, better quality'},
            {'value': 'small', 'label': 'Small (244MB)', 'description': 'Medium speed, good quality'},
            {'value': 'medium', 'label': 'Medium (769MB)', 'description': 'Slower, better quality'},
            {'value': 'large', 'label': 'Large (1550MB)', 'description': 'Slowest, best quality'}
        ],
        'devices': [
            {'value': 'auto', 'label': 'Auto (Recommended)'},
            {'value': 'cpu', 'label': 'CPU'},
            {'value': 'cuda', 'label': 'CUDA (GPU)'},
            {'value': 'mps', 'label': 'MPS (Apple Silicon)'}
        ],
        'quality_modes': [
            {'value': 'standard', 'label': 'Standard', 'description': 'Faster processing'},
            {'value': 'high_quality', 'label': 'High Quality', 'description': 'Better voice cloning'},
            {'value': 'ultra_quality', 'label': 'Ultra Quality', 'description': 'Best quality, slower'}
        ]
    })

if __name__ == '__main__':
    print("🎤 Starting AI Dubbing Tool API Server...")
    print("=" * 50)
    print("📡 API Endpoints:")
    print("   GET  /api/health     - Health check")
    print("   POST /api/dub        - Process dubbing")
    print("   GET  /api/settings   - Get available settings")
    print("   GET  /api/download/<filename> - Download files")
    print("=" * 50)
    print("🌐 Server will start on http://localhost:5000")
    print("📱 React frontend should connect to this API")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    ) 