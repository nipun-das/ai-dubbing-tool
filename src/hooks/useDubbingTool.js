import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const useDubbingTool = () => {
  const [settings, setSettings] = useState({
    inputLanguage: 'hi',
    whisperModel: 'base',
    device: 'auto',
    referenceDuration: 15,
    voiceQualityMode: 'high_quality',
    useSegments: true
  });

  const [originalText, setOriginalText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [outputAudio, setOutputAudio] = useState(null);
  const [sentences, setSentences] = useState([]);
  const [referenceAudioPath, setReferenceAudioPath] = useState(null);
  const [status, setStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const updateSettings = useCallback((newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  const processDubbing = useCallback(async (audioBlob, settings) => {
    try {
      setIsProcessing(true);
      setStatus('🔄 Starting dubbing process...');

      // Create FormData for the request
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.wav');
      formData.append('settings', JSON.stringify(settings));

      // Make API call to the backend
      const response = await axios.post(`${API_BASE_URL}/api/dub`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setStatus(`📤 Uploading... ${percentCompleted}%`);
        },
      });

      const { original_text, translated_text, output_audio_path, reference_audio_path, sentences: sentencesData, status: resultStatus } = response.data;

      setOriginalText(original_text || '');
      setTranslatedText(translated_text || '');
      setSentences(sentencesData || []);
      setReferenceAudioPath(reference_audio_path || null);
      setStatus(resultStatus || '✅ Dubbing completed successfully!');

      // Download the output audio
      if (output_audio_path) {
        try {
          // Extract just the filename from the full path
          const filename = output_audio_path.split('/').pop() || output_audio_path.split('\\').pop();
          const audioUrl = `${API_BASE_URL}/api/download/${filename}`;
          console.log('Downloading audio from:', audioUrl);
          
          const audioResponse = await axios.get(audioUrl, {
            responseType: 'blob'
          });
          setOutputAudio(audioResponse.data);
          console.log('Audio downloaded successfully');
        } catch (error) {
          console.error('Error downloading output audio:', error);
          console.error('Output path was:', output_audio_path);
        }
      }

      return response.data;
    } catch (error) {
      console.error('Error processing dubbing:', error);
      setStatus(`❌ Error: ${error.response?.data?.error || error.message}`);
      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const updateSentence = useCallback((sentenceId, updates) => {
    console.log('🔄 Updating sentence in hook:', sentenceId, updates);
    setSentences(prevSentences => 
      prevSentences.map(sentence => 
        sentence.id === sentenceId ? { ...sentence, ...updates } : sentence
      )
    );
    console.log('✅ Sentence updated in hook');
  }, []);

  const resetResults = useCallback(() => {
    setOriginalText('');
    setTranslatedText('');
    setOutputAudio(null);
    setSentences([]);
    setReferenceAudioPath(null);
    setStatus('');
  }, []);

  return {
    settings,
    updateSettings,
    processDubbing,
    originalText,
    translatedText,
    outputAudio,
    sentences,
    referenceAudioPath,
    status,
    isProcessing,
    resetResults,
    updateSentence
  };
}; 