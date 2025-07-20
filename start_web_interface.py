#!/usr/bin/env python3
"""
Startup script for AI Dubbing Tool Web Interface
Provides better feedback and multiple access options.
"""

import os
import sys
import socket
import subprocess
import time
from pathlib import Path

def check_port_available(port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False

def get_local_ip():
    """Get the local IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def main():
    """Start the web interface with better feedback."""
    print("🎤 AI Dubbing Tool Web Interface")
    print("=" * 50)
    
    # Check if required files exist
    if not Path("web_interface.py").exists():
        print("❌ web_interface.py not found!")
        print("Please run this script from the project root directory.")
        return
    
    # Check if dependencies are installed
    try:
        import gradio as gr
        print("✅ Gradio is installed")
    except ImportError:
        print("❌ Gradio not installed. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "gradio"], check=True)
            print("✅ Gradio installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Gradio")
            return
    
    # Check port availability
    port = 7860
    if not check_port_available(port):
        print(f"⚠️  Port {port} is already in use")
        print("Trying alternative port...")
        
        # Try alternative ports
        for alt_port in [7861, 7862, 7863, 7864, 7865]:
            if check_port_available(alt_port):
                port = alt_port
                print(f"✅ Using alternative port: {port}")
                break
        else:
            print("❌ No available ports found. Please close other applications using ports 7860-7865")
            return
    
    # Get local IP
    local_ip = get_local_ip()
    
    print(f"🌐 Starting web interface on port {port}...")
    print(f"📱 Access URLs:")
    print(f"   Local: http://localhost:{port}")
    print(f"   Network: http://{local_ip}:{port}")
    print()
    
    # Start the web interface
    try:
        # Set environment variable for the port
        os.environ["GRADIO_SERVER_PORT"] = str(port)
        
        # Import and run the web interface
        from web_interface import main as run_web_interface
        
        print("🚀 Launching web interface...")
        print("⏳ Please wait for the interface to load...")
        print()
        
        # Run the web interface
        run_web_interface()
        
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting web interface: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all dependencies are installed: python install.py")
        print("2. Check if the port is available")
        print("3. Try running: python web_interface.py directly")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 