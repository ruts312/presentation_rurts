import React, { useEffect } from 'react';
import { useAudio } from '../hooks/useAudio';

interface AudioPlayerProps {
  audioBlob: Blob | null;
  autoPlay?: boolean;
  onEnded?: () => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioBlob, autoPlay = false, onEnded }) => {
  const { isPlaying, currentTime, duration, play, pause, stop } = useAudio(onEnded);

  useEffect(() => {
    if (audioBlob && autoPlay) {
      play(audioBlob);
    }
  }, [audioBlob, autoPlay]);

  const handlePlay = () => {
    if (audioBlob) {
      play(audioBlob);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!audioBlob) {
    return null;
  }

  return (
    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 flex items-center gap-4">
      <div className="flex gap-2">
        {!isPlaying ? (
          <button
            onClick={handlePlay}
            className="bg-primary-600 hover:bg-primary-700 text-white rounded-full p-3 transition-colors"
            title="Воспроизвести"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </button>
        ) : (
          <button
            onClick={pause}
            className="bg-primary-600 hover:bg-primary-700 text-white rounded-full p-3 transition-colors"
            title="Пауза"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
            </svg>
          </button>
        )}
        
        <button
          onClick={stop}
          className="bg-gray-600 hover:bg-gray-700 text-white rounded-full p-3 transition-colors"
          title="Остановить"
        >
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 6h12v12H6z" />
          </svg>
        </button>
      </div>

      <div className="flex-1">
        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
        <div className="w-full bg-gray-300 dark:bg-gray-600 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all"
            style={{ width: `${(currentTime / duration) * 100 || 0}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;
