#!/usr/bin/env python3
"""
Installation script for AI Dubbing Tool
Automates the setup process for the dubbing tool.
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


def check_gpu():
    """Check for GPU availability."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA GPU detected: {gpu_name} (Count: {gpu_count})")
            return True
        else:
            print("⚠️  No CUDA GPU detected. Processing will be slower on CPU.")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed yet. GPU check will be done after installation.")
        return False


def install_requirements():
    """Install Python requirements."""
    print("\n📦 Installing Python requirements...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install PyTorch separately first (for Windows compatibility)
    print("\n🔥 Installing PyTorch...")
    if platform.system() == "Windows":
        # Use PyTorch's recommended installation for Windows
        torch_command = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
        if not run_command(torch_command, "Installing PyTorch (CPU version)"):
            print("⚠️  PyTorch CPU installation failed, trying alternative...")
            # Alternative: try without index-url
            if not run_command("pip install torch torchvision torchaudio", "Installing PyTorch (alternative method)"):
                return False
    else:
        # For non-Windows systems
        if not run_command("pip install torch torchvision torchaudio", "Installing PyTorch"):
            return False
    
    # Install other requirements (excluding torch since we installed it separately)
    print("\n📦 Installing other requirements...")
    
    # Read requirements and filter out torch-related packages
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    
    # Filter out torch-related lines
    filtered_requirements = []
    for line in requirements:
        line = line.strip()
        if line and not line.startswith("#") and not any(torch_pkg in line.lower() for torch_pkg in ["torch", "torchaudio"]):
            filtered_requirements.append(line)
    
    # Create temporary requirements file
    temp_req_file = "temp_requirements.txt"
    with open(temp_req_file, "w") as f:
        f.write("\n".join(filtered_requirements))
    
    # Install filtered requirements
    success = run_command(f"pip install -r {temp_req_file}", "Installing other requirements")
    
    # Clean up
    try:
        os.remove(temp_req_file)
    except:
        pass
    
    return success


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
    print("🎤 AI Dubbing Tool Installation")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    check_gpu()
    
    # Install dependencies
    if not install_requirements():
        print("❌ Failed to install requirements")
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