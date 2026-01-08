import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Нужен для статики вне /api (например, /audio/slide_01.wav)
export const API_ORIGIN = new URL(API_BASE_URL).origin;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Slide {
  id: number;
  title: string;
  content: string;
  tts?: string;
  notes?: string;
}

export interface SlidesResponse {
  total: number;
  slides: Slide[];
}

export interface QARequest {
  question: string;
  slide_context: string;
  slide_id: number;
}

export interface QAResponse {
  question: string;
  answer: string;
  audio: string;  // base64
  audio_format: string;
}

// Получить все слайды
export const fetchSlides = async (): Promise<SlidesResponse> => {
  const response = await api.get<SlidesResponse>('/slides');
  return response.data;
};

// Получить конкретный слайд
export const fetchSlide = async (slideId: number): Promise<Slide> => {
  const response = await api.get<Slide>(`/slides/${slideId}`);
  return response.data;
};

// Синтез речи (TTS)
export const textToSpeech = async (text: string): Promise<Blob> => {
  const response = await api.post(
    '/tts',
    { text, language: 'ky' },
    { responseType: 'blob' }
  );
  return response.data;
};

// Распознавание речи (STT)
export const speechToText = async (audioBlob: Blob): Promise<string> => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await api.post('/stt', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data.text;
};

// Вопросы и ответы
export const askQuestion = async (request: QARequest): Promise<QAResponse> => {
  const response = await api.post<QAResponse>('/qa', request);
  return response.data;
};

export default api;
