#!/usr/bin/env python3
"""
Test script for audio processing
Verifies that audio loading, extraction, and processing work correctly.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_audio_creation():
    """Test creating a test audio file."""
    print("🎵 Testing audio file creation...")
    
    try:
        from pydub import AudioSegment
        from pydub.generators import Sine
        
        # Create a simple test audio file
        sample_rate = 24000
        duration = 5000  # 5 seconds
        
        # Generate a simple sine wave
        generator = Sine(440)  # 440 Hz tone
        audio = generator.to_audio_segment(duration=duration)
        
        # Set sample rate
        audio = audio.set_frame_rate(sample_rate)
        
        # Save test audio
        test_audio_path = "test_audio.wav"
        audio.export(test_audio_path, format="wav")
        
        print(f"✅ Test audio created: {test_audio_path}")
        print(f"   Duration: {len(audio) / 1000:.2f} seconds")
        print(f"   Sample rate: {audio.frame_rate} Hz")
        print(f"   Channels: {audio.channels}")
        
        return test_audio_path
        
    except Exception as e:
        print(f"❌ Audio creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_audio_extraction(test_audio_path):
    """Test audio extraction functionality."""
    print("\n🎤 Testing audio extraction...")
    
    try:
        from ai_dubbing_tool import AIDubbingTool
        
        # Create dubbing tool instance
        dubbing_tool = AIDubbingTool(
            whisper_model_name="tiny",  # Use tiny model for testing
            f5_tts_model="F5TTS_v1_Base",
            device="cpu",  # Use CPU for testing
            output_dir="test_output"
        )
        
        # Test reference audio extraction
        reference_path = dubbing_tool.extract_reference_audio(test_audio_path, duration=3.0)
        
        print(f"✅ Reference audio extracted: {reference_path}")
        
        # Verify the extracted file
        if os.path.exists(reference_path):
            file_size = os.path.getsize(reference_path)
            print(f"   File size: {file_size} bytes")
            
            if file_size > 0:
                print("✅ Reference audio extraction successful")
                return reference_path
            else:
                print("❌ Reference audio file is empty")
                return None
        else:
            print("❌ Reference audio file not found")
            return None
            
    except Exception as e:
        print(f"❌ Audio extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_whisper_processing(test_audio_path):
    """Test Whisper transcription."""
    print("\n🔊 Testing Whisper transcription...")
    
    try:
        from ai_dubbing_tool import AIDubbingTool
        
        # Create dubbing tool instance
        dubbing_tool = AIDubbingTool(
            whisper_model_name="tiny",  # Use tiny model for testing
            f5_tts_model="F5TTS_v1_Base",
            device="cpu",  # Use CPU for testing
            output_dir="test_output"
        )
        
        # Load Whisper model
        print("Loading Whisper model...")
        dubbing_tool.load_models()
        
        # Test transcription
        print("Transcribing test audio...")
        translated_text, transcription_info = dubbing_tool.transcribe_and_translate(test_audio_path)
        
        print(f"✅ Transcription successful")
        print(f"   Translated text: '{translated_text}'")
        
        return translated_text
        
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def cleanup_test_files():
    """Clean up test files."""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "test_audio.wav",
        "test_output/reference_audio.wav"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"⚠️  Could not remove {file_path}: {e}")
    
    # Remove test output directory if empty
    test_output_dir = Path("test_output")
    if test_output_dir.exists() and not any(test_output_dir.iterdir()):
        try:
            test_output_dir.rmdir()
            print("✅ Removed empty test_output directory")
        except Exception as e:
            print(f"⚠️  Could not remove test_output directory: {e}")

def main():
    """Run all audio processing tests."""
    print("🎵 Audio Processing Test")
    print("=" * 50)
    
    # Create test audio
    test_audio_path = test_audio_creation()
    if not test_audio_path:
        print("❌ Cannot proceed without test audio")
        return
    
    # Test audio extraction
    reference_path = test_audio_extraction(test_audio_path)
    if not reference_path:
        print("❌ Audio extraction failed")
        cleanup_test_files()
        return
    
    # Test Whisper processing
    translated_text = test_whisper_processing(test_audio_path)
    if translated_text is None:
        print("❌ Whisper processing failed")
        cleanup_test_files()
        return
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print("✅ Audio creation: PASSED")
    print("✅ Audio extraction: PASSED")
    print("✅ Whisper processing: PASSED")
    
    print("\n🎉 All audio processing tests passed!")
    print("The AI dubbing tool should work correctly with real audio files.")
    
    # Cleanup
    cleanup_test_files()

if __name__ == "__main__":
    main() 