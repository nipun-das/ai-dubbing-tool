import React, { useState } from 'react';
import { 
  Settings, 
  Globe, 
  Mic, 
  Cpu, 
  Clock, 
  Download,
  Play,
  Pause,
  Volume2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';

const SettingsPanel = ({ 
  settings, 
  onSettingsChange, 
  originalText, 
  translatedText, 
  outputAudio, 
  status 
}) => {
  const [activeSection, setActiveSection] = useState('settings');
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const languageOptions = [
    { value: 'hi', label: 'Hindi' },
    { value: 'ml', label: 'Malayalam' },
    { value: 'ta', label: 'Tamil' },
    { value: 'te', label: 'Telugu' },
    { value: 'bn', label: 'Bengali' },
    { value: 'gu', label: 'Gujarati' },
    { value: 'kn', label: 'Kannada' },
    { value: 'mr', label: 'Marathi' },
    { value: 'pa', label: 'Punjabi' },
    { value: 'ur', label: 'Urdu' },
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'ru', label: 'Russian' },
    { value: 'ja', label: 'Japanese' },
    { value: 'ko', label: 'Korean' },
    { value: 'zh', label: 'Chinese' }
  ];

  const whisperModels = [
    { value: 'tiny', label: 'Tiny (39MB)', description: 'Fastest, good quality' },
    { value: 'base', label: 'Base (74MB)', description: 'Fast, better quality' },
    { value: 'small', label: 'Small (244MB)', description: 'Medium speed, good quality' },
    { value: 'medium', label: 'Medium (769MB)', description: 'Slower, better quality' },
    { value: 'large', label: 'Large (1550MB)', description: 'Slowest, best quality' }
  ];

  const qualityModes = [
    { value: 'standard', label: 'Standard', description: 'Faster processing' },
    { value: 'high_quality', label: 'High Quality', description: 'Better voice cloning' },
    { value: 'ultra_quality', label: 'Ultra Quality', description: 'Best quality, slower' }
  ];

  const handleSettingChange = (key, value) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  const playOutputAudio = () => {
    if (outputAudio) {
      const audio = new Audio(URL.createObjectURL(outputAudio));
      audio.play();
      setIsPlayingAudio(true);
      audio.onended = () => setIsPlayingAudio(false);
    }
  };

  const downloadOutputAudio = () => {
    if (outputAudio) {
      const url = URL.createObjectURL(outputAudio);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'dubbed_audio.wav';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Panel Header */}
      <div className="p-4 border-b border-dark-700">
        <div className="flex items-center gap-2 mb-4">
          <Settings className="w-5 h-5 text-primary-500" />
          <h2 className="text-lg font-semibold">Dubbing Settings</h2>
        </div>
        
        {/* Section Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveSection('settings')}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              activeSection === 'settings' 
                ? 'bg-primary-600 text-white' 
                : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
            }`}
          >
            Settings
          </button>
          <button
            onClick={() => setActiveSection('results')}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              activeSection === 'results' 
                ? 'bg-primary-600 text-white' 
                : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
            }`}
          >
            Results
          </button>
        </div>
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeSection === 'settings' ? (
          <div className="space-y-6">
            {/* Language Settings */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <Globe className="w-4 h-4 text-primary-500" />
                <h3 className="font-medium">Input Language</h3>
              </div>
              <select
                value={settings.inputLanguage || 'hi'}
                onChange={(e) => handleSettingChange('inputLanguage', e.target.value)}
                className="input-field w-full"
              >
                {languageOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-dark-400 mt-1">
                Select the language of your video
              </p>
            </div>

            {/* Whisper Model */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <Mic className="w-4 h-4 text-primary-500" />
                <h3 className="font-medium">Whisper Model</h3>
              </div>
              <select
                value={settings.whisperModel || 'base'}
                onChange={(e) => handleSettingChange('whisperModel', e.target.value)}
                className="input-field w-full"
              >
                {whisperModels.map((model) => (
                  <option key={model.value} value={model.value}>
                    {model.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-dark-400 mt-1">
                {whisperModels.find(m => m.value === settings.whisperModel)?.description}
              </p>
            </div>

            {/* Device Settings */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <Cpu className="w-4 h-4 text-primary-500" />
                <h3 className="font-medium">Processing Device</h3>
              </div>
              <select
                value={settings.device || 'auto'}
                onChange={(e) => handleSettingChange('device', e.target.value)}
                className="input-field w-full"
              >
                <option value="auto">Auto (Recommended)</option>
                <option value="cpu">CPU</option>
                <option value="cuda">CUDA (GPU)</option>
                <option value="mps">MPS (Apple Silicon)</option>
              </select>
              <p className="text-xs text-dark-400 mt-1">
                Choose hardware for processing
              </p>
            </div>

            {/* Reference Duration */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4 text-primary-500" />
                <h3 className="font-medium">Reference Audio Duration</h3>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min="5"
                  max="30"
                  step="1"
                  value={settings.referenceDuration || 15}
                  onChange={(e) => handleSettingChange('referenceDuration', parseFloat(e.target.value))}
                  className="flex-1"
                />
                <span className="text-sm font-medium w-12">
                  {settings.referenceDuration || 15}s
                </span>
              </div>
              <p className="text-xs text-dark-400 mt-1">
                Duration of audio used for voice cloning (longer = better quality)
              </p>
            </div>

            {/* Voice Quality Mode */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <Volume2 className="w-4 h-4 text-primary-500" />
                <h3 className="font-medium">Voice Cloning Quality</h3>
              </div>
              <select
                value={settings.voiceQualityMode || 'high_quality'}
                onChange={(e) => handleSettingChange('voiceQualityMode', e.target.value)}
                className="input-field w-full"
              >
                {qualityModes.map((mode) => (
                  <option key={mode.value} value={mode.value}>
                    {mode.label}
                  </option>
                ))}
              </select>
              <p className="text-xs text-dark-400 mt-1">
                {qualityModes.find(m => m.value === settings.voiceQualityMode)?.description}
              </p>
            </div>

            {/* Processing Options */}
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <Settings className="w-4 h-4 text-primary-500" />
                <h3 className="font-medium">Processing Options</h3>
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.useSegments !== false}
                  onChange={(e) => handleSettingChange('useSegments', e.target.checked)}
                  className="rounded border-dark-600 bg-dark-700 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm">Process in segments (recommended for long videos)</span>
              </label>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Status */}
            {status && (
              <div className="card">
                <div className="flex items-center gap-2 mb-3">
                  {status.includes('✅') ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                  )}
                  <h3 className="font-medium">Status</h3>
                </div>
                <p className="text-sm text-dark-300">{status}</p>
              </div>
            )}

            {/* Original Text */}
            {originalText && (
              <div className="card">
                <h3 className="font-medium mb-3">Original Text</h3>
                <div className="bg-dark-700 rounded p-3">
                  <p className="text-sm text-dark-300 leading-relaxed">
                    {originalText}
                  </p>
                </div>
              </div>
            )}

            {/* Translated Text */}
            {translatedText && (
              <div className="card">
                <h3 className="font-medium mb-3">Translated Text (English)</h3>
                <div className="bg-dark-700 rounded p-3">
                  <p className="text-sm text-white leading-relaxed">
                    {translatedText}
                  </p>
                </div>
              </div>
            )}

            {/* Output Audio */}
            {outputAudio && (
              <div className="card">
                <h3 className="font-medium mb-3">Dubbed Audio</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={playOutputAudio}
                      disabled={isPlayingAudio}
                      className="btn-secondary flex items-center gap-2"
                    >
                      {isPlayingAudio ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                      {isPlayingAudio ? 'Playing...' : 'Play Audio'}
                    </button>
                    <button
                      onClick={downloadOutputAudio}
                      className="btn-primary flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </div>
                  <p className="text-xs text-dark-400">
                    English dubbed audio with cloned voice
                  </p>
                </div>
              </div>
            )}

            {!originalText && !translatedText && !outputAudio && (
              <div className="text-center py-8">
                <div className="w-12 h-12 bg-dark-700 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Settings className="w-6 h-6 text-dark-400" />
                </div>
                <p className="text-dark-400">No results yet</p>
                <p className="text-sm text-dark-500">Process a video to see results here</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPanel; 