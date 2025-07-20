#!/usr/bin/env python3
"""
Test script for Malayalam transcription and translation
Demonstrates the original Malayalam text and English translation.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_dubbing_tool import AIDubbingTool


def test_malayalam_transcription(audio_file: str = None):
    """Test Malayalam transcription and translation."""
    
    print("🌴 Malayalam Transcription Test")
    print("=" * 40)
    
    try:
        # Initialize tool for Malayalam
        tool = AIDubbingTool(
            whisper_model_name="base",
            input_language="ml",  # Malayalam
            output_dir="test_output"
        )
        
        print("✅ Initialized for Malayalam")
        
        # Load models
        tool.load_models()
        print("✅ Models loaded successfully")
        
        if audio_file and os.path.exists(audio_file):
            print(f"🎵 Processing Malayalam audio: {audio_file}")
            
            # Test transcription and translation
            original_text, translated_text, info = tool.transcribe_and_translate(audio_file)
            
            print("\n" + "="*50)
            print("📝 RESULTS:")
            print("="*50)
            print(f"🌴 Original Malayalam: {original_text}")
            print(f"🇺🇸 English Translation: {translated_text}")
            print("="*50)
            
            # Show additional info if available
            if info.get("original_result"):
                confidence = info["original_result"].get("confidence", "N/A")
                print(f"🎯 Transcription Confidence: {confidence}")
            
            return original_text, translated_text
            
        else:
            print("📝 No audio file provided or file not found")
            print("   Use: python test_malayalam.py <audio_file>")
            print("\n💡 Example usage:")
            print("   python test_malayalam.py malayalam_audio.wav")
            
            # Show sample Malayalam phrases for testing
            print("\n🌴 Sample Malayalam Phrases for Testing:")
            print("   • 'നമസ്കാരം' (Namaskaram - Hello)")
            print("   • 'എന്താണ് നിങ്ങളുടെ പേര്?' (What is your name?)")
            print("   • 'എനിക്ക് സഹായം വേണം' (I need help)")
            print("   • 'നന്ദി' (Thank you)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_languages():
    """Test transcription for multiple Indian languages."""
    
    print("🌍 Multi-Language Transcription Test")
    print("=" * 50)
    
    languages = [
        ("Malayalam", "ml"),
        ("Tamil", "ta"),
        ("Telugu", "te"),
        ("Hindi", "hi"),
        ("Bengali", "bn"),
        ("Gujarati", "gu"),
        ("Kannada", "kn"),
        ("Marathi", "mr")
    ]
    
    print("✅ Supported Indian Languages for Transcription:")
    for name, code in languages:
        print(f"   • {name} ({code})")
    
    print("\n📝 Usage Examples:")
    for name, code in languages:
        print(f"   # For {name}:")
        print(f"   tool = AIDubbingTool(input_language='{code}')")
        print(f"   original, translated = tool.transcribe_and_translate('{name.lower()}_audio.wav')")
        print()


def main():
    """Main function."""
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        test_malayalam_transcription(audio_file)
    else:
        test_malayalam_transcription()
        print("\n" + "="*50)
        test_multiple_languages()


if __name__ == "__main__":
    main() 