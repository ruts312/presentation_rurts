import React from 'react';
import { useVoiceRecorder } from '../hooks/useVoiceRecorder';

interface VoiceRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  disabled?: boolean;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onRecordingComplete, disabled = false }) => {
  const { isRecording, audioBlob, startRecording, stopRecording, clearRecording } = useVoiceRecorder();

  const handleStart = () => {
    clearRecording();
    startRecording();
  };

  const handleStop = () => {
    stopRecording();
  };

  const handleSubmit = () => {
    if (audioBlob) {
      onRecordingComplete(audioBlob);
      clearRecording();
    }
  };

  return (
    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Задайте вопрос голосом
      </h3>

      <div className="flex flex-col items-center gap-4">
        {!isRecording && !audioBlob && (
          <button
            onClick={handleStart}
            disabled={disabled}
            className="bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-full p-6 transition-colors shadow-lg"
            title="Начать запись"
          >
            <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          </button>
        )}

        {isRecording && (
          <div className="flex flex-col items-center gap-4">
            <div className="flex items-center gap-3 text-red-600 dark:text-red-400">
              <div className="w-4 h-4 bg-red-600 rounded-full animate-pulse" />
              <span className="text-lg font-semibold">Идет запись...</span>
            </div>
            <button
              onClick={handleStop}
              className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Остановить запись
            </button>
          </div>
        )}

        {audioBlob && !isRecording && (
          <div className="flex flex-col items-center gap-4 w-full">
            <div className="flex items-center gap-3 text-green-600 dark:text-green-400">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
              </svg>
              <span className="text-lg font-semibold">Запись готова</span>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={handleSubmit}
                className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                Отправить вопрос
              </button>
              <button
                onClick={clearRecording}
                className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                Перезаписать
              </button>
            </div>
          </div>
        )}
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-400 mt-4 text-center">
        Нажмите кнопку и задайте свой вопрос на кыргызском или русском языке
      </p>
    </div>
  );
};

export default VoiceRecorder;
