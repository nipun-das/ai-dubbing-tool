#!/usr/bin/env python3
"""
Windows-specific installation script for AI Dubbing Tool
Handles PyTorch installation issues on Windows.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_pytorch_windows():
    """Install PyTorch specifically for Windows."""
    print("\n🔥 Installing PyTorch for Windows...")
    
    # Try different PyTorch installation methods
    methods = [
        ("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu", "PyTorch CPU version"),
        ("pip install torch torchvision torchaudio", "PyTorch default version"),
        ("pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2", "PyTorch specific version"),
    ]
    
    for command, description in methods:
        print(f"\n🔄 Trying {description}...")
        if run_command(command, description):
            return True
        print(f"⚠️  {description} failed, trying next method...")
    
    return False


def install_other_requirements():
    """Install other requirements excluding PyTorch."""
    print("\n📦 Installing other requirements...")
    
    # Core packages that should work
    core_packages = [
        "numpy>=1.21.0",
        "pydub>=0.25.1", 
        "soundfile>=0.12.1",
        "librosa>=0.10.0",
        "tiktoken>=0.5.0",
        "numba>=0.58.0",
        "more-itertools>=8.14.0",
        "accelerate>=0.33.0",
        "bitsandbytes>0.37.0",
        "cached_path",
        "click",
        "datasets",
        "ema_pytorch>=0.5.2",
        "hydra-core>=1.3.0",
        "jieba",
        "matplotlib",
        "omegaconf",
        "pydantic<=2.10.6",
        "pypinyin",
        "safetensors",
        "tomli",
        "torchdiffeq",
        "tqdm>=4.65.0",
        "transformers",
        "transformers_stream_generator",
        "unidecode",
        "vocos",
        "wandb",
        "x_transformers>=1.31.14",
        "pathlib2>=2.3.7",
        "typing-extensions>=4.0.0",
        "psutil>=5.8.0",
        "gradio>=3.0.0"
    ]
    
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing...")
    
    return True


def install_whisper():
    """Install Whisper."""
    print("\n🔊 Installing Whisper...")
    
    whisper_path = Path("whisper")
    if not whisper_path.exists():
        print("❌ Whisper directory not found")
        return False
    
    # Change to whisper directory and install
    original_dir = os.getcwd()
    os.chdir(whisper_path)
    
    success = run_command("pip install -e .", "Installing Whisper")
    
    # Return to original directory
    os.chdir(original_dir)
    
    return success


def install_tts():
    """Install TTS (Coqui) for YourTTS."""
    print("\n🎤 Installing TTS (Coqui)...")
    
    success = run_command("pip install TTS", "Installing TTS (Coqui)")
    
    if success:
        print("✅ TTS (Coqui) installed successfully")
        return True
    else:
        print("❌ Failed to install TTS (Coqui)")
        return False


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = ["output", "web_output"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def test_imports():
    """Test if all required modules can be imported."""
    print("\n🧪 Testing imports...")
    
    try:
        # Test PyTorch import
        import torch
        print(f"✅ PyTorch imported successfully (version: {torch.__version__})")
        
        # Test Whisper import
        import whisper
        print("✅ Whisper imported successfully")
        
        # Test TTS import
        from TTS.api import TTS
        print("✅ TTS (Coqui) imported successfully")
        
        # Test main tool
        from ai_dubbing_tool import AIDubbingTool
        print("✅ AI Dubbing Tool imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main installation function."""
    print("🎤 AI Dubbing Tool Installation (Windows)")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    # Install PyTorch first
    if not install_pytorch_windows():
        print("❌ Failed to install PyTorch")
        sys.exit(1)
    
    # Install other requirements
    if not install_other_requirements():
        print("❌ Failed to install other requirements")
        sys.exit(1)
    
    # Install Whisper
    if not install_whisper():
        print("❌ Failed to install Whisper")
        sys.exit(1)
    
    # Install TTS (Coqui)
    if not install_tts():
        print("❌ Failed to install TTS (Coqui)")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_imports():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\n📖 Next steps:")
    print("1. Run the web interface: python web_interface.py")
    print("2. Or use command line: python ai_dubbing_tool.py <audio_file>")
    print("3. Check README.md for detailed usage instructions")
    
    print("\n⚠️  Note: First run will download AI models (may take several minutes)")


if __name__ == "__main__":
    main() 