#!/usr/bin/env python3
"""
Web Interface for AI Dubbing Tool
A Gradio-based web interface for the AI dubbing tool.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Optional, Tuple

import gradio as gr
import yaml

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from ai_dubbing_tool import AIDubbingTool


class DubbingWebInterface:
    def __init__(self, config_path: str = "dubbing_config.yaml"):
        """Initialize the web interface."""
        self.config = self.load_config(config_path)
        self.dubbing_tool = None
        self.is_initialized = False
        
        # Language options for the interface
        self.language_options = [
            ("Hindi", "hi"),
            ("Malayalam", "ml"),
            ("Tamil", "ta"),
            ("Telugu", "te"),
            ("Bengali", "bn"),
            ("Gujarati", "gu"),
            ("Kannada", "kn"),
            ("Marathi", "mr"),
            ("Punjabi", "pa"),
            ("Urdu", "ur"),
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
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found, using defaults")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def initialize_models(self, whisper_model: str, yourtts_model: str, device: str, input_language: str) -> str:
        """Initialize the dubbing tool with specified models."""
        try:
            self.dubbing_tool = AIDubbingTool(
                whisper_model_name=whisper_model,
                yourtts_model_name=yourtts_model,
                device=device,
                output_dir="web_output",
                input_language=input_language
            )
            
            self.dubbing_tool.load_models()
            self.is_initialized = True
            
            return "✅ Models initialized successfully!"
            
        except Exception as e:
            error_msg = f"❌ Error initializing models: {str(e)}"
            print(error_msg)
            print("\n🔧 Troubleshooting:")
            print("1. Make sure all dependencies are installed: python install.py")
            print("2. Check if YourTTS and Whisper are properly installed")
            print("3. Try running: python test_yourtts.py")
            traceback.print_exc()
            return error_msg
    
    def process_audio(
        self,
        audio_file,
        whisper_model: str,
        yourtts_model: str,
        device: str,
        input_language: str,
        use_segments: bool,
        reference_duration: float,
        voice_quality_mode: str,
        progress=gr.Progress()
    ) -> Tuple[str, str, str, str]:
        """
        Process audio file for dubbing.
        
        Returns:
            Tuple of (status_message, original_text, translated_text, output_audio_path)
        """
        try:
            # Initialize models if not already done
            if not self.is_initialized or self.dubbing_tool is None:
                status = self.initialize_models(whisper_model, yourtts_model, device, input_language)
                if "❌" in status:
                    return status, "", "", None
            
            if audio_file is None:
                return "❌ Please upload an audio file", "", "", None
            
            progress(0.1, desc="Loading audio file...")
            
            # Handle audio file input
            temp_dir = Path("web_output")
            temp_dir.mkdir(exist_ok=True)
            
            if audio_file is None:
                return "❌ Please upload an audio file", "", None
            
            # If audio_file is already a path (string), use it directly
            if isinstance(audio_file, str):
                input_path = audio_file
                print(f"Using audio file path: {input_path}")
            else:
                # If it's a file object, save it
                input_path = temp_dir / "input_audio.wav"
                print(f"Saving uploaded file to: {input_path}")
                with open(input_path, "wb") as f:
                    f.write(audio_file.read())
            
            # Verify the input file exists
            if not os.path.exists(input_path):
                return f"❌ Audio file not found: {input_path}", "", "", None
            
            progress(0.2, desc="Transcribing and translating...")
            
            # Transcribe and translate
            original_text, translated_text, transcription_info = self.dubbing_tool.transcribe_and_translate(str(input_path))
            
            progress(0.4, desc="Extracting reference audio...")
            
            # Extract reference audio
            reference_audio_path = self.dubbing_tool.extract_reference_audio(
                str(input_path), 
                duration=reference_duration
            )
            
            progress(0.6, desc="Generating speech with voice cloning...")
            
            # Generate speech
            output_path = self.dubbing_tool.generate_speech_with_voice_cloning(
                translated_text,
                reference_audio_path
            )
            
            progress(0.9, desc="Finalizing...")
            
            # Read the output file for Gradio
            with open(output_path, "rb") as f:
                output_audio = f.read()
            
            progress(1.0, desc="Complete!")
            
            status_msg = f"✅ Dubbing completed successfully!\n\n📝 Original text: {original_text}\n\n📝 Translated text: {translated_text}\n\n📁 Output saved to: {output_path}"
            
            return status_msg, original_text, translated_text, output_audio
            
        except Exception as e:
            error_msg = f"❌ Error during processing: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return error_msg, "", "", None
    
    def create_interface(self):
        """Create the Gradio interface."""
        with gr.Blocks(
            title="AI Dubbing Tool",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
                margin: auto !important;
            }
            """
        ) as interface:
            
            gr.Markdown("""
            # 🎤 AI Dubbing Tool
            
            Convert audio from various languages to English while maintaining the same speaker's voice using AI voice cloning.
            
            **How it works:**
            1. Upload an audio file in your chosen language
            2. The tool transcribes and translates it to English
            3. Uses voice cloning to generate English speech with the same voice
            4. Downloads the final dubbed audio
            
            **Supported formats:** WAV, MP3, M4A, FLAC
            **Supported languages:** Hindi, Malayalam, Tamil, Telugu, Bengali, Gujarati, Kannada, Marathi, Punjabi, Urdu, and many more!
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ Settings")
                    
                    input_language = gr.Dropdown(
                        choices=[(name, code) for name, code in self.language_options],
                        value=self.config.get("processing", {}).get("input_language", "hi"),
                        label="Input Language",
                        info="Language of the audio file you're uploading"
                    )
                    
                    whisper_model = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large"],
                        value=self.config.get("models", {}).get("whisper", {}).get("model_name", "base"),
                        label="Whisper Model Size",
                        info="Larger models are more accurate but slower"
                    )
                    
                    yourtts_model = gr.Dropdown(
                        choices=["tts_models/multilingual/multi-dataset/your_tts"],
                        value="tts_models/multilingual/multi-dataset/your_tts",
                        label="YourTTS Model",
                        info="Voice cloning model"
                    )
                    
                    device = gr.Dropdown(
                        choices=["auto", "cpu", "cuda", "mps"],
                        value=self.config.get("processing", {}).get("device", "auto"),
                        label="Device",
                        info="Hardware to run inference on"
                    )
                    
                    use_segments = gr.Checkbox(
                        value=self.config.get("processing", {}).get("use_segments", True),
                        label="Process in Segments",
                        info="Recommended for long audio files"
                    )
                    
                    reference_duration = gr.Slider(
                        minimum=5.0,
                        maximum=30.0,
                        value=self.config.get("audio", {}).get("reference_duration", 15.0),
                        step=1.0,
                        label="Reference Audio Duration (seconds)",
                        info="Duration of audio to use for voice cloning (longer = better quality)"
                    )
                    
                    voice_quality_mode = gr.Dropdown(
                        choices=[
                            ("Standard", "standard"),
                            ("High Quality", "high_quality"),
                            ("Ultra Quality", "ultra_quality")
                        ],
                        value="high_quality",
                        label="Voice Cloning Quality",
                        info="Higher quality = slower but better voice cloning"
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("### 🎵 Audio Processing")
                    
                    audio_input = gr.Audio(
                        label="Upload Audio File",
                        type="filepath",
                        format="wav"
                    )
                    
                    process_btn = gr.Button(
                        "🎬 Start Dubbing",
                        variant="primary",
                        size="lg"
                    )
                    
                    status_output = gr.Textbox(
                        label="Status",
                        lines=5,
                        interactive=False
                    )
                    
                    original_text_output = gr.Textbox(
                        label="Original Text",
                        lines=3,
                        interactive=False
                    )
                    
                    translated_text_output = gr.Textbox(
                        label="Translated Text (English)",
                        lines=3,
                        interactive=False
                    )
                    
                    audio_output = gr.Audio(
                        label="Dubbed Audio (English)",
                        type="filepath",
                        format="wav"
                    )
            
            # Event handlers
            process_btn.click(
                fn=self.process_audio,
                inputs=[
                    audio_input,
                    whisper_model,
                    yourtts_model,
                    device,
                    input_language,
                    use_segments,
                    reference_duration,
                    voice_quality_mode
                ],
                outputs=[
                    status_output,
                    original_text_output,
                    translated_text_output,
                    audio_output
                ]
            )
            
            gr.Markdown("""
            ### 📋 Instructions
            
            1. **Upload Audio**: Select a Hindi audio file (WAV, MP3, M4A, FLAC)
            2. **Configure Settings**: Adjust model sizes and processing options
            3. **Start Processing**: Click "Start Dubbing" to begin
            4. **Download Result**: The dubbed English audio will appear below
            
            ### ⚠️ Notes
            
            - First run will download the required AI models (may take a few minutes)
            - Processing time depends on audio length and model size
            - **YourTTS inference can take 1-5 minutes per batch on CPU**
            - For best results, use clear Hindi speech with minimal background noise
            - GPU acceleration (CUDA) is recommended for faster processing
            
            ### 🔧 Troubleshooting
            
            - If you encounter memory issues, try using a smaller Whisper model
            - For very long audio files, ensure "Process in Segments" is enabled
            - **If processing seems stuck, wait up to 5 minutes for YourTTS inference**
            - Use shorter audio files (30 seconds or less) for faster testing
            - Check the status output for detailed error messages
            
            ### ⚡ Performance Tips
            
            - Use "tiny" Whisper model for faster transcription
            - Use "cpu" device if you have GPU memory issues
            - Keep reference duration short (5-10 seconds)
            - Process short audio files first to test the system
            """)
        
        return interface


def main():
    """Run the web interface."""
    print("🎤 Starting AI Dubbing Tool Web Interface...")
    print("=" * 50)
    
    try:
        # Create web interface
        web_interface = DubbingWebInterface()
        interface = web_interface.create_interface()
        
        print("✅ Web interface created successfully")
        print("🌐 Launching web server...")
        
        # Launch the interface
        interface.launch(
            server_name="127.0.0.1",  # Use localhost instead of 0.0.0.0
            server_port=7860,
            share=False,
            debug=True,
            show_error=True,
            quiet=False  # Show startup messages
        )
        
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure port 7860 is not already in use")
        print("2. Try running: python web_interface.py")
        print("3. Check if all dependencies are installed")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 