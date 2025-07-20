#!/usr/bin/env python3
"""
Status checker for AI Dubbing Tool
Helps users understand what's happening during processing.
"""

import time
import psutil
import os

def check_system_status():
    """Check system resources."""
    print("🖥️  System Status Check")
    print("=" * 50)
    
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent}%")
    
    # Memory usage
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
    
    # Disk usage
    disk = psutil.disk_usage('/')
    print(f"Disk Usage: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
    
    # Check for Python processes
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if 'python' in proc.info['name'].lower():
                python_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if python_processes:
        print(f"\n🐍 Python Processes: {len(python_processes)}")
        for proc in python_processes[:5]:  # Show top 5
            print(f"   PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, Mem: {proc['memory_percent']:.1f}%)")
    else:
        print("\n🐍 No Python processes found")

def check_output_files():
    """Check for output files."""
    print("\n📁 Output Files Check")
    print("=" * 50)
    
    output_dirs = ["output", "web_output", "test_output", "test_simple_output"]
    
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            if files:
                print(f"📂 {output_dir}/")
                for file in files:
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        mtime = time.ctime(os.path.getmtime(file_path))
                        print(f"   📄 {file} ({size} bytes, modified: {mtime})")
            else:
                print(f"📂 {output_dir}/ (empty)")
        else:
            print(f"📂 {output_dir}/ (not found)")

def check_model_files():
    """Check for model files."""
    print("\n🤖 Model Files Check")
    print("=" * 50)
    
    # Check Whisper models
    whisper_cache = os.path.expanduser("~/.cache/whisper")
    if os.path.exists(whisper_cache):
        whisper_models = os.listdir(whisper_cache)
        print(f"🔊 Whisper Models: {len(whisper_models)}")
        for model in whisper_models:
            print(f"   📄 {model}")
    else:
        print("🔊 Whisper Models: No cache directory found")
    
    # Check F5-TTS models
    f5_tts_cache = os.path.expanduser("~/.cache/huggingface/hub")
    if os.path.exists(f5_tts_cache):
        print("🎤 F5-TTS Models: Cache directory exists")
    else:
        print("🎤 F5-TTS Models: No cache directory found")

def provide_advice():
    """Provide advice based on current status."""
    print("\n💡 Advice")
    print("=" * 50)
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 80:
        print("⚠️  High CPU usage detected")
        print("   - F5-TTS inference is likely running")
        print("   - This is normal for voice cloning")
        print("   - Wait patiently for completion")
    else:
        print("✅ CPU usage is normal")
    
    # Check memory usage
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        print("⚠️  High memory usage detected")
        print("   - Consider closing other applications")
        print("   - Use smaller models if available")
    else:
        print("✅ Memory usage is normal")
    
    # General advice
    print("\n📋 General Tips:")
    print("   - F5-TTS inference can take 1-5 minutes per batch")
    print("   - Progress updates appear every 10 seconds")
    print("   - Use shorter audio files for faster testing")
    print("   - GPU acceleration significantly speeds up processing")

def main():
    """Main function."""
    print("🔍 AI Dubbing Tool Status Check")
    print("=" * 60)
    
    check_system_status()
    check_output_files()
    check_model_files()
    provide_advice()
    
    print("\n" + "=" * 60)
    print("✅ Status check completed")
    print("\nIf processing seems stuck:")
    print("1. Check if CPU usage is high (normal during F5-TTS inference)")
    print("2. Wait up to 5 minutes for completion")
    print("3. Use shorter audio files for testing")
    print("4. Check the web interface status output for details")

if __name__ == "__main__":
    main() 