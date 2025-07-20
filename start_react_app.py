#!/usr/bin/env python3
"""
Startup script for AI Dubbing Tool with React UI
Launches both the API server and React development server.
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

# Global variable to store the working npm command
npm_command = 'npm'

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check if Node.js is installed
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js first.")
        return False
    
    # Check if npm is installed with better error handling
    npm_found = False
    npm_version = None
    
    # Try multiple ways to find npm
    npm_commands = ['npm', 'npm.cmd', 'npm.exe']
    
    for npm_cmd in npm_commands:
        try:
            result = subprocess.run([npm_cmd, '--version'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                print(f"✅ npm: {npm_version}")
                npm_found = True
                # Store the working npm command
                global npm_command
                npm_command = npm_cmd
                break
        except FileNotFoundError:
            continue
    
    if not npm_found:
        # Try with full path on Windows
        if os.name == 'nt':  # Windows
            possible_paths = [
                os.path.join(os.environ.get('APPDATA', ''), 'npm', 'npm.cmd'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs', 'npm.cmd'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'nodejs', 'npm.cmd'),
            ]
            
            for npm_path in possible_paths:
                if os.path.exists(npm_path):
                    try:
                        result = subprocess.run([npm_path, '--version'], capture_output=True, text=True)
                        if result.returncode == 0:
                            npm_version = result.stdout.strip()
                            print(f"✅ npm: {npm_version} (found at {npm_path})")
                            npm_found = True
                            npm_command = npm_path
                            break
                    except:
                        continue
    
    # Check if yarn is available as alternative
    if not npm_found:
        try:
            result = subprocess.run(['yarn', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Yarn: {result.stdout.strip()} (will use instead of npm)")
                npm_found = True
                npm_command = 'yarn'
            else:
                print("❌ Yarn not found")
        except FileNotFoundError:
            print("❌ Yarn not found")
    
    if not npm_found:
        print("\n💡 Solutions:")
        print("1. Check if npm is in your PATH environment variable")
        print("2. Try running: npm --version in your terminal")
        print("3. Reinstall Node.js from https://nodejs.org/")
        print("4. Install Yarn: npm install -g yarn")
        return False
    
    # Check if Python dependencies are installed
    try:
        import flask
        import flask_cors
        print("✅ Python dependencies: Flask and Flask-CORS")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install flask flask-cors")
        return False
    
    return True
    
    # Check if Python dependencies are installed
    try:
        import flask
        import flask_cors
        print("✅ Python dependencies: Flask and Flask-CORS")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install flask flask-cors")
        return False
    
    return True

def install_react_dependencies():
    """Install React dependencies if needed."""
    print("📦 Installing React dependencies...")
    
    # Use the npm command that was found in check_dependencies
    global npm_command
    
    if not os.path.exists('node_modules'):
        print(f"Installing packages with {npm_command}...")
        
        try:
            if npm_command == 'yarn':
                result = subprocess.run(['yarn', 'install'], capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run([npm_command, 'install'], capture_output=True, text=True, shell=True)
                
            if result.returncode != 0:
                print(f"❌ Failed to install packages: {result.stderr}")
                return False
            print("✅ React dependencies installed")
        except Exception as e:
            print(f"❌ Error installing packages: {e}")
            return False
    else:
        print("✅ React dependencies already installed")
    
    return True

def start_api_server():
    """Start the Flask API server."""
    print("🚀 Starting API server...")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Start the API server
    try:
        subprocess.run([sys.executable, 'api_server.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ API server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("🛑 API server stopped")
        return True

def start_react_app():
    """Start the React development server."""
    print("🚀 Starting React development server...")
    
    # Use the npm command that was found in check_dependencies
    global npm_command
    
    try:
        if npm_command == 'yarn':
            subprocess.run(['yarn', 'start'], check=True, shell=True)
        else:
            subprocess.run([npm_command, 'start'], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ React app failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("🛑 React app stopped")
        return True

def main():
    """Main startup function."""
    print("🎤 AI Dubbing Tool - React UI Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Install React dependencies
    if not install_react_dependencies():
        print("\n❌ Failed to install React dependencies.")
        sys.exit(1)
    
    print("\n✅ All dependencies ready!")
    print("\n🚀 Starting servers...")
    print("   • API Server: http://localhost:5000")
    print("   • React App: http://localhost:3000")
    print("\n⏳ Starting servers in 3 seconds...")
    time.sleep(3)
    
    # Start API server in a separate thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    # Wait a bit for API server to start
    time.sleep(2)
    
    # Open browser
    try:
        webbrowser.open('http://localhost:3000')
    except:
        pass
    
    # Start React app in main thread
    try:
        start_react_app()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 