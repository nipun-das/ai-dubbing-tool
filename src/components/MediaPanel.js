import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Video, Music, FileText, CheckCircle, AlertCircle, Play } from 'lucide-react';
import { motion } from 'framer-motion';

const MediaPanel = ({ 
  onAudioUpload, 
  uploadedAudio, 
  onProcessAudio,
  isProcessing, 
  progress 
}) => {
  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file && (file.type.startsWith('audio/') || file.name.toLowerCase().endsWith('.wav'))) {
      onAudioUpload(file);
    }
  }, [onAudioUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'],
      'application/octet-stream': ['.wav'] // Some systems don't recognize .wav as audio
    },
    multiple: false
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-full flex flex-col">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} flex-1 flex flex-col items-center justify-center`}
      >
        <input {...getInputProps()} />
        
        {!uploadedAudio ? (
          <div className="text-center">
            <Upload className="w-12 h-12 text-dark-400 mx-auto mb-4" />
            <p className="text-dark-400 mb-2">There's nothing yet</p>
            <p className="text-sm text-dark-500">Drag and drop your audio files here</p>
            {isDragActive && (
              <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-primary-500 mt-2"
              >
                Drop the audio file here...
              </motion.p>
            )}
          </div>
        ) : (
                      <div className="w-full">
              <h3 className="text-lg font-semibold mb-4">Uploaded Audio</h3>
              
              {/* Audio File */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card mb-4"
              >
                <div className="flex items-center gap-3">
                  <Music className="w-8 h-8 text-primary-500" />
                  <div className="flex-1">
                    <p className="font-medium truncate">{uploadedAudio.name}</p>
                    <p className="text-sm text-dark-400">
                      {formatFileSize(uploadedAudio.size)} • Audio
                    </p>
                  </div>
                  <CheckCircle className="w-5 h-5 text-green-500" />
                </div>
              </motion.div>

              {/* Process Button */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4"
              >
                <button
                  onClick={onProcessAudio}
                  disabled={isProcessing}
                  className="w-full btn-primary flex items-center justify-center gap-2 py-3"
                >
                  {isProcessing ? (
                    <>
                      <div className="spinner" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Process Audio
                    </>
                  )}
                </button>
              </motion.div>
            </div>
        )}
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-4 bg-dark-800 border border-dark-700 rounded-lg"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="spinner" />
            <span className="font-medium">Processing Audio...</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-dark-400 mt-2">
            {progress < 30 && "Transcribing and translating..."}
            {progress >= 30 && progress < 60 && "Extracting reference audio..."}
            {progress >= 60 && progress < 90 && "Generating dubbed audio..."}
            {progress >= 90 && "Finalizing..."}
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default MediaPanel; 