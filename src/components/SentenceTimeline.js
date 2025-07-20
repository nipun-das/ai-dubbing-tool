import React, { useState, useRef, forwardRef } from 'react';
import { 
  Scissors, 
  Trash2, 
  ZoomIn, 
  ZoomOut, 
  Type, 
  Download, 
  Mic,
  Music,
  Volume2,
  Move,
  Edit3,
  Play,
  Pause,
  Copy,
  RotateCcw,
  Settings,
  Plus,
  Minus,
  Sparkles
} from 'lucide-react';
import { motion, Reorder } from 'framer-motion';
import DialogueRefiner from './DialogueRefiner';

const SentenceTimeline = forwardRef(({ 
  currentTime, 
  duration, 
  onTimelineClick,
  originalAudio,
  originalAudioPath, // Add original audio path
  sentences = [],
  onSentenceUpdate,
  onSentenceReorder,
  onSentenceDelete,
  onSentenceSplit,
  onSentenceMerge,
  zoom = 100,
  onZoomChange,
  onRefinementComplete
}, ref) => {
  const [selectedSentence, setSelectedSentence] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [showWaveform, setShowWaveform] = useState(true);
  const [showDialogueRefiner, setShowDialogueRefiner] = useState(false);
  const [refiningSentence, setRefiningSentence] = useState(null);

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const generateTimeMarkers = () => {
    if (!duration) return [];
    const markers = [];
    const interval = Math.max(1, Math.floor(duration / (zoom / 10))); // Dynamic interval based on zoom
    
    for (let i = 0; i <= duration; i += interval) {
      markers.push(i);
    }
    return markers;
  };

  const timeMarkers = generateTimeMarkers();
  const playheadPosition = duration > 0 ? (currentTime / duration) * 100 : 0;

  const handleSentenceClick = (sentence) => {
    setSelectedSentence(sentence.id);
  };

  const handleSentenceDrag = (sentenceId, newStartTime) => {
    if (onSentenceUpdate) {
      onSentenceUpdate(sentenceId, { startTime: newStartTime });
    }
  };

  const handleSentenceResize = (sentenceId, newDuration) => {
    if (onSentenceUpdate) {
      onSentenceUpdate(sentenceId, { duration: newDuration });
    }
  };

  const handleDialogueRefine = async (refinedText) => {
    if (refiningSentence && onSentenceUpdate) {
      console.log('🔄 Refining dialogue:', refinedText);
      
      // First, update the sentence text immediately in the frontend
      onSentenceUpdate(refiningSentence.id, { 
        translatedText: refinedText,
        isRefined: true // Mark as refined
      });
      
      // Trigger automatic audio reprocessing with voice cloning
      try {
        console.log('🎤 Reprocessing audio with voice cloning...');
        const response = await fetch('/api/reprocess-sentence', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            sentenceId: refiningSentence.id,
            originalText: refiningSentence.originalText,
            refinedText: refinedText,
            startTime: refiningSentence.startTime,
            duration: refiningSentence.duration,
            referenceAudioPath: refiningSentence.referenceAudioPath || 'reference_audio.wav', // Fallback
            originalAudioPath: originalAudioPath, // Add original audio path
            useVoiceCloning: true // Ensure voice cloning is used
          }),
        });

        if (response.ok) {
          const result = await response.json();
          console.log('✅ Audio reprocessed successfully:', result);
          
          // Update the sentence with new audio data and mark as refined
          onSentenceUpdate(refiningSentence.id, { 
            translatedText: refinedText,
            dubbedAudio: result.sentenceAudioPath || result.audioPath,
            audioUrl: result.sentenceAudioUrl || result.audioUrl,
            modifiedAudioPath: result.modifiedAudioPath,
            modifiedAudioUrl: result.modifiedAudioUrl,
            isRefined: true,
            refinedAt: new Date().toISOString()
          });
          
          // Debug: Log the complete response
          console.log('🎵 Complete backend response:', result);
          console.log('🎵 Individual sentence audio URL:', result.sentenceAudioUrl || result.audioUrl);
          console.log('🎵 Modified full audio URL:', result.modifiedAudioUrl);
          console.log('🎵 Individual sentence audio path:', result.sentenceAudioPath || result.audioPath);
          console.log('🎵 Modified full audio path:', result.modifiedAudioPath);
          
          // Force a re-render to show the updated text
          setTimeout(() => {
            const updatedSentence = sentences.find(s => s.id === refiningSentence.id);
            if (updatedSentence) {
              console.log('📝 Updated sentence text:', updatedSentence.translatedText);
              console.log('🎵 Updated sentence audio URLs:', {
                audioUrl: updatedSentence.audioUrl,
                modifiedAudioUrl: updatedSentence.modifiedAudioUrl
              });
            }
            
            // Notify parent component that refinement is complete
            if (onRefinementComplete) {
              console.log('🔄 Notifying parent component of refinement completion...');
              onRefinementComplete();
            }
          }, 100);
          
        } else {
          console.error('❌ Audio reprocessing failed:', response.statusText);
        }
      } catch (error) {
        console.error('❌ Error reprocessing audio:', error);
        // Still update the text even if audio fails
        onSentenceUpdate(refiningSentence.id, { 
          translatedText: refinedText,
          isRefined: true
        });
      }
    }
  };

  const handleDialogueRefinerCancel = () => {
    setShowDialogueRefiner(false);
    setRefiningSentence(null);
  };

  const getSentencePosition = (sentence) => {
    if (!duration) return 0;
    return (sentence.startTime / duration) * 100;
  };

  const getSentenceWidth = (sentence) => {
    if (!duration) return 10;
    const width = (sentence.duration / duration) * 100;
    return Math.max(width, 5); // Minimum width of 5%
  };

  return (
    <div className="h-96 bg-dark-900 border-t border-dark-700 flex flex-col">
      {/* Timeline Tools */}
      <div className="px-4 py-2 border-b border-dark-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-dark-700 rounded" title="Split Sentence">
            <Scissors className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Delete Sentence">
            <Trash2 className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Merge Sentences">
            <Plus className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Edit Text">
            <Edit3 className="w-4 h-4" />
          </button>
          <button 
            className="p-2 hover:bg-dark-700 rounded" 
            title="Refine Dialogue with AI"
            onClick={() => {
              if (selectedSentence) {
                const sentence = sentences.find(s => s.id === selectedSentence);
                if (sentence) {
                  setRefiningSentence(sentence);
                  setShowDialogueRefiner(true);
                }
              }
            }}
          >
            <Sparkles className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Copy Sentence">
            <Copy className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Reset Changes">
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button 
            className="p-2 hover:bg-dark-700 rounded" 
            title="Toggle Waveform"
            onClick={() => setShowWaveform(!showWaveform)}
          >
            <Volume2 className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Zoom Out">
            <ZoomOut className="w-4 h-4" onClick={() => onZoomChange(Math.max(50, zoom - 25))} />
          </button>
          <span className="text-sm text-dark-400 w-12 text-center">{zoom}%</span>
          <button className="p-2 hover:bg-dark-700 rounded" title="Zoom In">
            <ZoomIn className="w-4 h-4" onClick={() => onZoomChange(Math.min(400, zoom + 25))} />
          </button>
          <button className="p-2 hover:bg-dark-700 rounded" title="Settings">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Timeline Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Time Ruler */}
        <div className="h-8 bg-dark-800 border-b border-dark-700 relative">
          <div 
            ref={ref}
            className="w-full h-full relative cursor-pointer"
            onClick={onTimelineClick}
          >
            {/* Time Markers */}
            {timeMarkers.map((time) => (
              <div
                key={time}
                className="absolute top-0 bottom-0 flex flex-col items-center"
                style={{ left: `${(time / duration) * 100}%` }}
              >
                <div className="w-px h-4 bg-dark-600" />
                <span className="text-xs text-dark-400 mt-1">
                  {formatTime(time)}
                </span>
              </div>
            ))}

            {/* Playhead */}
            <div 
              className="playhead"
              style={{ left: `${playheadPosition}%` }}
            />
            
            {/* Current time indicator */}
            <div 
              className="absolute top-0 bottom-0 w-0.5 bg-red-500 pointer-events-none"
              style={{ left: `${playheadPosition}%` }}
            />
          </div>
        </div>

        {/* Tracks Container */}
        <div className="flex-1 overflow-y-auto">
          {/* Original Audio Track */}
          <div className="timeline-track border-b border-dark-700">
            <div className="flex items-center gap-2 mr-4 min-w-32">
              <Volume2 className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium">Original Audio</span>
            </div>
            <div className="flex-1 relative h-12">
              {originalAudio ? (
                <div className="w-full h-full bg-green-600/20 rounded flex items-center justify-center">
                  <span className="text-xs text-green-400 font-medium">
                    {originalAudio.name}
                  </span>
                  {showWaveform && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="flex items-end gap-px h-6">
                        {Array.from({ length: 50 }, (_, i) => (
                          <div
                            key={i}
                            className="w-1 bg-green-400/60 rounded-sm"
                            style={{ height: `${Math.random() * 100}%` }}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="w-full h-full border-2 border-dashed border-dark-600 rounded flex items-center justify-center">
                  <span className="text-xs text-dark-400">No audio loaded</span>
                </div>
              )}
            </div>
          </div>

          {/* Sentences Track */}
          <div className="timeline-track">
            <div className="flex items-center gap-2 mr-4 min-w-32">
              <Type className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium">Sentences</span>
              <span className="text-xs text-dark-400">({sentences.length})</span>
            </div>
            <div className="flex-1 relative h-12 bg-dark-600/30 rounded overflow-x-auto">
              {sentences.length > 0 ? (
                <div className="flex h-full items-center gap-2 px-2" style={{ minWidth: `${sentences.length * 200}px` }}>
                  {/* Scroll indicator */}
                  {sentences.length > 5 && (
                    <div className="absolute top-1 right-2 text-xs text-dark-400 bg-dark-800/80 px-2 py-1 rounded">
                      Scroll to see more →
                    </div>
                  )}
                  {sentences.map((sentence, index) => (
                    <motion.div
                      key={sentence.id}
                      className={`flex-shrink-0 h-10 rounded cursor-pointer transition-all ${
                        selectedSentence === sentence.id 
                          ? 'bg-blue-500 border-2 border-blue-300' 
                          : currentTime >= sentence.startTime && currentTime <= sentence.startTime + sentence.duration
                          ? 'bg-blue-400 border-2 border-blue-200'
                          : 'bg-blue-600/80 hover:bg-blue-500/90'
                      }`}
                      style={{
                        width: '180px',
                        minWidth: '180px',
                        zIndex: selectedSentence === sentence.id ? 10 : 1
                      }}
                      onClick={() => handleSentenceClick(sentence)}
                      drag="x"
                      dragConstraints={{
                        left: -index * 200,
                        right: (sentences.length - index - 1) * 200
                      }}
                      dragElastic={0}
                      dragMomentum={false}
                      onDragStart={() => setIsDragging(true)}
                      onDragEnd={(e, info) => {
                        setIsDragging(false);
                        // Calculate new position based on drag
                        const newIndex = Math.round((info.point.x + index * 200) / 200);
                        const clampedIndex = Math.max(0, Math.min(sentences.length - 1, newIndex));
                        if (clampedIndex !== index && onSentenceReorder) {
                          // Reorder sentences
                          const newOrder = [...sentences];
                          const [movedSentence] = newOrder.splice(index, 1);
                          newOrder.splice(clampedIndex, 0, movedSentence);
                          onSentenceReorder(newOrder);
                        }
                      }}
                    >
                                              <div className="h-full flex items-center justify-between px-2">
                          <div className="flex items-center gap-1 flex-1 min-w-0">
                            <div className="flex items-center gap-1">
                              <span className="text-xs text-white/40 font-mono bg-white/10 px-1 rounded">
                                {index + 1}
                              </span>
                              <Move className="w-3 h-3 text-white/60 flex-shrink-0" />
                            </div>
                            <div className="flex flex-col min-w-0 flex-1">
                              <span className="text-xs text-white font-medium truncate">
                                {(sentence.originalText || '').substring(0, 15)}...
                              </span>
                              <span className={`text-xs truncate ${sentence.isRefined ? 'text-green-300 font-medium' : 'text-white/70'}`}>
                                {(sentence.translatedText || '').substring(0, 15)}...
                              </span>
                            </div>
                          </div>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          <button
                            className="p-1 hover:bg-white/20 rounded transition-colors"
                            onClick={(e) => {
                              e.stopPropagation();
                              setRefiningSentence(sentence);
                              setShowDialogueRefiner(true);
                            }}
                            title="Refine Dialogue"
                          >
                            <Sparkles className="w-3 h-3 text-white/80 hover:text-white" />
                          </button>
                          {sentence.isRefined && (
                            <span className="text-xs text-green-400">✨</span>
                          )}
                          <div className="flex flex-col items-end">
                            <span className="text-xs text-white/60">
                              {formatTime(sentence.startTime)} - {formatTime(sentence.startTime + sentence.duration)}
                            </span>
                            <span className="text-xs text-white/60">
                              {formatTime(sentence.duration)}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Resize handles */}
                      <div 
                        className="absolute left-0 top-0 bottom-0 w-1 bg-white/30 cursor-ew-resize"
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          // Handle left resize
                        }}
                      />
                      <div 
                        className="absolute right-0 top-0 bottom-0 w-1 bg-white/30 cursor-ew-resize"
                        onMouseDown={(e) => {
                          e.stopPropagation();
                          // Handle right resize
                        }}
                      />
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="w-full h-full border-2 border-dashed border-dark-600 rounded flex items-center justify-center">
                  <span className="text-xs text-dark-400">No sentences detected</span>
                </div>
              )}
            </div>
          </div>

          {/* Dubbed Audio Track */}
          <div className="timeline-track">
            <div className="flex items-center gap-2 mr-4 min-w-32">
              <Music className="w-4 h-4 text-purple-500" />
              <span className="text-sm font-medium">Dubbed Audio</span>
            </div>
            <div className="flex-1 relative h-12">
              {sentences.some(s => s.dubbedAudio) ? (
                <div className="w-full h-full relative">
                  {sentences.map((sentence) => (
                    sentence.dubbedAudio && (
                      <div
                        key={`dubbed-${sentence.id}`}
                        className="absolute top-1 bottom-1 bg-purple-600/80 rounded"
                        style={{
                          left: `${getSentencePosition(sentence)}%`,
                          width: `${getSentenceWidth(sentence)}%`
                        }}
                      >
                        <div className="h-full flex items-center justify-center">
                          <Play className="w-3 h-3 text-white" />
                        </div>
                      </div>
                    )
                  ))}
                </div>
              ) : (
                <div className="w-full h-full border-2 border-dashed border-dark-600 rounded flex items-center justify-center">
                  <span className="text-xs text-dark-400">Dubbed audio will appear here</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Sentence Details Panel */}
      {selectedSentence && (
        <div className="h-32 bg-dark-800 border-t border-dark-700 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium">Sentence Details</h3>
            <button 
              onClick={() => setSelectedSentence(null)}
              className="text-dark-400 hover:text-white"
            >
              ×
            </button>
          </div>
          {(() => {
            const sentence = sentences.find(s => s.id === selectedSentence);
            if (!sentence) return null;
            
            return (
              <div className="space-y-2">
                <div className="flex items-center gap-4 text-xs">
                  <span>Start: {formatTime(sentence.startTime)}</span>
                  <span>Duration: {formatTime(sentence.duration)}</span>
                  <span>End: {formatTime(sentence.startTime + sentence.duration)}</span>
                </div>
                <div className="bg-dark-700 rounded p-2">
                  <p className="text-xs text-white">{sentence.originalText || sentence.translatedText || 'No text'}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button className="btn-secondary text-xs px-2 py-1">
                    <Play className="w-3 h-3" />
                    Play
                  </button>
                  <button className="btn-secondary text-xs px-2 py-1">
                    <Edit3 className="w-3 h-3" />
                    Edit
                  </button>
                  <button 
                    className="btn-secondary text-xs px-2 py-1 flex items-center gap-1"
                    onClick={() => {
                      setRefiningSentence(sentence);
                      setShowDialogueRefiner(true);
                    }}
                  >
                    <Sparkles className="w-3 h-3" />
                    Refine
                  </button>
                  <button className="btn-secondary text-xs px-2 py-1">
                    <Mic className="w-3 h-3" />
                    Re-dub
                  </button>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Dialogue Refiner Modal */}
      {showDialogueRefiner && refiningSentence && (
        <DialogueRefiner
          sentence={refiningSentence}
          onRefine={handleDialogueRefine}
          onCancel={handleDialogueRefinerCancel}
          originalText={refiningSentence.originalText || ''}
          dubbedText={refiningSentence.translatedText || ''}
          startTime={refiningSentence.startTime || 0}
          duration={refiningSentence.duration || 0}
          isVisible={showDialogueRefiner}
        />
      )}
    </div>
  );
});

SentenceTimeline.displayName = 'SentenceTimeline';

export default SentenceTimeline; 