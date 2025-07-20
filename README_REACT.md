# 🎤 AI Dubbing Tool - React UI

A modern, professional video editing interface for AI-powered video dubbing with voice cloning capabilities. This React.js application provides a sleek, intuitive interface similar to professional video editing software.

![AI Dubbing Tool React UI](https://img.shields.io/badge/React-18.2.0-blue) ![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue) ![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.3.2-blue)

## ✨ Features

### 🎬 Professional Video Editing Interface
- **Modern Dark Theme**: Sleek, professional dark interface
- **Video Player**: Full-featured video player with controls
- **Timeline**: Professional timeline with tracks for video, audio, and dubbed audio
- **Drag & Drop**: Easy file upload with drag and drop support
- **Real-time Preview**: Live video preview with playback controls

### 🎤 AI Dubbing Capabilities
- **Multi-language Support**: Support for 20+ languages including Hindi, Malayalam, Tamil, and more
- **Voice Cloning**: Advanced voice cloning with YourTTS
- **Smart Audio Extraction**: Automatic audio extraction from video files
- **Quality Settings**: Multiple quality modes for voice cloning
- **Progress Tracking**: Real-time progress updates during processing

### 🛠️ Advanced Settings
- **Whisper Models**: Choose from Tiny to Large models for transcription
- **Device Selection**: CPU, GPU (CUDA), or Apple Silicon (MPS) support
- **Reference Duration**: Adjustable reference audio duration for better voice cloning
- **Processing Options**: Segment-based processing for long videos

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (v16 or higher)
2. **Python** (3.8 or higher)
3. **npm** or **yarn**

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd hackathon
   ```

2. **Install Python dependencies**:
   ```bash
   pip install flask flask-cors
   ```

3. **Install React dependencies**:
   ```bash
   npm install
   ```

4. **Start the application**:
   ```bash
   python start_react_app.py
   ```

The application will automatically:
- Start the Flask API server on `http://localhost:5000`
- Start the React development server on `http://localhost:3000`
- Open your browser to the application

## 📁 Project Structure

```
hackathon/
├── src/                          # React source code
│   ├── components/               # React components
│   │   ├── Sidebar.js           # Navigation sidebar
│   │   ├── MediaPanel.js        # Media upload panel
│   │   ├── VideoPlayer.js       # Video player component
│   │   ├── Timeline.js          # Timeline component
│   │   └── SettingsPanel.js     # Settings and results panel
│   ├── hooks/                   # Custom React hooks
│   │   └── useDubbingTool.js    # Dubbing tool logic
│   ├── utils/                   # Utility functions
│   │   └── videoUtils.js        # Video processing utilities
│   ├── App.js                   # Main application component
│   └── index.css                # Global styles
├── api_server.py                # Flask API server
├── ai_dubbing_tool.py           # Core dubbing functionality
├── package.json                 # React dependencies
├── tailwind.config.js           # Tailwind CSS configuration
└── start_react_app.py           # Startup script
```

## 🎯 Usage Guide

### 1. Upload Video
- Drag and drop a video file onto the media panel
- Or click the upload button to select a file
- Supported formats: MP4, AVI, MOV, MKV, WebM

### 2. Configure Settings
- **Input Language**: Select the language of your video
- **Whisper Model**: Choose transcription quality vs speed
- **Device**: Select processing hardware (CPU/GPU)
- **Reference Duration**: Set audio duration for voice cloning
- **Voice Quality**: Choose quality mode for voice cloning

### 3. Process Dubbing
- The system will automatically:
  - Extract audio from the video
  - Transcribe and translate the speech
  - Generate English dubbed audio with cloned voice
  - Display results in the timeline

### 4. Review Results
- View original and translated text
- Play the generated dubbed audio
- Download the final audio file
- See all tracks in the timeline

## 🎨 Interface Components

### Header
- Project name and navigation
- Editing tools (cursor, hand, zoom)
- Export button and user controls

### Sidebar
- Media library
- Stock videos, photos, audio
- Text, captions, transcripts
- Stickers and effects

### Media Panel
- File upload area
- Uploaded media display
- Processing status and progress

### Video Player
- Full-featured video player
- Playback controls
- Volume and timeline scrubbing
- Fullscreen support

### Timeline
- Professional timeline interface
- Multiple tracks (video, audio, dubbed)
- Time markers and playhead
- Editing tools

### Settings Panel
- Dubbing configuration
- Language and model selection
- Results display
- Audio playback controls

## 🔧 Configuration

### Environment Variables
```bash
REACT_APP_API_URL=http://localhost:5000  # API server URL
```

### API Endpoints
- `GET /api/health` - Health check
- `POST /api/dub` - Process dubbing
- `GET /api/settings` - Get available settings
- `GET /api/download/<filename>` - Download files

## 🎤 Supported Languages

### Indian Languages
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

### International Languages
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

## 🚀 Advanced Features

### Voice Cloning Quality
- **Standard**: Faster processing, good quality
- **High Quality**: Better voice cloning (recommended)
- **Ultra Quality**: Best quality, slower processing

### Whisper Models
- **Tiny (39MB)**: Fastest, good quality
- **Base (74MB)**: Fast, better quality
- **Small (244MB)**: Medium speed, good quality
- **Medium (769MB)**: Slower, better quality
- **Large (1550MB)**: Slowest, best quality

### Processing Devices
- **Auto**: Automatically select best available
- **CPU**: Use CPU processing
- **CUDA**: Use NVIDIA GPU acceleration
- **MPS**: Use Apple Silicon GPU

## 🛠️ Development

### Running in Development Mode
```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Start React app
npm start
```

### Building for Production
```bash
npm run build
```

### Testing
```bash
npm test
```

## 🔍 Troubleshooting

### Common Issues

1. **Node.js not found**
   ```bash
   # Install Node.js from https://nodejs.org/
   ```

2. **Python dependencies missing**
   ```bash
   pip install flask flask-cors
   ```

3. **Port already in use**
   ```bash
   # Kill processes using ports 3000 or 5000
   lsof -ti:3000 | xargs kill -9
   lsof -ti:5000 | xargs kill -9
   ```

4. **CORS errors**
   - Ensure the API server is running on port 5000
   - Check that CORS is properly configured

### Performance Tips

1. **Use GPU acceleration** if available
2. **Choose appropriate Whisper model** based on your needs
3. **Process shorter videos** for faster results
4. **Use segment processing** for long videos

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** for speech recognition
- **YourTTS** for voice cloning
- **React** and **Tailwind CSS** for the UI framework
- **Flask** for the backend API

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**🎤 Transform your videos with AI-powered dubbing!** 