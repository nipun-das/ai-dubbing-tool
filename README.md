# AI Dubbing Tool 🎭

Team Name : GenFusion
Members : Nipun Das
          Anandu M
Track : Entertainment


A powerful tool that converts audio from one language to another while maintaining the original speaker's voice using AI voice cloning technology.

## What This Tool Does ✨

- **Transcribes** audio from various languages (Hindi, Malayalam, Tamil, etc.)
- **Translates** the text to English
- **Clones** the original speaker's voice
- **Generates** new audio in English with the same voice
- **Allows editing** of individual sentences
- **Exports** the final dubbed audio

## Quick Start 🚀

### Prerequisites

Before you start, make sure you have:
- **Python 3.8 or higher** installed
- **Node.js 16 or higher** installed
- **Git** installed
- At least **8GB RAM** (16GB recommended)
- **Windows 10/11** (this guide is for Windows)

### Step 1: Download the Project

1. Open Command Prompt or PowerShell
2. Navigate to where you want to install the project:
   ```bash
   cd C:\Users\YourUsername\Desktop
   ```
3. Download the project:
   ```bash
   git clone https://github.com/your-username/ai-dubbing-tool.git
   cd ai-dubbing-tool
   ```

### Step 2: Install Python Dependencies

1. Open Command Prompt in the project folder
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```
4. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Install Frontend Dependencies

1. In the same Command Prompt, install Node.js packages:
   ```bash
   npm install
   ```

### Step 4: Start the Application

1. **Start the Backend Server** (in one Command Prompt):
   ```bash
   # Make sure virtual environment is activated
   venv\Scripts\activate
   python api_server.py
   ```
   You should see: "Server running on http://localhost:5000"

2. **Start the Frontend** (in another Command Prompt):
   ```bash
   npm start
   ```
   You should see: "Local: http://localhost:3000"

3. **Open your browser** and go to: `http://localhost:3000`

## How to Use the Tool 📖

### 1. Upload Audio
- Click "Upload" button
- Select an audio file (WAV, MP3, M4A)
- Wait for processing (this may take a few minutes)

### 2. Review and Edit
- The tool will show you the original text and English translation
- You can edit individual sentences by clicking on them
- Use the "Refine Dialogue" button to improve translations

### 3. Export
- Click "Export" to generate the final dubbed audio
- The audio will be downloaded automatically

## Troubleshooting 🔧

### Common Issues and Solutions

**Problem: "Module not found" errors**
- Solution: Make sure you activated the virtual environment:
  ```bash
  venv\Scripts\activate
  ```

**Problem: "Port already in use"**
- Solution: Close other applications using ports 3000 or 5000
- Or use different ports:
  ```bash
  # For backend
  python api_server.py --port 5001
  
  # For frontend
  npm start -- --port 3001
  ```

**Problem: "CUDA out of memory"**
- Solution: Use CPU instead of GPU:
  ```bash
  set FORCE_CPU=true
  python api_server.py
  ```

**Problem: "Audio not playing"**
- Solution: 
  1. Check if both servers are running
  2. Refresh the browser page
  3. Check browser console for errors

**Problem: "Voice cloning not working"**
- Solution:
  1. Make sure your audio file is clear and has good quality
  2. Try with a shorter audio file first
  3. Check that the reference audio is being extracted properly

### Performance Tips

- **For better speed**: Use a computer with a good GPU
- **For better quality**: Use high-quality audio files
- **For stability**: Close other applications while processing

## File Structure 📁

```
ai-dubbing-tool/
├── src/                    # Frontend React code
│   ├── components/        # UI components
│   ├── hooks/            # Custom React hooks
│   └── utils/            # Utility functions
├── api_server.py         # Backend server
├── ai_dubbing_tool.py    # Main AI processing
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
└── README.md            # This file
```

## Supported Languages 🌍

**Input Languages:**
- Hindi (hi)
- Malayalam (ml)
- Tamil (ta)
- Telugu (te)
- Bengali (bn)
- Gujarati (gu)
- Kannada (kn)
- Marathi (mr)
- Punjabi (pa)
- Urdu (ur)
- And many more!

**Output Language:**
- English (en)

## Technical Details 🔬

### Backend Technologies
- **Python 3.8+**
- **Flask** - Web server
- **Whisper** - Speech recognition and translation
- **YourTTS** - Voice cloning
- **PyDub** - Audio processing

### Frontend Technologies
- **React 18**
- **Node.js**
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations

### AI Models Used
- **Whisper** - For transcription and translation
- **YourTTS** - For voice cloning and synthesis

## Advanced Configuration ⚙️

### Changing Input Language
Edit `ai_dubbing_tool.py` and change the `input_language` parameter:
```python
dubbing_tool = AIDubbingTool(input_language="ml")  # For Malayalam
```

### Using Different Whisper Models
```python
dubbing_tool = AIDubbingTool(whisper_model_name="large")  # Better quality, slower
```

### Force CPU Usage
```bash
set FORCE_CPU=true
python api_server.py
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License 📄

This project is licensed under the MIT License.

## Support 💬

If you encounter any issues:
1. Check the troubleshooting section above
2. Look at the console logs for error messages
3. Create an issue on GitHub with detailed information

## Credits 🙏

- **OpenAI Whisper** - For speech recognition and translation
- **Coqui YourTTS** - For voice cloning technology
- **React Team** - For the frontend framework
- **Python Community** - For various libraries and tools

---

**Happy Dubbing! 🎤✨** 
