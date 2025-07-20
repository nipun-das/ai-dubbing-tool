#!/usr/bin/env python3
"""
Test script for multi-language AI dubbing functionality
Demonstrates how to use the tool with different input languages.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_dubbing_tool import AIDubbingTool


def test_multilingual_dubbing():
    """Test dubbing with different languages."""
    
    print("🌍 Multi-Language AI Dubbing Tool Test")
    print("=" * 50)
    
    # Test languages
    test_languages = [
        ("Hindi", "hi"),
        ("Malayalam", "ml"),
        ("Tamil", "ta"),
        ("Telugu", "te"),
        ("Bengali", "bn"),
        ("Gujarati", "gu"),
        ("Kannada", "kn"),
        ("Marathi", "mr"),
        ("Punjabi", "pa"),
        ("Urdu", "ur")
    ]
    
    print("✅ Supported Indian Languages:")
    for name, code in test_languages:
        print(f"   • {name} ({code})")
    
    print("\n📝 Usage Examples:")
    print("1. For Malayalam audio:")
    print("   dubbing_tool = AIDubbingTool(input_language='ml')")
    print("   dubbing_tool.dub_audio('malayalam_audio.wav')")
    
    print("\n2. For Tamil audio:")
    print("   dubbing_tool = AIDubbingTool(input_language='ta')")
    print("   dubbing_tool.dub_audio('tamil_audio.wav')")
    
    print("\n3. For Telugu audio:")
    print("   dubbing_tool = AIDubbingTool(input_language='te')")
    print("   dubbing_tool.dub_audio('telugu_audio.wav')")
    
    print("\n🌐 Other Supported Languages:")
    other_languages = [
        ("English", "en"),
        ("Spanish", "es"),
        ("French", "fr"),
        ("German", "de"),
        ("Italian", "it"),
        ("Portuguese", "pt"),
        ("Russian", "ru"),
        ("Japanese", "ja"),
        ("Korean", "ko"),
        ("Chinese", "zh")
    ]
    
    for name, code in other_languages:
        print(f"   • {name} ({code})")
    
    print("\n🎯 How to use:")
    print("1. Initialize the tool with your desired input language:")
    print("   tool = AIDubbingTool(input_language='ml')  # for Malayalam")
    print("   tool.load_models()")
    
    print("\n2. Process your audio file:")
    print("   output_path = tool.dub_audio('your_audio.wav')")
    
    print("\n3. Or use the web interface:")
    print("   python start_web_interface.py")
    print("   Then select your input language from the dropdown!")
    
    print("\n⚠️  Notes:")
    print("- All languages are translated to English")
    print("- Voice cloning works with any language")
    print("- Whisper supports 99+ languages")
    print("- YourTTS can clone voices from any language")


def test_specific_language(language_code: str, audio_file: str = None):
    """Test dubbing with a specific language."""
    
    language_names = {
        "hi": "Hindi", "ml": "Malayalam", "ta": "Tamil", "te": "Telugu",
        "bn": "Bengali", "gu": "Gujarati", "kn": "Kannada", "mr": "Marathi",
        "pa": "Punjabi", "ur": "Urdu"
    }
    
    language_name = language_names.get(language_code, language_code)
    
    print(f"🧪 Testing {language_name} dubbing...")
    print("=" * 40)
    
    try:
        # Initialize tool with specific language
        tool = AIDubbingTool(
            whisper_model_name="base",
            input_language=language_code,
            output_dir="test_output"
        )
        
        print(f"✅ Initialized for {language_name}")
        
        # Load models
        tool.load_models()
        print("✅ Models loaded successfully")
        
        if audio_file and os.path.exists(audio_file):
            print(f"🎵 Processing audio file: {audio_file}")
            output_path = tool.dub_audio(audio_file)
            print(f"✅ Output saved to: {output_path}")
        else:
            print("📝 No audio file provided or file not found")
            print("   Use: python test_multilingual.py <language_code> <audio_file>")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function."""
    if len(sys.argv) > 1:
        language_code = sys.argv[1]
        audio_file = sys.argv[2] if len(sys.argv) > 2 else None
        test_specific_language(language_code, audio_file)
    else:
        test_multilingual_dubbing()


if __name__ == "__main__":
    main() 