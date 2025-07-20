import React, { forwardRef } from 'react';
import { 
  Scissors, 
  Trash2, 
  ZoomIn, 
  ZoomOut, 
  Type, 
  Download, 
  Mic,
  Video,
  Music,
  Volume2
} from 'lucide-react';

const Timeline = forwardRef(({ 
  currentTime, 
  duration, 
  onTimelineClick, 
  uploadedAudio, 
  outputAudio 
}, ref) => {
  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const generateTimeMarkers = () => {
    if (!duration) return [];
    const markers = [];
    const interval = Math.max(5, Math.floor(duration / 10)); // Show markers every 5 seconds or less
    
    for (let i = 0; i <= duration; i += interval) {
      markers.push(i);
    }
    return markers;
  };

  const timeMarkers = generateTimeMarkers();
  const playheadPosition = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="h-48 bg-dark-900 border-t border-dark-700 flex flex-col">
      {/* Timeline Tools */}
      <div className="px-4 py-2 border-b border-dark-700 flex items-center gap-2">
        <button className="p-2 hover:bg-dark-700 rounded" title="Split">
          <Scissors className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-dark-700 rounded" title="Delete">
          <Trash2 className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-dark-700 rounded" title="Zoom In">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-dark-700 rounded" title="Zoom Out">
          <ZoomOut className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-dark-700 rounded" title="Add Text">
          <Type className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-dark-700 rounded" title="Export">
          <Download className="w-4 h-4" />
        </button>
        <button className="p-2 hover:bg-dark-700 rounded" title="Voice Over">
          <Mic className="w-4 h-4" />
        </button>
      </div>

      {/* Timeline Content */}
      <div className="flex-1 flex flex-col">
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
          </div>
        </div>

        {/* Tracks */}
        <div className="flex-1 flex flex-col gap-2 p-2">
          {/* Original Audio Track */}
          <div className="timeline-track">
            <div className="flex items-center gap-2 mr-4">
              <Volume2 className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium">Original Audio</span>
            </div>
            {uploadedAudio ? (
              <div className="flex-1 bg-green-600 rounded h-8 flex items-center justify-center">
                <span className="text-xs text-white font-medium">
                  {uploadedAudio.name}
                </span>
              </div>
            ) : (
              <div className="flex-1 border-2 border-dashed border-dark-600 rounded flex items-center justify-center">
                <span className="text-xs text-dark-400">Drag audio here</span>
              </div>
            )}
          </div>

          {/* Dubbed Audio Track */}
          <div className="timeline-track">
            <div className="flex items-center gap-2 mr-4">
              <Music className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-medium">Dubbed Audio</span>
            </div>
            {outputAudio ? (
              <div className="flex-1 bg-blue-600 rounded h-8 flex items-center justify-center">
                <span className="text-xs text-white font-medium">
                  English Dubbed
                </span>
              </div>
            ) : (
              <div className="flex-1 border-2 border-dashed border-dark-600 rounded flex items-center justify-center">
                <span className="text-xs text-dark-400">Dubbed audio will appear here</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="px-4 py-2 text-center">
        <p className="text-sm text-dark-400">
          Drag and drop audio files here to create your dubbed content
        </p>
      </div>
    </div>
  );
});

Timeline.displayName = 'Timeline';

export default Timeline; 