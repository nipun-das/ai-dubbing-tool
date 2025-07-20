import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Download,
  Save,
  RotateCcw,
  Settings,
  Mic,
  Edit3,
  Trash2,
  Copy,
  Scissors
} from 'lucide-react';
import { motion } from 'framer-motion';

const AudioEditor = forwardRef(({ 
  originalAudio, 
  processedAudio,
  sentences, 
  onSentenceUpdate, 
  onSentenceDelete,
  onSentenceSplit,
  onSentenceMerge,
  onSave,
  onExport,
  onRefinementComplete
}, ref) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [selectedSentence, setSelectedSentence] = useState(null);
  const [playbackMode, setPlaybackMode] = useState('original'); // 'original', 'dubbed', 'mixed'
  const [isDragging, setIsDragging] = useState(false);
  const [currentAudioType, setCurrentAudioType] = useState('original'); // 'original', 'individual', 'modified'
  
  const audioRef = useRef(null);
  const audioContextRef = useRef(null);
  const audioBufferRef = useRef(null);
  const sourceNodeRef = useRef(null);
  const startTimeRef = useRef(0);
  const animationFrameRef = useRef(null);
  const progressBarRef = useRef(null);

  // Expose functions to parent component
  useImperativeHandle(ref, () => ({
    forceLoadCompleteAudio,
    loadExportedAudio
  }));

  // Initialize audio context for real-time playback
  useEffect(() => {
    if (typeof window !== 'undefined' && window.AudioContext) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    return () => {
      // Stop any active audio sources
      if (sourceNodeRef.current) {
        sourceNodeRef.current.stop();
        sourceNodeRef.current = null;
      }
      
      // Cancel any animation frames
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      // Close audio context
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Load audio buffer when audio changes
  useEffect(() => {
    const audioToLoad = processedAudio || originalAudio;
    if (audioToLoad && audioContextRef.current) {
      loadAudioBuffer(audioToLoad);
    }
  }, [originalAudio, processedAudio]);

  // Load audio from URL when sentences have audio URLs - DISABLED AUTO-LOADING
  useEffect(() => {
    if (sentences && sentences.length > 0 && audioContextRef.current) {
      console.log('🔄 Sentences changed, checking for audio URLs...');
      console.log('📋 Sentences:', sentences.map(s => ({
        id: s.id,
        hasAudioUrl: !!s.audioUrl,
        hasModifiedAudioUrl: !!s.modifiedAudioUrl,
        audioUrl: s.audioUrl,
        modifiedAudioUrl: s.modifiedAudioUrl,
        isRefined: s.isRefined
      })));
      
      // DISABLED: Auto-loading audio to prevent simultaneous playback
      console.log('🚫 Auto-loading disabled to prevent simultaneous audio playback');
      console.log('💡 Use manual buttons to load specific audio types');
      
      // Only load original audio if no other audio is loaded
      if (!audioBufferRef.current) {
        console.log('🎵 Loading original audio as fallback...');
        // Load original audio if available
        const sentenceWithAudio = sentences.find(s => s.audioUrl);
        if (sentenceWithAudio && sentenceWithAudio.audioUrl) {
          const cacheBustedUrl = `${sentenceWithAudio.audioUrl}?t=${Date.now()}`;
          loadAudioFromUrl(cacheBustedUrl, 'original');
        }
      }
    }
  }, [sentences]);

  // Separate useEffect for auto-loading complete audio after refinement - DISABLED
  useEffect(() => {
    if (sentences && sentences.length > 0 && audioContextRef.current) {
      // Check if any sentence has been refined and has modified audio
      const hasRefinedSentences = sentences.some(s => s.isRefined && s.modifiedAudioUrl);
      const hasCompleteAudio = sentences.some(s => s.modifiedAudioUrl);
      
      console.log('🔄 Checking for auto-loading complete audio...');
      console.log('Has refined sentences with modified audio:', hasRefinedSentences);
      console.log('Has complete audio available:', hasCompleteAudio);
      console.log('Current audio type:', currentAudioType);
      
      // DISABLED: Auto-loading to prevent simultaneous playback
      if (hasRefinedSentences && hasCompleteAudio) {
        console.log('🚫 Auto-loading complete audio disabled to prevent simultaneous playback');
        console.log('💡 Use "Load Complete" button to manually load complete audio');
      }
    }
  }, [sentences, currentAudioType]);

  // Callback when refinement is complete
  useEffect(() => {
    if (sentences && sentences.length > 0) {
      const hasRefinedSentences = sentences.some(s => s.isRefined && s.modifiedAudioUrl);
      if (hasRefinedSentences && onRefinementComplete) {
        console.log('🔄 Refinement complete, notifying parent component...');
        onRefinementComplete();
      }
    }
  }, [sentences, onRefinementComplete]);

  const loadAudioBuffer = async (audioFile) => {
    try {
      const arrayBuffer = await audioFile.arrayBuffer();
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      audioBufferRef.current = audioBuffer;
      setDuration(audioBuffer.duration);
      console.log('Audio buffer loaded:', audioBuffer.duration, 'seconds');
      
      // Reset playback to start
      setCurrentTime(0);
    } catch (error) {
      console.error('Error loading audio buffer:', error);
    }
  };

  const loadAudioFromUrl = async (audioUrl, audioType = 'original') => {
    try {
      console.log(`🎵 Loading ${audioType} audio from URL:`, audioUrl);
      console.log(`🔗 Full URL: ${window.location.origin}${audioUrl}`);
      
      // Stop any existing playback before loading new audio
      if (isPlaying) {
        pauseAudio();
      }
      
      // Ensure no other audio sources are active
      if (sourceNodeRef.current) {
        sourceNodeRef.current.stop();
        sourceNodeRef.current = null;
      }
      
      const response = await fetch(audioUrl);
      console.log(`📡 Response status: ${response.status}`);
      console.log(`📡 Response headers:`, Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const arrayBuffer = await response.arrayBuffer();
      console.log(`📦 Audio data size: ${arrayBuffer.byteLength} bytes`);
      
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      audioBufferRef.current = audioBuffer;
      setDuration(audioBuffer.duration);
      setCurrentAudioType(audioType);
      console.log(`✅ ${audioType} audio loaded:`, audioBuffer.duration, 'seconds');
      console.log(`🎵 Audio buffer:`, audioBuffer);
      
      // Reset playback to start
      setCurrentTime(0);
    } catch (error) {
      console.error(`❌ Error loading ${audioType} audio from URL:`, error);
      console.error(`❌ Error details:`, error.message);
    }
  };

  const playAudio = () => {
    if (!audioContextRef.current || !audioBufferRef.current) return;

    // Stop any existing playback first
    if (sourceNodeRef.current) {
      sourceNodeRef.current.stop();
      sourceNodeRef.current = null;
    }

    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }

    const source = audioContextRef.current.createBufferSource();
    source.buffer = audioBufferRef.current;
    
    const gainNode = audioContextRef.current.createGain();
    gainNode.gain.value = isMuted ? 0 : volume;
    
    source.connect(gainNode);
    gainNode.connect(audioContextRef.current.destination);
    
    sourceNodeRef.current = source;
    startTimeRef.current = audioContextRef.current.currentTime - currentTime;
    
    source.start(0, currentTime);
    source.onended = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };
    
    setIsPlaying(true);
    updatePlaybackTime();
  };

  const pauseAudio = () => {
    if (sourceNodeRef.current) {
      sourceNodeRef.current.stop();
      sourceNodeRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    setIsPlaying(false);
  };

  const updatePlaybackTime = () => {
    if (isPlaying && audioContextRef.current) {
      const newTime = audioContextRef.current.currentTime - startTimeRef.current;
      setCurrentTime(Math.max(0, newTime));
      
      if (newTime >= duration) {
        setIsPlaying(false);
        setCurrentTime(0);
      } else {
        animationFrameRef.current = requestAnimationFrame(updatePlaybackTime);
      }
    }
  };

  const handleSeek = (e) => {
    if (!duration) return;
    
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, clickX / rect.width));
    const newTime = percentage * duration;
    
    console.log('Seeking to:', newTime, 'seconds (', percentage * 100, '%)');
    setCurrentTime(newTime);
    
    // If playing, restart playback from new position
    if (isPlaying) {
      pauseAudio();
      setTimeout(() => {
        playAudio();
      }, 50);
    }
  };

  const handleMouseDown = (e) => {
    if (!duration) return;
    setIsDragging(true);
    handleSeek(e);
  };

  const handleMouseMove = (e) => {
    if (!isDragging || !duration) return;
    handleSeek(e);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Add global mouse event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      const handleGlobalMouseMove = (e) => {
        if (progressBarRef.current) {
          const rect = progressBarRef.current.getBoundingClientRect();
          const clickX = e.clientX - rect.left;
          const percentage = Math.max(0, Math.min(1, clickX / rect.width));
          const newTime = percentage * duration;
          setCurrentTime(newTime);
        }
      };

      const handleGlobalMouseUp = () => {
        setIsDragging(false);
      };

      document.addEventListener('mousemove', handleGlobalMouseMove);
      document.addEventListener('mouseup', handleGlobalMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleGlobalMouseMove);
        document.removeEventListener('mouseup', handleGlobalMouseUp);
      };
    }
  }, [isDragging, duration]);

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSentenceAtTime = (time) => {
    return sentences.find(sentence => 
      time >= sentence.startTime && time <= sentence.startTime + sentence.duration
    );
  };

  const currentSentence = getSentenceAtTime(currentTime);

  const handleSentenceEdit = (sentenceId, field, value) => {
    onSentenceUpdate(sentenceId, { [field]: value });
  };

  const handleSentenceDelete = (sentenceId) => {
    onSentenceDelete(sentenceId);
    setSelectedSentence(null);
  };

  const handleSentenceSplit = (sentenceId) => {
    onSentenceSplit(sentenceId);
  };

  const handleSave = () => {
    onSave(sentences);
  };

  const playSentenceAudio = async (sentence) => {
    if (sentence.audioUrl) {
      try {
        console.log('Playing sentence audio:', sentence.audioUrl);
        const response = await fetch(sentence.audioUrl);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
        
        // Create a new audio source for this sentence
        const source = audioContextRef.current.createBufferSource();
        source.buffer = audioBuffer;
        
        const gainNode = audioContextRef.current.createGain();
        gainNode.gain.value = isMuted ? 0 : volume;
        
        source.connect(gainNode);
        gainNode.connect(audioContextRef.current.destination);
        
        source.start(0);
        source.onended = () => {
          console.log('Sentence audio finished playing');
        };
        
        console.log('Playing refined sentence audio');
      } catch (error) {
        console.error('Error playing sentence audio:', error);
      }
    }
  };

  const playModifiedFullAudio = async (sentence) => {
    if (sentence.modifiedAudioUrl) {
      try {
        console.log('🎵 Playing modified full audio:', sentence.modifiedAudioUrl);
        // Add cache-busting parameter to prevent 304 responses
        const cacheBustedUrl = `${sentence.modifiedAudioUrl}?t=${Date.now()}`;
        await loadAudioFromUrl(cacheBustedUrl, 'modified');
        
        // Play the modified full audio
        playAudio();
        
        console.log('✅ Playing modified full audio with all sentences');
      } catch (error) {
        console.error('❌ Error playing modified full audio:', error);
      }
    }
  };

  const loadModifiedFullAudio = async () => {
    // Find any sentence with modified audio
    const sentenceWithModified = sentences.find(s => s.modifiedAudioUrl);
    if (sentenceWithModified && sentenceWithModified.modifiedAudioUrl) {
      try {
        console.log('🔄 Manually loading modified full audio...');
        // Add cache-busting parameter to prevent 304 responses
        const cacheBustedUrl = `${sentenceWithModified.modifiedAudioUrl}?t=${Date.now()}`;
        await loadAudioFromUrl(cacheBustedUrl, 'modified');
        console.log('✅ Modified full audio loaded successfully');
      } catch (error) {
        console.error('❌ Error loading modified full audio:', error);
      }
    } else {
      console.log('❌ No modified full audio found in sentences');
    }
  };

  const debugAudioUrls = () => {
    console.log('🔍 Debug: Available audio URLs in sentences:');
    sentences.forEach((sentence, index) => {
      console.log(`  ${index + 1}. ${sentence.id}:`);
      console.log(`     Individual: ${sentence.audioUrl || 'None'}`);
      console.log(`     Modified: ${sentence.modifiedAudioUrl || 'None'}`);
    });
    console.log(`Current audio type: ${currentAudioType}`);
    console.log(`Current duration: ${duration}s`);
    
    // Test URL accessibility
    sentences.forEach((sentence, index) => {
      if (sentence.modifiedAudioUrl) {
        console.log(`🔗 Testing modified audio URL for ${sentence.id}:`);
        fetch(sentence.modifiedAudioUrl)
          .then(response => {
            console.log(`  ✅ Modified audio accessible: ${response.status} ${response.statusText}`);
            console.log(`  📦 Content-Length: ${response.headers.get('content-length')} bytes`);
          })
          .catch(error => {
            console.log(`  ❌ Modified audio not accessible: ${error.message}`);
          });
      }
      if (sentence.audioUrl) {
        console.log(`🔗 Testing individual audio URL for ${sentence.id}:`);
        fetch(sentence.audioUrl)
          .then(response => {
            console.log(`  ✅ Individual audio accessible: ${response.status} ${response.statusText}`);
            console.log(`  📦 Content-Length: ${response.headers.get('content-length')} bytes`);
          })
          .catch(error => {
            console.log(`  ❌ Individual audio not accessible: ${error.message}`);
          });
      }
    });
  };

  const handleExport = () => {
    onExport(sentences);
  };

  const testModifiedAudio = async () => {
    console.log('🧪 Testing modified audio loading...');
    
    // Find any sentence with modified audio
    const sentenceWithModified = sentences.find(s => s.modifiedAudioUrl);
    if (!sentenceWithModified) {
      console.log('❌ No sentence with modified audio found');
      return;
    }
    
    console.log('🎵 Found sentence with modified audio:', sentenceWithModified.id);
    console.log('🔗 Modified audio URL:', sentenceWithModified.modifiedAudioUrl);
    
    try {
      // Add cache-busting parameter to prevent 304 responses
      const cacheBustedUrl = `${sentenceWithModified.modifiedAudioUrl}?t=${Date.now()}`;
      console.log('🔗 Cache-busted URL:', cacheBustedUrl);
      
      // Test the URL directly
      const response = await fetch(cacheBustedUrl);
      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const arrayBuffer = await response.arrayBuffer();
      console.log('📦 Audio data size:', arrayBuffer.byteLength, 'bytes');
      
      // Load into audio context
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      console.log('✅ Audio buffer created:', audioBuffer.duration, 'seconds');
      
      // Update the main audio buffer
      audioBufferRef.current = audioBuffer;
      setDuration(audioBuffer.duration);
      setCurrentAudioType('modified');
      setCurrentTime(0);
      
      console.log('🎵 Modified audio loaded successfully!');
      console.log('🎵 Ready to play modified full audio');
      
      // Auto-play the modified audio
      playAudio();
      
    } catch (error) {
      console.error('❌ Error testing modified audio:', error);
    }
  };

  const clearAudioCacheAndReload = async () => {
    console.log('🧹 Clearing audio cache and reloading...');
    
    // Clear the current audio buffer
    audioBufferRef.current = null;
    setDuration(0);
    setCurrentTime(0);
    setIsPlaying(false);
    
    // Find any sentence with modified audio
    const sentenceWithModified = sentences.find(s => s.modifiedAudioUrl);
    if (sentenceWithModified && sentenceWithModified.modifiedAudioUrl) {
      try {
        console.log('🔄 Reloading modified audio after cache clear...');
        // Add cache-busting parameter with a unique timestamp
        const cacheBustedUrl = `${sentenceWithModified.modifiedAudioUrl}?t=${Date.now()}&v=${Math.random()}`;
        await loadAudioFromUrl(cacheBustedUrl, 'modified');
        console.log('✅ Modified audio reloaded successfully');
      } catch (error) {
        console.error('❌ Error reloading modified audio:', error);
      }
    } else {
      console.log('❌ No modified audio found to reload');
    }
  };

  const loadCompleteAudio = async () => {
    try {
      console.log('🔄 Loading complete audio after refinement...');
      
      // Priority 1: Modified full audio (complete refined audio)
      const sentenceWithModifiedAudio = sentences.find(s => s.modifiedAudioUrl);
      if (sentenceWithModifiedAudio && sentenceWithModifiedAudio.modifiedAudioUrl) {
        console.log('🎵 Loading complete modified audio:', sentenceWithModifiedAudio.modifiedAudioUrl);
        const cacheBustedUrl = `${sentenceWithModifiedAudio.modifiedAudioUrl}?t=${Date.now()}`;
        await loadAudioFromUrl(cacheBustedUrl, 'complete');
        console.log('✅ Complete refined audio loaded successfully');
        return true;
      }
      
      // Priority 2: Original processed audio
      if (processedAudio) {
        console.log('🎵 Loading original processed audio as fallback');
        await loadAudioBuffer(processedAudio);
        console.log('✅ Original processed audio loaded successfully');
        return true;
      }
      
      console.log('❌ No complete audio available');
      return false;
    } catch (error) {
      console.error('❌ Error loading complete audio:', error);
      return false;
    }
  };

  const forceLoadCompleteAudio = async () => {
    console.log('🚀 Force loading complete audio...');
    
    // Stop any current playback and clear any existing sources
    if (isPlaying) {
      pauseAudio();
    }
    
    // Ensure no other audio sources are active
    if (sourceNodeRef.current) {
      sourceNodeRef.current.stop();
      sourceNodeRef.current = null;
    }
    
    // Clear current audio buffer
    audioBufferRef.current = null;
    setDuration(0);
    setCurrentTime(0);
    
    // Wait a bit for cleanup
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Try to load complete audio
    const success = await loadCompleteAudio();
    
    if (success) {
      console.log('✅ Complete audio force-loaded successfully');
      // Don't auto-play - let user control playback
      console.log('🎵 Complete audio loaded and ready to play');
    } else {
      console.log('❌ Failed to force-load complete audio');
    }
    
    return success;
  };

  const loadExportedAudio = async (exportedFilename) => {
    try {
      console.log('🎵 Loading exported audio:', exportedFilename);
      
      // Stop any current playback and clear any existing sources
      if (isPlaying) {
        pauseAudio();
      }
      
      // Ensure no other audio sources are active
      if (sourceNodeRef.current) {
        sourceNodeRef.current.stop();
        sourceNodeRef.current = null;
      }
      
      // Clear current audio buffer
      audioBufferRef.current = null;
      setDuration(0);
      setCurrentTime(0);
      
      // Wait a bit for cleanup
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Load the exported audio from the server
      const audioUrl = `/api/download/${exportedFilename}`;
      console.log('🎵 Loading exported audio from URL:', audioUrl);
      
      // Add cache-busting parameter to prevent 304 responses
      const cacheBustedUrl = `${audioUrl}?t=${Date.now()}`;
      await loadAudioFromUrl(cacheBustedUrl, 'exported');
      
      console.log('✅ Exported audio loaded successfully');
      
      // Don't auto-play - let user control playback
      console.log('🎵 Exported audio loaded and ready to play');
      
      return true;
    } catch (error) {
      console.error('❌ Error loading exported audio:', error);
      return false;
    }
  };

  const testExportProcess = async () => {
    console.log('🧪 Testing export process...');
    
    if (!sentences || sentences.length === 0) {
      console.log('❌ No sentences to export');
      return;
    }
    
    console.log('📋 Sentences to export:', sentences);
    
    try {
      // Call the export function directly
      console.log('📤 Calling export function...');
      onExport(sentences);
      
      // Wait a bit and then check if we have an exported file
      setTimeout(async () => {
        const exportedFile = localStorage.getItem('lastExportedFile');
        console.log('📦 Exported file from localStorage:', exportedFile);
        
        if (exportedFile) {
          console.log('🎵 Testing loading of exported file...');
          const success = await loadExportedAudio(exportedFile);
          
          if (success) {
            console.log('✅ Export and load test successful!');
          } else {
            console.log('❌ Export succeeded but loading failed');
          }
        } else {
          console.log('❌ No exported file found in localStorage');
        }
      }, 3000); // Wait 3 seconds for export to complete
      
    } catch (error) {
      console.error('❌ Error in export test:', error);
    }
  };

  const testAudioLoadingDirectly = async () => {
    console.log('🧪 Testing audio loading directly...');
    
    // Test with a known audio file
    const testAudioUrl = '/api/download/generated_speech.wav';
    console.log('🎵 Testing with known audio file:', testAudioUrl);
    
    try {
      // Test if the file exists
      const response = await fetch(testAudioUrl);
      console.log('📡 Response status:', response.status);
      
      if (response.ok) {
        console.log('✅ Test audio file is accessible');
        console.log('📦 File size:', response.headers.get('content-length'), 'bytes');
        
        // Try to load it
        const cacheBustedUrl = `${testAudioUrl}?t=${Date.now()}`;
        await loadAudioFromUrl(cacheBustedUrl, 'test');
        
        console.log('✅ Test audio loaded successfully!');
        console.log('🎵 Audio should now be playing');
      } else {
        console.log('❌ Test audio file not accessible');
      }
    } catch (error) {
      console.error('❌ Error testing audio loading:', error);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-dark-800 rounded-lg overflow-hidden">
      {/* Audio Controls */}
      <div className="p-4 border-b border-dark-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <button
              onClick={isPlaying ? pauseAudio : playAudio}
              className="w-12 h-12 bg-primary-600 hover:bg-primary-700 rounded-full flex items-center justify-center transition-colors"
            >
              {isPlaying ? (
                <Pause className="w-6 h-6 text-white" />
              ) : (
                <Play className="w-6 h-6 text-white ml-1" />
              )}
            </button>
            
            <div className="flex items-center gap-2">
              <button
                onClick={toggleMute}
                className="p-2 hover:bg-dark-700 rounded"
              >
                {isMuted ? (
                  <VolumeX className="w-5 h-5 text-white" />
                ) : (
                  <Volume2 className="w-5 h-5 text-white" />
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-1 bg-dark-600 rounded-full appearance-none cursor-pointer"
              />
            </div>
            
            <span className="text-sm text-white">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
            {currentAudioType !== 'original' && (
              <span className={`text-xs px-2 py-1 rounded-full ${
                currentAudioType === 'complete' 
                  ? 'bg-green-600/20 text-green-400'
                  : currentAudioType === 'modified' 
                  ? 'bg-primary-600/20 text-primary-400'
                  : currentAudioType === 'exported'
                  ? 'bg-purple-600/20 text-purple-400'
                  : 'bg-green-600/20 text-green-400'
              }`}>
                {currentAudioType === 'complete' ? '🎵 Complete Audio' : 
                 currentAudioType === 'modified' ? '🎵 Full Audio' :
                 currentAudioType === 'exported' ? '📦 Exported Audio' :
                 '🎵 Individual'}
              </span>
            )}
            {/* Manual load modified audio button */}
            {sentences.some(s => s.modifiedAudioUrl) && currentAudioType !== 'modified' && currentAudioType !== 'complete' && (
              <button
                onClick={loadModifiedFullAudio}
                className="text-xs px-2 py-1 bg-primary-600/20 text-primary-400 rounded-full hover:bg-primary-600/30 transition-colors"
                title="Load modified full audio"
              >
                🔄 Load Full
              </button>
            )}
            {/* Load complete audio button */}
            {sentences.some(s => s.modifiedAudioUrl) && currentAudioType !== 'complete' && (
              <button
                onClick={loadCompleteAudio}
                className="text-xs px-2 py-1 bg-green-600/20 text-green-400 rounded-full hover:bg-green-600/30 transition-colors"
                title="Load complete refined audio"
              >
                🎵 Load Complete
              </button>
            )}
            {/* Force load complete audio button */}
            {sentences.some(s => s.modifiedAudioUrl) && (
              <button
                onClick={forceLoadCompleteAudio}
                className="text-xs px-2 py-1 bg-red-600/20 text-red-400 rounded-full hover:bg-red-600/30 transition-colors"
                title="Force load complete refined audio"
              >
                🚀 Force Complete
              </button>
            )}
            {/* Load exported audio button */}
            {localStorage.getItem('lastExportedFile') && (
              <button
                onClick={() => {
                  const exportedFile = localStorage.getItem('lastExportedFile');
                  if (exportedFile) {
                    loadExportedAudio(exportedFile);
                  }
                }}
                className="text-xs px-2 py-1 bg-purple-600/20 text-purple-400 rounded-full hover:bg-purple-600/30 transition-colors"
                title="Load last exported audio"
              >
                📦 Load Exported
              </button>
            )}
            {/* Debug button */}
            <button
              onClick={debugAudioUrls}
              className="text-xs px-2 py-1 bg-gray-600/20 text-gray-400 rounded-full hover:bg-gray-600/30 transition-colors"
              title="Debug audio URLs"
            >
              🔍 Debug
            </button>
            {/* Test export button */}
            <button
              onClick={testExportProcess}
              className="text-xs px-2 py-1 bg-blue-600/20 text-blue-400 rounded-full hover:bg-blue-600/30 transition-colors"
              title="Test export process"
            >
              📦 Test Export
            </button>
            {/* Test audio loading button */}
            <button
              onClick={testAudioLoadingDirectly}
              className="text-xs px-2 py-1 bg-yellow-600/20 text-yellow-400 rounded-full hover:bg-yellow-600/30 transition-colors"
              title="Test audio loading directly"
            >
              🎵 Test Audio
            </button>
            {/* Test modified audio button */}
            {sentences.some(s => s.modifiedAudioUrl) && (
              <button
                onClick={testModifiedAudio}
                className="text-xs px-2 py-1 bg-purple-600/20 text-purple-400 rounded-full hover:bg-purple-600/30 transition-colors"
                title="Test modified audio loading"
              >
                🧪 Test
              </button>
            )}
            {/* Cache clear button */}
            {sentences.some(s => s.modifiedAudioUrl) && (
              <button
                onClick={clearAudioCacheAndReload}
                className="text-xs px-2 py-1 bg-orange-600/20 text-orange-400 rounded-full hover:bg-orange-600/30 transition-colors"
                title="Clear cache and reload modified audio"
              >
                🧹 Reload
              </button>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <select
              value={playbackMode}
              onChange={(e) => setPlaybackMode(e.target.value)}
              className="bg-dark-700 border border-dark-600 text-white rounded px-3 py-1 text-sm"
            >
              <option value="original">Original Audio</option>
              {processedAudio && <option value="dubbed">Dubbed Audio</option>}
              {processedAudio && <option value="mixed">Mixed</option>}
            </select>
            
            <button
              onClick={handleSave}
              className="btn-secondary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
            
            <button
              onClick={handleExport}
              className="btn-primary flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div 
          ref={progressBarRef}
          className={`w-full h-4 bg-dark-700 rounded-full cursor-pointer relative group ${
            isDragging ? 'cursor-grabbing' : 'cursor-grab'
          }`}
          onClick={handleSeek}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          {/* Background track */}
          <div className="absolute inset-0 bg-dark-600 rounded-full" />
          
          {/* Progress fill */}
          <div 
            className="h-full bg-primary-600 rounded-full relative transition-all duration-100"
            style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
          >
            {/* Playhead */}
            <div className="absolute right-0 top-1/2 transform -translate-y-1/2 w-4 h-4 bg-primary-400 rounded-full shadow-lg border-2 border-white opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          
          {/* Hover indicator */}
          <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="h-full bg-primary-500/30 rounded-full" />
          </div>
          
          {/* Sentence markers */}
          {sentences.map((sentence, index) => (
            <div
              key={sentence.id}
              className="absolute top-0 bottom-0 w-1 bg-blue-500 cursor-pointer hover:bg-blue-400 transition-colors"
              style={{ 
                left: `${duration > 0 ? (sentence.startTime / duration) * 100 : 0}%`,
                opacity: currentSentence?.id === sentence.id ? 1 : 0.6
              }}
              onClick={(e) => {
                e.stopPropagation();
                setCurrentTime(sentence.startTime);
                setSelectedSentence(sentence.id);
                if (isPlaying) {
                  pauseAudio();
                  setTimeout(() => playAudio(), 100);
                }
              }}
              title={`${sentence.originalText?.substring(0, 30)}...`}
            />
          ))}
          
          {/* Time tooltip on hover */}
          <div className="absolute top-0 left-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="bg-dark-900 text-white text-xs px-2 py-1 rounded shadow-lg">
              {formatTime(currentTime)}
            </div>
          </div>
        </div>
      </div>

      {/* Current Sentence Display */}
      {currentSentence && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-blue-600/20 border-b border-blue-600/30"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-blue-300">Current Sentence</h3>
              <p className="text-white text-sm mt-1">{currentSentence.originalText}</p>
              <div className="flex items-center gap-2 mt-1">
                <p className={`text-sm ${currentSentence.isRefined ? 'text-green-200 font-medium' : 'text-blue-200'}`}>
                  {currentSentence.translatedText}
                </p>
                {currentSentence.isRefined && (
                  <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded-full">
                    ✨ Refined
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Play modified full audio button */}
              {currentSentence.modifiedAudioUrl && (
                <button
                  onClick={() => playModifiedFullAudio(currentSentence)}
                  className="btn-primary text-xs px-2 py-1 flex items-center gap-1"
                  title="Play modified full audio with all sentences"
                >
                  <Play className="w-3 h-3" />
                  Play Full
                </button>
              )}
              
              {/* Play refined audio button */}
              {currentSentence.audioUrl && (
                <button
                  onClick={() => playSentenceAudio(currentSentence)}
                  className="btn-success text-xs px-2 py-1 flex items-center gap-1"
                  title="Play refined audio"
                >
                  <Volume2 className="w-3 h-3" />
                  Play Refined
                </button>
              )}
              
              <button
                onClick={() => handleSentenceEdit(currentSentence.id, 'startTime', currentTime)}
                className="btn-secondary text-xs px-2 py-1"
              >
                <Edit3 className="w-3 h-3" />
                Edit
              </button>
              <button
                onClick={() => handleSentenceSplit(currentSentence.id)}
                className="btn-secondary text-xs px-2 py-1"
              >
                <Scissors className="w-3 h-3" />
                Split
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Sentences List */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {sentences.map((sentence, index) => (
            <motion.div
              key={sentence.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`card cursor-pointer transition-all ${
                selectedSentence === sentence.id ? 'ring-2 ring-primary-500' : ''
              }`}
              onClick={() => setSelectedSentence(sentence.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-dark-400">
                      {formatTime(sentence.startTime)} - {formatTime(sentence.startTime + sentence.duration)}
                    </span>
                    <span className="text-xs text-dark-400">
                      Duration: {formatTime(sentence.duration)}
                    </span>
                  </div>
                  
                  <div className="space-y-1">
                    <p className="text-sm text-white">{sentence.originalText}</p>
                    <div className="flex items-center gap-2">
                      <p className={`text-sm ${sentence.isRefined ? 'text-green-300 font-medium' : 'text-blue-300'}`}>
                        {sentence.translatedText}
                      </p>
                      {sentence.isRefined && (
                        <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded-full">
                          ✨ Refined
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setCurrentTime(sentence.startTime);
                    }}
                    className="p-2 hover:bg-dark-600 rounded"
                    title="Jump to sentence"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  
                  {/* Play modified full audio button */}
                  {sentence.modifiedAudioUrl && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        playModifiedFullAudio(sentence);
                      }}
                      className="p-2 hover:bg-primary-600/20 rounded text-primary-400"
                      title="Play modified full audio with all sentences"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  )}
                  
                  {/* Play refined audio button */}
                  {sentence.audioUrl && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        playSentenceAudio(sentence);
                      }}
                      className="p-2 hover:bg-green-600/20 rounded text-green-400"
                      title="Play refined audio"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSentenceEdit(sentence.id, 'startTime', currentTime);
                    }}
                    className="p-2 hover:bg-dark-600 rounded"
                    title="Edit sentence"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSentenceDelete(sentence.id);
                    }}
                    className="p-2 hover:bg-red-600/20 rounded text-red-400"
                    title="Delete sentence"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
});

AudioEditor.displayName = 'AudioEditor';

export default AudioEditor; 