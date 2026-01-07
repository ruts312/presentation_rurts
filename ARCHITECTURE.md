# Диаграммы архитектуры проекта

## Архитектура компонентов

```mermaid
flowchart TB
    subgraph frontend [Frontend - React/TypeScript]
        UI[Слайды презентации]
        AudioPlayer[Аудио плеер]
        MicRecorder[Запись микрофона]
        StopButton[Кнопка СТОП]
    end
    
    subgraph backend [Backend - FastAPI/Python]
        SlidesAPI[API Слайдов]
        TTSAPI[TTS Service]
        STTAPI[STT Service]
        QAAPI[QA Service]
    end
    
    subgraph external [Внешние API]
        HuggingFace[Hugging Face TTS]
        Whisper[OpenAI Whisper]
        GPT4[OpenAI GPT-4]
    end
    
    UI --> SlidesAPI
    AudioPlayer --> TTSAPI
    MicRecorder --> STTAPI
    StopButton --> AudioPlayer
    
    TTSAPI --> HuggingFace
    STTAPI --> Whisper
    QAAPI --> GPT4
    QAAPI --> TTSAPI
```

## Последовательность взаимодействия

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant FE as Frontend
    participant BE as Backend
    participant HF as HuggingFace TTS
    participant W as Whisper
    participant GPT as GPT-4

    User->>FE: Открывает презентацию
    FE->>BE: Запрос слайдов
    BE-->>FE: Слайды с текстом
    FE->>BE: Запрос озвучки слайда
    BE->>HF: Текст на кыргызском
    HF-->>BE: Аудио файл
    BE-->>FE: Аудио
    FE->>FE: Воспроизведение
    
    User->>FE: Нажимает СТОП
    FE->>FE: Пауза аудио
    User->>FE: Говорит вопрос
    FE->>BE: Аудио вопроса
    BE->>W: Распознавание речи
    W-->>BE: Текст вопроса
    BE->>GPT: Вопрос + контекст
    GPT-->>BE: Ответ на кыргызском
    BE->>HF: Озвучка ответа
    HF-->>BE: Аудио ответа
    BE-->>FE: Текст + аудио ответа
    FE->>FE: Воспроизведение ответа
    User->>FE: Продолжить презентацию
```

## Структура проекта

```
presentation_ruts/
├── backend/
│   ├── main.py                 # FastAPI приложение
│   ├── config.py               # Конфигурация
│   ├── routers/
│   │   ├── slides.py           # API слайдов
│   │   ├── tts.py              # Text-to-Speech
│   │   ├── stt.py              # Speech-to-Text
│   │   └── qa.py               # Вопросы и ответы
│   ├── services/
│   │   ├── huggingface_tts.py  # Hugging Face TTS
│   │   ├── whisper_stt.py      # OpenAI Whisper
│   │   └── openai_qa.py        # GPT-4 интеграция
│   ├── data/
│   │   └── slides.json         # Контент презентации
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Presentation.tsx
│   │   │   ├── Slide.tsx
│   │   │   ├── AudioPlayer.tsx
│   │   │   ├── VoiceRecorder.tsx
│   │   │   └── QAPanel.tsx
│   │   ├── hooks/
│   │   │   ├── useAudio.ts
│   │   │   └── useVoiceRecorder.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── start_backend.bat          # Скрипт запуска backend
├── start_frontend.bat         # Скрипт запуска frontend
├── start_all.bat              # Запуск всего приложения
└── README.md
```
