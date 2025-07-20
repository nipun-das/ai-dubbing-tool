#!/usr/bin/env python3
"""
Test script for AI Dubbing Tool
Verifies that all components are properly installed and working.
"""

import os
import sys
import traceback
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    tests = [
        ("Whisper", "whisper"),
        ("PyTorch", "torch"),
        ("NumPy", "numpy"),
        ("SoundFile", "soundfile"),
        ("PyDub", "pydub"),
        ("Gradio", "gradio"),
        ("YAML", "yaml"),
    ]
    
    failed_imports = []
    
    for module_name, import_name in tests:
        try:
            __import__(import_name)
            print(f"✅ {module_name} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            failed_imports.append(module_name)
    
    # Test F5-TTS imports
    try:
        sys.path.insert(0, str(Path("F5-TTS/src")))
        from f5_tts.infer.utils_infer import device
        print("✅ F5-TTS imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import F5-TTS: {e}")
        failed_imports.append("F5-TTS")
    
    # Test main tool import
    try:
        from ai_dubbing_tool import AIDubbingTool
        print("✅ AI Dubbing Tool imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI Dubbing Tool: {e}")
        failed_imports.append("AI Dubbing Tool")
    
    return len(failed_imports) == 0, failed_imports


def test_gpu():
    """Test GPU availability."""
    print("\n🖥️  Testing GPU availability...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA GPU detected: {gpu_name} (Count: {gpu_count})")
            
            # Test GPU memory
            try:
                memory_info = torch.cuda.get_device_properties(0)
                total_memory = memory_info.total_memory / (1024**3)  # Convert to GB
                print(f"✅ GPU Memory: {total_memory:.1f} GB")
            except Exception as e:
                print(f"⚠️  Could not get GPU memory info: {e}")
            
            return True
        else:
            print("⚠️  No CUDA GPU detected. Processing will be slower on CPU.")
            return False
            
    except ImportError:
        print("❌ PyTorch not installed")
        return False


def test_audio_processing():
    """Test audio processing capabilities."""
    print("\n🎵 Testing audio processing...")
    
    try:
        from pydub import AudioSegment
        from pydub.silence import split_on_silence
        
        # Create a simple test audio
        test_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
        
        # Test basic operations
        test_audio.export("test_audio.wav", format="wav")
        print("✅ Audio creation and export successful")
        
        # Test silence detection
        segments = split_on_silence(test_audio, min_silence_len=500)
        print(f"✅ Silence detection successful (found {len(segments)} segments)")
        
        # Clean up
        if os.path.exists("test_audio.wav"):
            os.remove("test_audio.wav")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processing test failed: {e}")
        return False


def test_whisper_loading():
    """Test Whisper model loading."""
    print("\n🔊 Testing Whisper model loading...")
    
    try:
        import whisper
        
        # Try to load a small model
        model = whisper.load_model("tiny")
        print("✅ Whisper tiny model loaded successfully")
        
        # Test basic functionality
        if hasattr(model, 'transcribe'):
            print("✅ Whisper transcribe method available")
        else:
            print("❌ Whisper transcribe method not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        traceback.print_exc()
        return False


def test_f5_tts_loading():
    """Test F5-TTS model loading."""
    print("\n🎤 Testing F5-TTS model loading...")
    
    try:
        sys.path.insert(0, str(Path("F5-TTS/src")))
        
        from f5_tts.infer.utils_infer import load_model, load_vocoder
        
        # Test if functions are available
        if callable(load_model):
            print("✅ F5-TTS load_model function available")
        else:
            print("❌ F5-TTS load_model function not found")
        
        if callable(load_vocoder):
            print("✅ F5-TTS load_vocoder function available")
        else:
            print("❌ F5-TTS load_vocoder function not found")
        
        return True
        
    except Exception as e:
        print(f"❌ F5-TTS test failed: {e}")
        traceback.print_exc()
        return False


def test_directories():
    """Test if required directories exist."""
    print("\n📁 Testing directory structure...")
    
    required_dirs = ["F5-TTS", "whisper"]
    optional_dirs = ["output", "web_output"]
    
    missing_required = []
    missing_optional = []
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ Required directory found: {directory}")
        else:
            print(f"❌ Required directory missing: {directory}")
            missing_required.append(directory)
    
    for directory in optional_dirs:
        if Path(directory).exists():
            print(f"✅ Optional directory found: {directory}")
        else:
            print(f"⚠️  Optional directory missing: {directory}")
            missing_optional.append(directory)
    
    return len(missing_required) == 0, missing_required, missing_optional


def test_config_files():
    """Test if configuration files exist."""
    print("\n⚙️  Testing configuration files...")
    
    config_files = ["requirements.txt", "dubbing_config.yaml"]
    missing_files = []
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ Configuration file found: {config_file}")
        else:
            print(f"⚠️  Configuration file missing: {config_file}")
            missing_files.append(config_file)
    
    return len(missing_files) == 0, missing_files


def test_dubbing_tool_initialization():
    """Test if the dubbing tool can be initialized."""
    print("\n🎬 Testing dubbing tool initialization...")
    
    try:
        from ai_dubbing_tool import AIDubbingTool
        
        # Try to create an instance
        dubbing_tool = AIDubbingTool(
            whisper_model_name="tiny",  # Use tiny model for testing
            f5_tts_model="F5TTS_v1_Base",
            device="cpu",  # Use CPU for testing
            output_dir="test_output"
        )
        
        print("✅ Dubbing tool initialized successfully")
        
        # Test device detection
        device = dubbing_tool._get_device("auto")
        print(f"✅ Device detection: {device}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dubbing tool initialization failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🧪 AI Dubbing Tool Installation Test")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Module Imports", test_imports),
        ("GPU Availability", test_gpu),
        ("Audio Processing", test_audio_processing),
        ("Whisper Loading", test_whisper_loading),
        ("F5-TTS Loading", test_f5_tts_loading),
        ("Directory Structure", test_directories),
        ("Configuration Files", test_config_files),
        ("Dubbing Tool Initialization", test_dubbing_tool_initialization),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if test_name == "Module Imports":
                success, failed_imports = test_func()
                results[test_name] = (success, failed_imports)
            elif test_name == "Directory Structure":
                success, missing_required, missing_optional = test_func()
                results[test_name] = (success, missing_required, missing_optional)
            elif test_name == "Configuration Files":
                success, missing_files = test_func()
                results[test_name] = (success, missing_files)
            else:
                success = test_func()
                results[test_name] = success
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        if isinstance(result, tuple):
            success = result[0]
            details = result[1:]
        else:
            success = result
            details = []
        
        if success:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            if details:
                print(f"   Details: {details}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is complete and working.")
        print("\n📖 Next steps:")
        print("1. Run the web interface: python web_interface.py")
        print("2. Or use command line: python ai_dubbing_tool.py <audio_file>")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Run the installation script: python install.py")
        print("2. Check the README.md for troubleshooting guide")
        print("3. Ensure all dependencies are properly installed")


if __name__ == "__main__":
    main() 