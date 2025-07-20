#!/usr/bin/env python3
"""
Example usage of the AI Dubbing Tool
Demonstrates how to use the dubbing tool programmatically.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_dubbing_tool import AIDubbingTool


def example_basic_usage():
    """Example of basic usage."""
    print("🎤 Example: Basic Usage")
    print("=" * 40)
    
    # Initialize the dubbing tool
    dubbing_tool = AIDubbingTool(
        whisper_model_name="base",      # Use base Whisper model
        f5_tts_model="F5TTS_v1_Base",   # Use F5-TTS v1 base model
        device="auto",                  # Auto-detect device
        output_dir="example_output"     # Output directory
    )
    
    # Load models
    dubbing_tool.load_models()
    
    # Example: Process a short audio file
    # Note: Replace with actual audio file path
    audio_file = "path/to/your/hindi_audio.wav"
    
    if os.path.exists(audio_file):
        print(f"Processing: {audio_file}")
        
        # Dub the audio
        output_path = dubbing_tool.dub_audio(
            audio_file,
            use_segments=False  # Process entire audio at once for short files
        )
        
        print(f"✅ Dubbing completed! Output: {output_path}")
    else:
        print(f"⚠️  Audio file not found: {audio_file}")
        print("Please provide a valid Hindi audio file path")


def example_advanced_usage():
    """Example of advanced usage with custom settings."""
    print("\n🎤 Example: Advanced Usage")
    print("=" * 40)
    
    # Initialize with custom settings
    dubbing_tool = AIDubbingTool(
        whisper_model_name="large",     # Use large Whisper model for better accuracy
        f5_tts_model="F5TTS_v1_Base",   # Use F5-TTS v1 base model
        device="cuda",                  # Force CUDA usage
        output_dir="advanced_output"    # Custom output directory
    )
    
    # Load models
    dubbing_tool.load_models()
    
    # Example: Process a long audio file with segments
    audio_file = "path/to/your/long_hindi_audio.wav"
    
    if os.path.exists(audio_file):
        print(f"Processing long audio: {audio_file}")
        
        # Process in segments for better memory management
        output_path = dubbing_tool.dub_audio(
            audio_file,
            use_segments=True  # Process in segments for long files
        )
        
        print(f"✅ Long audio dubbing completed! Output: {output_path}")
    else:
        print(f"⚠️  Audio file not found: {audio_file}")


def example_step_by_step():
    """Example showing step-by-step processing."""
    print("\n🎤 Example: Step-by-Step Processing")
    print("=" * 40)
    
    # Initialize tool
    dubbing_tool = AIDubbingTool(
        whisper_model_name="base",
        f5_tts_model="F5TTS_v1_Base",
        device="auto",
        output_dir="step_output"
    )
    
    # Load models
    dubbing_tool.load_models()
    
    audio_file = "path/to/your/hindi_audio.wav"
    
    if os.path.exists(audio_file):
        print(f"Processing: {audio_file}")
        
        # Step 1: Transcribe and translate
        print("\n📝 Step 1: Transcribing and translating...")
        translated_text, transcription_info = dubbing_tool.transcribe_and_translate(audio_file)
        print(f"Translated text: {translated_text}")
        
        # Step 2: Extract reference audio
        print("\n🎵 Step 2: Extracting reference audio...")
        reference_audio_path = dubbing_tool.extract_reference_audio(audio_file, duration=10.0)
        print(f"Reference audio: {reference_audio_path}")
        
        # Step 3: Generate speech with voice cloning
        print("\n🎤 Step 3: Generating speech with voice cloning...")
        output_path = dubbing_tool.generate_speech_with_voice_cloning(
            translated_text,
            reference_audio_path
        )
        print(f"Generated speech: {output_path}")
        
        print(f"\n✅ Step-by-step processing completed! Output: {output_path}")
    else:
        print(f"⚠️  Audio file not found: {audio_file}")


def example_batch_processing():
    """Example of batch processing multiple files."""
    print("\n🎤 Example: Batch Processing")
    print("=" * 40)
    
    # Initialize tool
    dubbing_tool = AIDubbingTool(
        whisper_model_name="base",
        f5_tts_model="F5TTS_v1_Base",
        device="auto",
        output_dir="batch_output"
    )
    
    # Load models once
    dubbing_tool.load_models()
    
    # List of audio files to process
    audio_files = [
        "path/to/audio1.wav",
        "path/to/audio2.wav",
        "path/to/audio3.wav"
    ]
    
    processed_files = []
    
    for i, audio_file in enumerate(audio_files, 1):
        if os.path.exists(audio_file):
            print(f"\n🔄 Processing file {i}/{len(audio_files)}: {audio_file}")
            
            try:
                output_path = dubbing_tool.dub_audio(audio_file, use_segments=True)
                processed_files.append(output_path)
                print(f"✅ File {i} completed: {output_path}")
            except Exception as e:
                print(f"❌ Error processing file {i}: {e}")
        else:
            print(f"⚠️  File not found: {audio_file}")
    
    print(f"\n🎉 Batch processing completed! Processed {len(processed_files)} files")


def example_custom_configuration():
    """Example with custom configuration."""
    print("\n🎤 Example: Custom Configuration")
    print("=" * 40)
    
    # Custom configuration
    config = {
        "whisper_model": "small",        # Medium-sized Whisper model
        "f5_tts_model": "F5TTS_Base",    # Standard F5-TTS model
        "device": "cpu",                 # Use CPU (slower but more compatible)
        "reference_duration": 15.0,      # Use 15 seconds for voice cloning
        "use_segments": True             # Always use segments
    }
    
    # Initialize with custom config
    dubbing_tool = AIDubbingTool(
        whisper_model_name=config["whisper_model"],
        f5_tts_model=config["f5_tts_model"],
        device=config["device"],
        output_dir="custom_output"
    )
    
    # Load models
    dubbing_tool.load_models()
    
    audio_file = "path/to/your/hindi_audio.wav"
    
    if os.path.exists(audio_file):
        print(f"Processing with custom config: {audio_file}")
        print(f"Config: {config}")
        
        output_path = dubbing_tool.dub_audio(
            audio_file,
            use_segments=config["use_segments"]
        )
        
        print(f"✅ Custom configuration processing completed! Output: {output_path}")
    else:
        print(f"⚠️  Audio file not found: {audio_file}")


def main():
    """Run all examples."""
    print("🎤 AI Dubbing Tool Examples")
    print("=" * 50)
    
    # Note: These examples require actual audio files
    # Replace the file paths with your actual Hindi audio files
    
    print("📝 Note: Replace 'path/to/your/hindi_audio.wav' with actual file paths")
    print("to run these examples with real audio files.\n")
    
    # Run examples
    example_basic_usage()
    example_advanced_usage()
    example_step_by_step()
    example_batch_processing()
    example_custom_configuration()
    
    print("\n🎉 All examples completed!")
    print("\n📖 For more information, check the README.md file")


if __name__ == "__main__":
    main() 