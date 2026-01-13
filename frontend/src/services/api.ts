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
  image_url?: string;
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
  language?: string;
}

export interface QAResponse {
  question: string;
  answer: string;
  audio: string;  // base64
  audio_format: string;
}

// Получить все слайды
export const fetchSlides = async (language: string = 'ru', deck?: string): Promise<SlidesResponse> => {
  const response = await api.get<SlidesResponse>('/slides', {
    params: { lang: language, deck },
  });
  return response.data;
};

// Получить конкретный слайд
export const fetchSlide = async (slideId: number): Promise<Slide> => {
  const response = await api.get<Slide>(`/slides/${slideId}`);
  return response.data;
};

// Синтез речи (TTS)
export const textToSpeech = async (text: string, language: string = 'ru'): Promise<Blob> => {
  const response = await api.post(
    '/tts',
    { text, language },
    { responseType: 'blob' }
  );
  return response.data;
};

// Распознавание речи (STT)
export const speechToText = async (audioBlob: Blob, language: string = 'ru'): Promise<string> => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  formData.append('language', language);

  try {
    const response = await api.post('/stt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.text;
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const detail = (err.response?.data as any)?.detail;
      throw new Error(detail || err.message || 'STT error');
    }
    throw err;
  }
};

// Вопросы и ответы
export const askQuestion = async (request: QARequest): Promise<QAResponse> => {
  const response = await api.post<QAResponse>('/qa', request);
  return response.data;
};

export default api;
