/**
 * Utility functions for video processing
 */

/**
 * Extract audio from a video file using Web Audio API
 * @param {File} videoFile - The video file to extract audio from
 * @returns {Promise<Blob>} - Audio blob
 */
export const extractAudioFromVideo = async (videoFile) => {
  return new Promise((resolve, reject) => {
    try {
      // Create video element to load the video
      const video = document.createElement('video');
      video.muted = true;
      video.crossOrigin = 'anonymous';
      
      // Create audio context
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const destination = audioContext.createMediaStreamDestination();
      
      // Create media element source
      const source = audioContext.createMediaElementSource(video);
      source.connect(destination);
      
      // Create MediaRecorder to record the audio
      const mediaRecorder = new MediaRecorder(destination.stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      const audioChunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        try {
          // Create audio blob
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          
          // Convert to WAV format for better compatibility
          const wavBlob = await convertToWav(audioBlob);
          resolve(wavBlob);
        } catch (error) {
          reject(error);
        }
      };
      
      // Handle video load events
      video.onloadedmetadata = () => {
        video.currentTime = 0;
      };
      
      video.onseeked = () => {
        // Start recording when video is ready
        mediaRecorder.start();
        video.play();
      };
      
      video.onended = () => {
        // Stop recording when video ends
        mediaRecorder.stop();
      };
      
      video.onerror = (error) => {
        reject(new Error('Failed to load video: ' + error.message));
      };
      
      // Load the video
      video.src = URL.createObjectURL(videoFile);
      
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Convert audio blob to WAV format
 * @param {Blob} audioBlob - Audio blob to convert
 * @returns {Promise<Blob>} - WAV format blob
 */
const convertToWav = async (audioBlob) => {
  return new Promise((resolve, reject) => {
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const fileReader = new FileReader();
      
      fileReader.onload = async (event) => {
        try {
          const arrayBuffer = event.target.result;
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
          
          // Convert to WAV
          const wavBlob = audioBufferToWav(audioBuffer);
          resolve(wavBlob);
        } catch (error) {
          reject(error);
        }
      };
      
      fileReader.onerror = () => {
        reject(new Error('Failed to read audio file'));
      };
      
      fileReader.readAsArrayBuffer(audioBlob);
    } catch (error) {
      reject(error);
    }
  });
};

/**
 * Convert AudioBuffer to WAV format
 * @param {AudioBuffer} audioBuffer - Audio buffer to convert
 * @returns {Blob} - WAV format blob
 */
const audioBufferToWav = (audioBuffer) => {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const length = audioBuffer.length;
  
  // Create WAV header
  const buffer = new ArrayBuffer(44 + length * numChannels * 2);
  const view = new DataView(buffer);
  
  // WAV header
  const writeString = (offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };
  
  writeString(0, 'RIFF');
  view.setUint32(4, 36 + length * numChannels * 2, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numChannels * 2, true);
  view.setUint16(32, numChannels * 2, true);
  view.setUint16(34, 16, true);
  writeString(36, 'data');
  view.setUint32(40, length * numChannels * 2, true);
  
  // Write audio data
  let offset = 44;
  for (let i = 0; i < length; i++) {
    for (let channel = 0; channel < numChannels; channel++) {
      const sample = Math.max(-1, Math.min(1, audioBuffer.getChannelData(channel)[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
  }
  
  return new Blob([buffer], { type: 'audio/wav' });
};

/**
 * Get video metadata (duration, dimensions, etc.)
 * @param {File} videoFile - Video file to analyze
 * @returns {Promise<Object>} - Video metadata
 */
export const getVideoMetadata = (videoFile) => {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    video.preload = 'metadata';
    
    video.onloadedmetadata = () => {
      resolve({
        duration: video.duration,
        width: video.videoWidth,
        height: video.videoHeight,
        size: videoFile.size,
        type: videoFile.type
      });
    };
    
    video.onerror = () => {
      reject(new Error('Failed to load video metadata'));
    };
    
    video.src = URL.createObjectURL(videoFile);
  });
};

/**
 * Validate video file
 * @param {File} file - File to validate
 * @returns {boolean} - Whether file is valid
 */
export const isValidVideoFile = (file) => {
  const validTypes = [
    'video/mp4',
    'video/avi',
    'video/mov',
    'video/mkv',
    'video/webm',
    'video/quicktime'
  ];
  
  const validExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.qt'];
  
  // Check MIME type
  if (validTypes.includes(file.type)) {
    return true;
  }
  
  // Check file extension
  const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  if (validExtensions.includes(extension)) {
    return true;
  }
  
  return false;
};

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 * @returns {string} - Formatted size string
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Format duration
 * @param {number} seconds - Duration in seconds
 * @returns {string} - Formatted duration string
 */
export const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}; 