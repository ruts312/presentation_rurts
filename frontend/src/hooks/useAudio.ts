import { useState, useRef, useEffect } from 'react';

export const useAudio = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // Создать аудио элемент
  const createAudio = (audioBlob: Blob) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const audio = new Audio(URL.createObjectURL(audioBlob));
    audioRef.current = audio;

    audio.addEventListener('loadedmetadata', () => {
      setDuration(audio.duration);
    });

    audio.addEventListener('timeupdate', () => {
      setCurrentTime(audio.currentTime);
    });

    audio.addEventListener('ended', () => {
      setIsPlaying(false);
      setIsPaused(false);
      setCurrentTime(0);
    });

    return audio;
  };

  // Воспроизвести аудио
  const play = async (audioBlob?: Blob) => {
    if (audioBlob) {
      const audio = createAudio(audioBlob);
      await audio.play();
      setIsPlaying(true);
      setIsPaused(false);
    } else if (audioRef.current) {
      await audioRef.current.play();
      setIsPlaying(true);
      setIsPaused(false);
    }
  };

  // Пауза
  const pause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
      setIsPaused(true);
    }
  };

  // Остановить
  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setIsPaused(false);
      setCurrentTime(0);
    }
  };

  // Очистка при unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  return {
    isPlaying,
    isPaused,
    currentTime,
    duration,
    play,
    pause,
    stop,
  };
};
