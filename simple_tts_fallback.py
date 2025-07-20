#!/usr/bin/env python3
"""
Simple TTS Fallback
Provides basic text-to-speech functionality when YourTTS fails.
"""

import os
import numpy as np
from pathlib import Path
from scipy.io import wavfile
import librosa
import soundfile as sf

class SimpleTTSFallback:
    """Simple TTS fallback that generates basic speech-like audio."""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        
    def text_to_speech(self, text: str, output_path: str, duration_per_word: float = 0.5):
        """
        Generate simple speech-like audio from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            duration_per_word: Duration per word in seconds
        """
        print(f"🎤 Generating simple TTS for: '{text}'")
        
        # Split text into words
        words = text.split()
        total_duration = len(words) * duration_per_word
        
        # Generate audio
        t = np.linspace(0, total_duration, int(self.sample_rate * total_duration))
        
        # Create a simple speech-like waveform
        # Use different frequencies for different parts of speech
        audio_data = np.zeros_like(t)
        
        for i, word in enumerate(words):
            # Calculate timing for this word
            start_time = i * duration_per_word
            end_time = (i + 1) * duration_per_word
            
            # Find indices for this word
            start_idx = int(start_time * self.sample_rate)
            end_idx = int(end_time * self.sample_rate)
            
            if start_idx < len(t) and end_idx <= len(t):
                # Generate a simple tone for this word
                word_duration = end_time - start_time
                word_t = np.linspace(0, word_duration, end_idx - start_idx)
                
                # Use different frequencies based on word length
                base_freq = 200 + (len(word) * 20)  # Longer words = higher pitch
                
                # Add some variation
                freq_variation = np.sin(word_t * 2) * 10
                frequency = base_freq + freq_variation
                
                # Generate tone with envelope
                tone = np.sin(2 * np.pi * frequency * word_t)
                
                # Apply envelope (fade in/out)
                envelope = np.ones_like(word_t)
                fade_samples = int(0.1 * self.sample_rate)  # 100ms fade
                if len(envelope) > 2 * fade_samples:
                    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
                
                tone = tone * envelope * 0.3  # Reduce volume
                
                # Add to main audio
                audio_data[start_idx:end_idx] = tone
        
        # Normalize audio
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data)) * 0.8
        
        # Save audio
        sf.write(output_path, audio_data, self.sample_rate)
        
        print(f"✅ Simple TTS audio saved: {output_path}")
        return output_path
    
    def create_beep_audio(self, text: str, output_path: str, duration: float = 2.0):
        """
        Create a simple beep audio as placeholder.
        
        Args:
            text: Text (not used, but kept for interface compatibility)
            output_path: Path to save the audio file
            duration: Duration of the beep in seconds
        """
        print(f"🔊 Creating beep audio placeholder...")
        
        # Generate a simple beep sound
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        frequency = 440  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some variation to make it more interesting
        envelope = np.exp(-t * 0.5)  # Exponential decay
        audio_data = audio_data * envelope
        
        # Save as WAV
        sf.write(output_path, audio_data, self.sample_rate)
        
        print(f"✅ Beep audio saved: {output_path}")
        return output_path

def create_simple_audio(text: str, output_path: str, method: str = "speech"):
    """
    Create simple audio from text using the specified method.
    
    Args:
        text: Text to convert
        output_path: Output file path
        method: "speech" or "beep"
    """
    tts = SimpleTTSFallback()
    
    if method == "speech":
        return tts.text_to_speech(text, output_path)
    else:
        return tts.create_beep_audio(text, output_path)

if __name__ == "__main__":
    # Test the simple TTS
    tts = SimpleTTSFallback()
    
    # Test speech generation
    test_text = "Hello, this is a test of the simple TTS system."
    output_file = "test_simple_tts.wav"
    
    tts.text_to_speech(test_text, output_file)
    print(f"Test completed. Check {output_file}") 