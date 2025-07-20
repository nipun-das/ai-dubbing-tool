import React, { useState } from 'react';
import { 
  Sparkles, 
  Wand2, 
  Clock, 
  Volume2, 
  Edit3, 
  Check, 
  X, 
  RotateCcw,
  MessageSquare,
  Zap
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const DialogueRefiner = ({ 
  sentence, 
  onRefine, 
  onCancel, 
  originalText, 
  dubbedText,
  startTime,
  duration,
  isVisible = false 
}) => {
  const [refinementPrompt, setRefinementPrompt] = useState('');
  const [isRefining, setIsRefining] = useState(false);
  const [refinedText, setRefinedText] = useState('');
  const [refinementHistory, setRefinementHistory] = useState([]);
  const [selectedStyle, setSelectedStyle] = useState('natural');

  const refinementStyles = [
    { id: 'natural', name: 'Natural', description: 'More conversational and natural flow' },
    { id: 'formal', name: 'Formal', description: 'Professional and formal tone' },
    { id: 'casual', name: 'Casual', description: 'Relaxed and informal style' },
    { id: 'emotional', name: 'Emotional', description: 'More expressive and emotional' },
    { id: 'concise', name: 'Concise', description: 'Shorter and more direct' },
    { id: 'detailed', name: 'Detailed', description: 'More descriptive and elaborate' }
  ];

  const quickPrompts = [
    "Make it more natural and conversational",
    "Keep the same meaning but change the tone",
    "Make it shorter while keeping the key points",
    "Add more emotion and expression",
    "Make it more formal and professional",
    "Simplify the language"
  ];

  const handleRefine = async () => {
    if (!refinementPrompt.trim()) return;
    
    setIsRefining(true);
    try {
      const response = await fetch('/api/refine-dialogue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          originalText,
          currentText: dubbedText,
          refinementPrompt,
          style: selectedStyle,
          startTime,
          duration,
          context: `This dialogue should fit within ${duration.toFixed(2)} seconds and maintain the original timing.`
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setRefinedText(data.refinedText);
        setRefinementHistory(prev => [...prev, {
          prompt: refinementPrompt,
          result: data.refinedText,
          timestamp: new Date().toISOString()
        }]);
      } else {
        throw new Error('Failed to refine dialogue');
      }
    } catch (error) {
      console.error('Error refining dialogue:', error);
      alert('Failed to refine dialogue. Please try again.');
    } finally {
      setIsRefining(false);
    }
  };

  const handleApply = () => {
    if (refinedText) {
      onRefine(refinedText);
      // Show success message
      alert('✅ Dialogue refined successfully!\n\n📝 Text updated in frontend\n🎤 Audio reprocessed with voice cloning\n🔊 You can now play the refined audio');
      onCancel();
    }
  };

  const handleQuickPrompt = (prompt) => {
    setRefinementPrompt(prompt);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onCancel}
      >
        <motion.div
          initial={{ y: 20 }}
          animate={{ y: 0 }}
          className="bg-dark-800 border border-dark-700 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-6 border-b border-dark-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-primary-500/20 rounded-lg">
                <Sparkles className="w-5 h-5 text-primary-500" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Refine Dialogue</h3>
                <p className="text-sm text-dark-400">
                  AI-powered dialogue refinement with timing constraints
                </p>
              </div>
            </div>

            {/* Timing Info */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-500" />
                <span>Start: {formatTime(startTime)}</span>
              </div>
              <div className="flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-green-500" />
                <span>Duration: {formatTime(duration)}</span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto">
            {/* Original vs Current */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-orange-400">
                  Original Text
                </label>
                <div className="p-3 bg-dark-900 border border-dark-600 rounded text-sm">
                  {originalText}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-blue-400">
                  Current Dubbed Text
                </label>
                <div className="p-3 bg-dark-900 border border-dark-600 rounded text-sm">
                  {dubbedText}
                </div>
              </div>
            </div>

            {/* Style Selection */}
            <div>
              <label className="block text-sm font-medium mb-3">Refinement Style</label>
              <div className="grid grid-cols-2 gap-2">
                {refinementStyles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() => setSelectedStyle(style.id)}
                    className={`p-3 text-left rounded border transition-colors ${
                      selectedStyle === style.id
                        ? 'border-primary-500 bg-primary-500/10 text-primary-400'
                        : 'border-dark-600 hover:border-dark-500'
                    }`}
                  >
                    <div className="font-medium text-sm">{style.name}</div>
                    <div className="text-xs text-dark-400">{style.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Quick Prompts */}
            <div>
              <label className="block text-sm font-medium mb-3">Quick Prompts</label>
              <div className="flex flex-wrap gap-2">
                {quickPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickPrompt(prompt)}
                    className="px-3 py-1 text-xs bg-dark-700 hover:bg-dark-600 rounded-full transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Prompt */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Custom Refinement Prompt
              </label>
              <textarea
                value={refinementPrompt}
                onChange={(e) => setRefinementPrompt(e.target.value)}
                placeholder="Describe how you want to refine this dialogue..."
                className="w-full p-3 bg-dark-900 border border-dark-600 rounded resize-none h-20"
                rows={3}
              />
            </div>

            {/* Refine Button */}
            <button
              onClick={handleRefine}
              disabled={isRefining || !refinementPrompt.trim()}
              className="w-full btn-primary flex items-center justify-center gap-2 py-3"
            >
              {isRefining ? (
                <>
                  <div className="spinner" />
                  Refining...
                </>
              ) : (
                <>
                  <Wand2 className="w-4 h-4" />
                  Refine with AI
                </>
              )}
            </button>

            {/* Refined Result */}
            {refinedText && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-3"
              >
                <label className="block text-sm font-medium text-green-400">
                  Refined Text
                </label>
                <div className="p-3 bg-green-500/10 border border-green-500/30 rounded">
                  <p className="text-sm">{refinedText}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleApply}
                    className="flex-1 btn-success flex items-center justify-center gap-2 py-2"
                  >
                    <Check className="w-4 h-4" />
                    Apply Refinement
                  </button>
                  <button
                    onClick={() => setRefinedText('')}
                    className="px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded flex items-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Try Again
                  </button>
                </div>
              </motion.div>
            )}

            {/* Refinement History */}
            {refinementHistory.length > 0 && (
              <div>
                <label className="block text-sm font-medium mb-3">Refinement History</label>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {refinementHistory.slice(-3).reverse().map((item, index) => (
                    <div key={index} className="p-2 bg-dark-900 border border-dark-600 rounded text-xs">
                      <div className="text-dark-400 mb-1">"{item.prompt}"</div>
                      <div className="text-green-400">{item.result}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-dark-700 flex justify-end gap-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Cancel
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DialogueRefiner; 