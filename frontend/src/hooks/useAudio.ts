import { useState, useRef, useEffect } from 'react';

export const useAudio = (onEnded?: () => void) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);
  const audioBlobRef = useRef<Blob | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // Создать аудио элемент
  const createAudio = (audioBlob: Blob) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }

    const url = URL.createObjectURL(audioBlob);
    audioUrlRef.current = url;
    audioBlobRef.current = audioBlob;

    const audio = new Audio(url);
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
      if (onEnded) {
        onEnded();
      }
    });

    return audio;
  };

  // Загрузить аудио (без автозапуска)
  const load = (audioBlob: Blob) => {
    if (audioBlobRef.current === audioBlob && audioRef.current) {
      return;
    }
    createAudio(audioBlob);
    setIsPlaying(false);
    setIsPaused(false);
    setCurrentTime(0);
  };

  // Воспроизвести аудио
  const play = async (audioBlob?: Blob) => {
    if (audioBlob) {
      // Если это тот же blob и аудио уже создано — просто продолжаем
      if (audioBlobRef.current === audioBlob && audioRef.current) {
        await audioRef.current.play();
      } else {
        const audio = createAudio(audioBlob);
        await audio.play();
      }
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
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }
    };
  }, []);

  return {
    isPlaying,
    isPaused,
    currentTime,
    duration,
    load,
    play,
    pause,
    stop,
  };
};
