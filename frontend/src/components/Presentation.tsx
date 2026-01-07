import React, { useState, useEffect } from 'react';
import Slide from './Slide';
import AudioPlayer from './AudioPlayer';
import VoiceRecorder from './VoiceRecorder';
import QAPanel from './QAPanel';
import { fetchSlides, textToSpeech, speechToText, askQuestion, Slide as SlideType } from '../services/api';

const Presentation: React.FC = () => {
  const [slides, setSlides] = useState<SlideType[]>([]);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Состояние для режима вопросов
  const [isQAMode, setIsQAMode] = useState(false);
  const [questionText, setQuestionText] = useState('');
  const [answerText, setAnswerText] = useState('');
  const [answerAudio, setAnswerAudio] = useState<Blob | null>(null);
  const [isProcessingQA, setIsProcessingQA] = useState(false);

  // Загрузка слайдов при монтировании
  useEffect(() => {
    loadSlides();
  }, []);

  // Загрузка аудио при смене слайда
  useEffect(() => {
    if (slides.length > 0 && !isQAMode) {
      loadSlideAudio(slides[currentSlideIndex]);
    }
  }, [currentSlideIndex, slides, isQAMode]);

  const loadSlides = async () => {
    try {
      setIsLoading(true);
      const data = await fetchSlides();
      setSlides(data.slides);
      setError(null);
    } catch (err) {
      setError('Ошибка загрузки слайдов');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSlideAudio = async (slide: SlideType) => {
    try {
      const audio = await textToSpeech(slide.content);
      setAudioBlob(audio);
    } catch (err) {
      console.error('Error loading audio:', err);
    }
  };

  const nextSlide = () => {
    if (currentSlideIndex < slides.length - 1) {
      setCurrentSlideIndex(currentSlideIndex + 1);
      setIsQAMode(false);
    }
  };

  const previousSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
      setIsQAMode(false);
    }
  };

  const handleStopPresentation = () => {
    setIsQAMode(true);
    setQuestionText('');
    setAnswerText('');
    setAnswerAudio(null);
  };

  const handleRecordingComplete = async (recordedAudioBlob: Blob) => {
    setIsProcessingQA(true);
    
    try {
      // 1. Распознать речь
      const transcription = await speechToText(recordedAudioBlob);
      setQuestionText(transcription);

      // 2. Получить ответ от GPT
      const currentSlide = slides[currentSlideIndex];
      const response = await askQuestion({
        question: transcription,
        slide_context: currentSlide.content,
        slide_id: currentSlide.id,
      });

      setAnswerText(response.answer);

      // 3. Конвертировать base64 аудио в Blob
      const audioData = atob(response.audio);
      const audioArray = new Uint8Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i);
      }
      const answerBlob = new Blob([audioArray], { type: 'audio/wav' });
      setAnswerAudio(answerBlob);

    } catch (err) {
      console.error('Error processing question:', err);
      setAnswerText('Извините, произошла ошибка при обработке вашего вопроса.');
    } finally {
      setIsProcessingQA(false);
    }
  };

  const handleCloseQA = () => {
    setIsQAMode(false);
    setQuestionText('');
    setAnswerText('');
    setAnswerAudio(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка презентации...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <p className="text-xl font-bold mb-2">Ошибка</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (slides.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600 dark:text-gray-400">Нет доступных слайдов</p>
      </div>
    );
  }

  const currentSlide = slides[currentSlideIndex];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Заголовок презентации */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Адам укуктары
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Интерактивная презентация на кыргызском языке
          </p>
        </div>

        {/* Слайд */}
        <div className="mb-8">
          <Slide slide={currentSlide} />
        </div>

        {/* Аудио плеер */}
        {!isQAMode && audioBlob && (
          <div className="mb-6">
            <AudioPlayer audioBlob={audioBlob} autoPlay={true} />
          </div>
        )}

        {/* Навигация */}
        <div className="flex justify-between items-center mb-8">
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
            <p className="text-gray-700 dark:text-gray-300 font-semibold">
              {currentSlideIndex + 1} / {slides.length}
            </p>
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

        {/* Кнопка СТОП */}
        {!isQAMode && (
          <div className="text-center mb-8">
            <button
              onClick={handleStopPresentation}
              className="bg-red-600 hover:bg-red-700 text-white px-12 py-4 rounded-lg font-bold text-xl transition-colors shadow-lg"
            >
              СТОП - Задать вопрос
            </button>
          </div>
        )}

        {/* Режим вопросов */}
        {isQAMode && (
          <div className="space-y-6">
            {!questionText && !answerText && (
              <VoiceRecorder
                onRecordingComplete={handleRecordingComplete}
                disabled={isProcessingQA}
              />
            )}

            {(questionText || answerText || isProcessingQA) && (
              <QAPanel
                question={questionText}
                answer={answerText}
                audioBlob={answerAudio}
                isLoading={isProcessingQA}
                onClose={handleCloseQA}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Presentation;
