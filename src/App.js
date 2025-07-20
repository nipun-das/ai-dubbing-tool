import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, 
  Smartphone, 
  Camera, 
  Cloud, 
  Grid3X3, 
  Image, 
  Music, 
  Type, 
  MessageSquare, 
  FileText, 
  Star, 
  FolderOpen,
  Play,
  Pause,
  Volume2,
  Settings,
  Download,
  HelpCircle,
  Square,
  MoreHorizontal,
  User
} from 'lucide-react';
import Sidebar from './components/Sidebar';
import MediaPanel from './components/MediaPanel';
import AudioEditor from './components/AudioEditor';
import SentenceTimeline from './components/SentenceTimeline';
import SettingsPanel from './components/SettingsPanel';
import { useDubbingTool } from './hooks/useDubbingTool';

function App() {
  const [activeTab, setActiveTab] = useState('media');
  const [uploadedAudio, setUploadedAudio] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [selectedSentence, setSelectedSentence] = useState(null);
  
  const {
    settings,
    updateSettings,
    processDubbing,
    originalText,
    translatedText,
    outputAudio,
    sentences,
    referenceAudioPath,
    status,
    updateSentence,
    resetResults
  } = useDubbingTool();

  const videoRef = useRef(null);
  const timelineRef = useRef(null);
  const audioEditorRef = useRef(null);

  const handleAudioUpload = (file) => {
    setUploadedAudio(file);
    // Reset any previous processing results using the hook's reset function
    resetResults();
  };

  const handleProcessAudio = async () => {
    if (!uploadedAudio) return;
    
    try {
      setIsProcessing(true);
      setProgress(10);
      
      // Process audio with dubbing tool
      const result = await processDubbing(uploadedAudio, settings);
      setProgress(100);
      
      console.log('Dubbing completed:', result);
    } catch (error) {
      console.error('Error processing audio:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimelineClick = (e) => {
    if (timelineRef.current && duration > 0) {
      const rect = timelineRef.current.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const percentage = clickX / rect.width;
      const newTime = percentage * duration;
      setCurrentTime(newTime);
      
      if (videoRef.current) {
        videoRef.current.currentTime = newTime;
      }
    }
  };

  const handleSentenceUpdate = (sentenceId, updates) => {
    console.log('🔄 Updating sentence:', sentenceId, updates);
    
    // Update sentence data using the hook's updateSentence function
    updateSentence(sentenceId, updates);
    
    // Log the update for debugging
    console.log('✅ Sentence updated successfully:', sentenceId);
    console.log('📝 Updated text:', updates.translatedText);
    console.log('🎵 Audio URL:', updates.audioUrl);
  };

  const handleSentenceReorder = (newOrder) => {
    // Handle sentence reordering
    console.log('Sentences reordered:', newOrder);
  };

  const handleSentenceDelete = (sentenceId) => {
    // Handle sentence deletion
    console.log('Sentence deleted:', sentenceId);
  };

  const handleSentenceSplit = (sentenceId) => {
    // Handle sentence splitting
    console.log('Sentence split:', sentenceId);
  };

  const handleSentenceMerge = (sentenceIds) => {
    // Handle sentence merging
    console.log('Sentences merged:', sentenceIds);
  };

  const handleSave = (updatedSentences) => {
    // Save the edited sentences
    console.log('Saving edited sentences:', updatedSentences);
    // In a real app, you'd send this to the backend
  };

  const handleExport = async (sentences) => {
    try {
      console.log('Exporting final audio with sentences:', sentences);
      
      // Call the export API
      const response = await fetch('http://localhost:5000/api/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sentences: sentences,
          reference_audio_path: referenceAudioPath || 'reference_audio.wav'
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log('Export successful:', result.message);
        console.log('Exported file:', result.output_filename);
        
        // Download the exported file
        const downloadUrl = `http://localhost:5000/api/download/${result.output_filename}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = result.output_filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Store the exported filename for later use
        localStorage.setItem('lastExportedFile', result.output_filename);
        
        // Load the exported audio in the main player
        console.log('🎵 Loading exported audio in main player...');
        console.log('🔍 AudioEditor ref:', audioEditorRef.current);
        console.log('🔍 loadExportedAudio function:', audioEditorRef.current?.loadExportedAudio);
        
        if (audioEditorRef.current && audioEditorRef.current.loadExportedAudio) {
          console.log('📞 Calling loadExportedAudio with filename:', result.output_filename);
          const loadSuccess = await audioEditorRef.current.loadExportedAudio(result.output_filename);
          console.log('📦 Load result:', loadSuccess);
        } else {
          console.log('❌ AudioEditor ref or loadExportedAudio function not available');
        }
        
      } else {
        console.error('Export failed:', result.error);
      }
    } catch (error) {
      console.error('Error exporting audio:', error);
    }
  };

  const handleRefinementComplete = () => {
    console.log('🎵 Refinement complete, complete audio should be loaded in player');
    // Force load the complete audio in the AudioEditor
    if (audioEditorRef.current && audioEditorRef.current.forceLoadCompleteAudio) {
      audioEditorRef.current.forceLoadCompleteAudio();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-screen bg-dark-950 text-white flex flex-col">
      {/* Header */}
      <header className="bg-dark-900 border-b border-dark-700 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 cursor-pointer">
            <span className="text-sm text-dark-400">Untitled project</span>
            <svg className="w-4 h-4 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-dark-700 rounded">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.122 2.122" />
              </svg>
            </button>
            <button className="p-2 hover:bg-dark-700 rounded">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
              </svg>
            </button>
            <span className="text-sm">{zoom}% v</span>
            <button className="p-2 hover:bg-dark-700 rounded">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
              </svg>
            </button>
            <button className="p-2 hover:bg-dark-700 rounded">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="btn-primary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button className="p-2 hover:bg-dark-700 rounded">
            <HelpCircle className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded">
            <Square className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded">
            <MoreHorizontal className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded">
            <User className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        
        {/* Left Panel - Media/Project */}
        <div className="w-80 bg-dark-900 border-r border-dark-700 flex flex-col">
          <div className="p-4 border-b border-dark-700">
            <h2 className="text-lg font-semibold mb-4">Project</h2>
            <div className="flex gap-2">
              <button className="btn-secondary flex items-center gap-2 flex-1">
                <Upload className="w-4 h-4" />
                Upload
              </button>
              <button className="btn-secondary p-2">
                <Smartphone className="w-4 h-4" />
              </button>
              <button className="btn-secondary p-2">
                <Camera className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <div className="flex-1 p-4">
            <MediaPanel 
              onAudioUpload={handleAudioUpload}
              uploadedAudio={uploadedAudio}
              onProcessAudio={handleProcessAudio}
              isProcessing={isProcessing}
              progress={progress}
            />
          </div>
        </div>
        
        {/* Center Panel - Audio Editor */}
        <div className="flex-1 bg-dark-800 flex flex-col">
          <AudioEditor
            ref={audioEditorRef}
            originalAudio={uploadedAudio}
            processedAudio={outputAudio}
            sentences={sentences}
            onSentenceUpdate={handleSentenceUpdate}
            onSentenceDelete={handleSentenceDelete}
            onSentenceSplit={handleSentenceSplit}
            onSentenceMerge={handleSentenceMerge}
            onSave={handleSave}
            onExport={handleExport}
            onRefinementComplete={handleRefinementComplete}
          />
        </div>
        
        {/* Right Panel - Settings */}
        <div className="w-80 bg-dark-900 border-l border-dark-700">
          <SettingsPanel
            settings={settings}
            onSettingsChange={updateSettings}
            originalText={originalText}
            translatedText={translatedText}
            outputAudio={outputAudio}
            status={status}
          />
        </div>
      </div>

      {/* Timeline */}
      <SentenceTimeline
        ref={timelineRef}
        currentTime={currentTime}
        duration={duration}
        onTimelineClick={handleTimelineClick}
        originalAudio={uploadedAudio}
        originalAudioPath={outputAudio ? 'generated_speech.wav' : null} // Add original audio path
        sentences={sentences}
        onSentenceUpdate={handleSentenceUpdate}
        onSentenceReorder={handleSentenceReorder}
        onSentenceDelete={handleSentenceDelete}
        onSentenceSplit={handleSentenceSplit}
        onSentenceMerge={handleSentenceMerge}
        zoom={zoom}
        onZoomChange={setZoom}
        onRefinementComplete={handleRefinementComplete}
      />
    </div>
  );
}

export default App; 