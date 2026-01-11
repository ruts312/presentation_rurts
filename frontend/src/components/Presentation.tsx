import React, { useState, useEffect, useRef } from 'react';
import Slide from './Slide';
import AudioPlayer from './AudioPlayer';
import VoiceRecorder from './VoiceRecorder';
import { fetchSlides, textToSpeech, speechToText, askQuestion, Slide as SlideType, API_ORIGIN } from '../services/api';

const pad2 = (n: number) => String(n).padStart(2, '0');

type PresentationLanguage = 'ky' | 'ru';

const Presentation: React.FC = () => {
  const [slides, setSlides] = useState<SlideType[]>([]);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [presentationLanguage] = useState<PresentationLanguage>('ru');
  const audioRequestSeq = useRef(0);
  
  // Новые состояния
  const [hasStarted, setHasStarted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [, setIsAudioPlaying] = useState(false);
  
  // Состояние для чата
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', text: string, audio?: Blob}>>([]);
  const [isProcessingQA, setIsProcessingQA] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [textInput, setTextInput] = useState('');

  // Если STT не распознал речь (пусто/ошибка), показываем модальное окно.
  const [isSttErrorOpen, setIsSttErrorOpen] = useState(false);
  const [sttErrorMessage, setSttErrorMessage] = useState<string>('');
  const showSttFailurePopup = (message: string) => {
    setSttErrorMessage(message);
    setIsSttErrorOpen(true);
  };
  
  // Загрузка слайдов при монтировании
  useEffect(() => {
    loadSlides('ru');
  }, []);

  // Загрузка аудио при смене слайда
  useEffect(() => {
    if (slides.length > 0 && hasStarted) {
      loadSlideAudio(slides[currentSlideIndex]);
    }
  }, [currentSlideIndex, slides, hasStarted]);

  const loadSlides = async (language: PresentationLanguage) => {
    try {
      setIsLoading(true);
      const data = await fetchSlides(language);
      setSlides(data.slides);
      setCurrentSlideIndex(0);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки слайдов');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSlideAudio = async (slide: SlideType) => {
    const requestId = ++audioRequestSeq.current;
    try {
      // 1) Пытаемся взять готовый файл озвучки для слайда
      const audioUrl = `${API_ORIGIN}/audio/ru/slide_${pad2(slide.id)}.wav`;
      const audioResponse = await fetch(audioUrl);

      if (audioResponse.ok) {
        const audio = await audioResponse.blob();
        if (requestId !== audioRequestSeq.current) return;
        setAudioBlob(audio);
        setIsAudioPlaying(true);
        return;
      }

      // 2) Фолбэк: синтезируем на лету (если файл отсутствует)
      const audio = await textToSpeech(slide.tts ?? slide.content, presentationLanguage);
      if (requestId !== audioRequestSeq.current) return;
      setAudioBlob(audio);
      setIsAudioPlaying(true);
    } catch (err) {
      console.error('Error loading audio:', err);
    }
  };

  const handleAudioEnd = () => {
    setIsAudioPlaying(false);
    // Автоматически перейти к следующему слайду
    if (isPlaying) {
      setTimeout(() => {
        setCurrentSlideIndex((idx) => {
          if (idx >= slides.length - 1) {
            setIsPlaying(false);
            return idx;
          }
          return idx + 1;
        });
      }, 1000); // Пауза 1 секунда перед следующим слайдом
    }
  };

  const startPresentation = () => {
    setHasStarted(true);
    setIsPlaying(true);
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const nextSlide = () => {
    if (currentSlideIndex < slides.length - 1) {
      setCurrentSlideIndex(currentSlideIndex + 1);
    }
  };

  const previousSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
    }
  };

  const handleTextQuestion = async () => {
    if (!textInput.trim()) return;

    const question = textInput.trim();
    const userMessage = { role: 'user' as const, text: question };
    setMessages(prev => [...prev, userMessage]);
    setTextInput('');
    setIsProcessingQA(true);
    
    try {
      const currentSlide = slides[currentSlideIndex];
      const response = await askQuestion({
        question,
        slide_context: currentSlide.content,
        slide_id: currentSlide.id,
        language: presentationLanguage,
      });

      // Конвертировать base64 аудио в Blob
      const audioData = atob(response.audio);
      const audioArray = new Uint8Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i);
      }
      const answerBlob = new Blob([audioArray], { type: 'audio/wav' });

      setMessages(prev => [...prev, { role: 'assistant', text: response.answer, audio: answerBlob }]);
    } catch (err) {
      console.error('Error processing question:', err);
      setMessages(prev => [...prev, { role: 'assistant', text: presentationLanguage === 'ru'
        ? 'Извините, произошла ошибка при обработке вашего вопроса.'
        : 'Кечиресиз, суроону иштетүүдө ката кетти.' }]);
    } finally {
      setIsProcessingQA(false);
    }
  };

  const handleRecordingComplete = async (recordedAudioBlob: Blob) => {
    setIsProcessingQA(true);

    try {
      // 1. Распознать речь
      let transcription = '';
      try {
        transcription = (await speechToText(recordedAudioBlob, presentationLanguage)).trim();
      } catch (err) {
        console.error('STT error:', err);
        const fallback = 'Не удалось распознать речь. Попробуйте ещё раз.';
        const msg = err instanceof Error && err.message ? err.message : fallback;
        showSttFailurePopup(msg);
        return;
      }

      // Если распознать не удалось — не отправляем в чат, а показываем окошко.
      if (!transcription) {
        showSttFailurePopup('Не удалось распознать речь. Попробуйте ещё раз.');
        return;
      }

      // 2) Вставить распознанный текст в поле ввода, чтобы пользователь мог
      // отредактировать и отправить вручную.
      setIsChatOpen(true);
      setTextInput(transcription);
    } catch (err) {
      console.error('Error processing question:', err);
      setMessages(prev => [...prev, { role: 'assistant', text: 'Извините, произошла ошибка при обработке вашего вопроса.' }]);
    } finally {
      setIsProcessingQA(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка презентации...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center text-red-600">
          <p className="text-xl font-bold mb-2">❌ Ошибка</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (slides.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <p className="text-gray-600 dark:text-gray-400">Нет доступных слайдов</p>
      </div>
    );
  }

  // Стартовый экран
  if (!hasStarted) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-600 to-indigo-900">
        <div className="text-center text-white px-4">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-pulse">
            Права человека и МВД Кыргызской Республики
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100">
            Презентация о правах человека и о том, как МВД помогает защищать эти права
          </p>
          <div className="mb-8 text-lg text-blue-100">
            <p>📊 {slides.length} слайд</p>
            <p>🎤 Голосовой ИИ‑ассистент</p>
            <p>🔊 Автоматическая озвучка</p>
          </div>

          <button
            onClick={startPresentation}
            className="bg-white text-blue-600 px-12 py-6 rounded-2xl font-bold text-2xl hover:bg-blue-50 transition-all transform hover:scale-105 shadow-2xl"
          >
            ▶️ Начать презентацию
          </button>
        </div>
      </div>
    );
  }

  const currentSlide = slides[currentSlideIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex flex-col">
      {/* Основной контент */}
      <div className="flex-1 p-4 md:p-8 pb-0">
        <div className="w-full max-w-none">
          {/* Заголовок и контроли */}
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
              Права человека и МВД Кыргызской Республики
            </h1>
            <div className="flex gap-2">
              <button
                onClick={togglePlayPause}
                className={`${isPlaying ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white px-6 py-2 rounded-lg font-semibold transition-colors`}
              >
                {isPlaying ? '⏸️ Пауза' : '▶️ Воспроизвести'}
              </button>
            </div>
          </div>

          {/* Слайд */}
          <div className="mb-6">
            <Slide slide={currentSlide} />
          </div>

          {/* Аудио плеер (скрытый, но с колбэком) */}
          {audioBlob && (
            <div className="mb-4">
              <AudioPlayer 
                audioBlob={audioBlob} 
                autoPlay={isPlaying} 
                onEnded={handleAudioEnd}
              />
            </div>
          )}

          {/* Навигация */}
          <div className="flex justify-between items-center mb-6">
            <button
              onClick={previousSlide}
              disabled={currentSlideIndex === 0}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
              </svg>
              Назад
            </button>

            <div className="text-center">
              <p className="text-gray-700 dark:text-gray-300 font-semibold text-lg">
                {currentSlideIndex + 1} / {slides.length}
              </p>
              <div className="flex gap-1 mt-2 justify-center">
                {slides.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-2 w-2 rounded-full ${idx === currentSlideIndex ? 'bg-blue-600' : 'bg-gray-300'}`}
                  />
                ))}
              </div>
            </div>

            <button
              onClick={nextSlide}
              disabled={currentSlideIndex === slides.length - 1}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              Далее
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Чат внизу */}
      <div className="bg-white dark:bg-gray-800 border-t-4 border-blue-600 shadow-2xl">
        <div className="w-full max-w-none">
          {/* Заголовок чата */}
          <div 
            className="flex justify-between items-center p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
            onClick={() => setIsChatOpen(!isChatOpen)}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🤖</span>
              <div>
                <h3 className="font-bold text-gray-900 dark:text-white">Чат с ИИ Ассистентом</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Задайте вопрос голосом или текстом</p>
              </div>
            </div>
            <button className="text-3xl text-gray-600 dark:text-gray-400">
              {isChatOpen ? '▼' : '▲'}
            </button>
          </div>

          {/* Сообщения чата */}
          {isChatOpen && (
            <div className="border-t border-gray-200 dark:border-gray-700">
              <div className="h-64 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                    <p className="text-xl mb-2">💬</p>
                    <p>Задайте вопрос по текущему слайду</p>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-md px-4 py-2 rounded-lg ${
                        msg.role === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                      }`}>
                        <p>{msg.text}</p>
                        {msg.audio && (
                          <div className="mt-2">
                            <audio controls className="w-full" src={URL.createObjectURL(msg.audio)} />
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                {isProcessingQA && (
                  <div className="flex justify-start">
                    <div className="bg-gray-200 dark:bg-gray-700 px-4 py-2 rounded-lg">
                      <div className="animate-pulse">Думаю...</div>
                    </div>
                  </div>
                )}
              </div>

              {/* Поле ввода */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleTextQuestion()}
                    placeholder="Напишите вопрос..."
                    className="flex-1 px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={isProcessingQA}
                  />
                  <button
                    onClick={handleTextQuestion}
                    disabled={isProcessingQA || !textInput.trim()}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                  >
                    📤 Отправить
                  </button>
                </div>
                <div className="flex justify-center">
                  <VoiceRecorder
                    onRecordingComplete={handleRecordingComplete}
                    disabled={isProcessingQA}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Окошко ошибки распознавания речи */}
      {isSttErrorOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60"
          role="dialog"
          aria-modal="true"
          aria-label="Speech recognition error"
          onClick={() => setIsSttErrorOpen(false)}
        >
          <div
            className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-800 shadow-2xl p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start gap-3">
              <div className="text-2xl">⚠️</div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">Ошибка</h3>
                <p className="mt-2 text-gray-700 dark:text-gray-300">{sttErrorMessage}</p>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
                onClick={() => setIsSttErrorOpen(false)}
              >
                Ок
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Presentation;
