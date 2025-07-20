#!/usr/bin/env python3
"""
Troubleshooting script for AI Dubbing Tool
Helps diagnose and fix common issues.
"""

import os
import sys
import subprocess
import socket
import platform
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    dependencies = [
        ("gradio", "Gradio"),
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
        ("soundfile", "SoundFile"),
        ("pydub", "PyDub"),
        ("yaml", "PyYAML"),
    ]
    
    missing = []
    
    for package, name in dependencies:
        try:
            __import__(package)
            print(f"✅ {name} is installed")
        except ImportError:
            print(f"❌ {name} is missing")
            missing.append(package)
    
    return missing

def check_ports():
    """Check if required ports are available."""
    print("\n🌐 Checking port availability...")
    
    ports = [7860, 7861, 7862, 7863, 7864, 7865]
    available_ports = []
    
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                available_ports.append(port)
                print(f"✅ Port {port} is available")
        except OSError:
            print(f"❌ Port {port} is in use")
    
    return available_ports

def check_files():
    """Check if required files exist."""
    print("\n📁 Checking required files...")
    
    required_files = [
        "web_interface.py",
        "ai_dubbing_tool.py",
        "requirements.txt",
        "dubbing_config.yaml"
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            missing_files.append(file)
    
    return missing_files

def check_directories():
    """Check if required directories exist."""
    print("\n📂 Checking directories...")
    
    required_dirs = ["F5-TTS", "whisper"]
    optional_dirs = ["output", "web_output"]
    
    missing_required = []
    missing_optional = []
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory} directory exists")
        else:
            print(f"❌ {directory} directory is missing")
            missing_required.append(directory)
    
    for directory in optional_dirs:
        if Path(directory).exists():
            print(f"✅ {directory} directory exists")
        else:
            print(f"⚠️  {directory} directory is missing (will be created)")
            missing_optional.append(directory)
    
    return missing_required, missing_optional

def check_gpu():
    """Check GPU availability."""
    print("\n🖥️  Checking GPU...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA GPU detected: {gpu_name} (Count: {gpu_count})")
            
            # Check GPU memory
            try:
                memory_info = torch.cuda.get_device_properties(0)
                total_memory = memory_info.total_memory / (1024**3)
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

def install_missing_dependencies(missing):
    """Install missing dependencies."""
    if not missing:
        return True
    
    print(f"\n📦 Installing missing dependencies: {', '.join(missing)}")
    
    for package in missing:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_missing_directories(missing_optional):
    """Create missing optional directories."""
    for directory in missing_optional:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")

def test_web_interface():
    """Test if the web interface can be imported."""
    print("\n🧪 Testing web interface...")
    
    try:
        from web_interface import DubbingWebInterface
        print("✅ Web interface can be imported")
        
        # Try to create an instance
        web_interface = DubbingWebInterface()
        print("✅ Web interface can be instantiated")
        
        return True
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def main():
    """Run all troubleshooting checks."""
    print("🔧 AI Dubbing Tool Troubleshooting")
    print("=" * 50)
    
    # Run all checks
    python_ok = check_python_version()
    missing_deps = check_dependencies()
    available_ports = check_ports()
    missing_files = check_files()
    missing_required_dirs, missing_optional_dirs = check_directories()
    gpu_available = check_gpu()
    web_interface_ok = test_web_interface()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Troubleshooting Summary")
    print("=" * 50)
    
    issues = []
    
    if not python_ok:
        issues.append("Python version incompatible")
    
    if missing_deps:
        issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
    
    if not available_ports:
        issues.append("No available ports (7860-7865)")
    
    if missing_files:
        issues.append(f"Missing files: {', '.join(missing_files)}")
    
    if missing_required_dirs:
        issues.append(f"Missing required directories: {', '.join(missing_required_dirs)}")
    
    if not web_interface_ok:
        issues.append("Web interface import failed")
    
    # Fix issues
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        
        print("\n🔧 Attempting to fix issues...")
        
        # Install missing dependencies
        if missing_deps:
            if install_missing_dependencies(missing_deps):
                print("✅ Dependencies installed successfully")
            else:
                print("❌ Failed to install some dependencies")
        
        # Create missing directories
        if missing_optional_dirs:
            create_missing_directories(missing_optional_dirs)
        
        # Re-test web interface
        if missing_deps:
            print("\n🧪 Re-testing web interface...")
            web_interface_ok = test_web_interface()
        
    else:
        print("✅ No issues found!")
    
    # Final recommendations
    print("\n📖 Recommendations:")
    
    if not gpu_available:
        print("⚠️  No GPU detected - processing will be slower")
        print("   Consider installing CUDA for faster processing")
    
    if available_ports:
        print(f"✅ Available ports: {', '.join(map(str, available_ports))}")
        print(f"   Use port {available_ports[0]} for the web interface")
    
    if web_interface_ok:
        print("✅ Web interface is ready to use")
        print("\n🚀 To start the web interface:")
        print("   python start_web_interface.py")
        print("   or")
        print("   python web_interface.py")
    else:
        print("❌ Web interface has issues")
        print("   Try running: python install.py")
    
    print("\n📚 For more help, check README.md")

if __name__ == "__main__":
    main() 