#!/usr/bin/env python3
"""
Check Gradio version and compatibility
"""

import gradio as gr

def check_gradio_version():
    """Check Gradio version and compatibility."""
    print("🌐 Gradio Version Check")
    print("=" * 50)
    
    version = gr.__version__
    print(f"Gradio version: {version}")
    
    # Parse version
    major, minor, patch = map(int, version.split('.')[:3])
    
    print(f"Major: {major}, Minor: {minor}, Patch: {patch}")
    
    # Check compatibility
    if major >= 4:
        print("✅ Using Gradio 4.x - Modern features available")
        print("   - source parameter supported")
        print("   - Enhanced audio components")
    elif major >= 3:
        print("✅ Using Gradio 3.x - Good compatibility")
        print("   - source parameter not available")
        print("   - Basic audio components work")
    else:
        print("⚠️  Using older Gradio version")
        print("   - Some features may not work")
        print("   - Consider upgrading: pip install --upgrade gradio")
    
    # Test audio component creation
    print("\n🧪 Testing audio component creation...")
    
    try:
        # Try with source parameter (Gradio 4.x)
        try:
            audio_v4 = gr.Audio(
                label="Test Audio",
                type="filepath",
                format="wav",
                source="upload"
            )
            print("✅ Audio component with 'source' parameter works (Gradio 4.x)")
            supports_source = True
        except TypeError:
            print("⚠️  Audio component with 'source' parameter not supported")
            supports_source = False
        
        # Try without source parameter (Gradio 3.x)
        audio_v3 = gr.Audio(
            label="Test Audio",
            type="filepath",
            format="wav"
        )
        print("✅ Audio component without 'source' parameter works")
        
        return supports_source
        
    except Exception as e:
        print(f"❌ Audio component test failed: {e}")
        return False

def get_recommended_gradio_version():
    """Get recommended Gradio version."""
    print("\n📋 Recommendations:")
    print("For best compatibility with this AI dubbing tool:")
    print("   - Gradio 3.x (minimum): pip install 'gradio>=3.0.0'")
    print("   - Gradio 4.x (recommended): pip install 'gradio>=4.0.0'")
    print("   - Latest version: pip install --upgrade gradio")

def main():
    """Main function."""
    supports_source = check_gradio_version()
    get_recommended_gradio_version()
    
    if supports_source:
        print("\n🎉 Your Gradio version supports all features!")
    else:
        print("\n⚠️  Some features may be limited with your Gradio version")
        print("   The web interface will still work, but with basic audio upload")

if __name__ == "__main__":
    main() 