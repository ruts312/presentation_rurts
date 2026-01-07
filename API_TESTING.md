# Тестирование API

## Тестовые запросы для проверки работы Backend

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{"status": "healthy"}
```

### 2. Получить все слайды

```bash
curl http://localhost:8000/api/slides
```

Ожидаемый ответ:
```json
{
  "total": 10,
  "slides": [...]
}
```

### 3. Получить конкретный слайд

```bash
curl http://localhost:8000/api/slides/1
```

### 4. Тест TTS сервиса

```bash
curl http://localhost:8000/api/tts/test
```

Ожидаемый ответ:
```json
{
  "status": "ready",
  "service": "HuggingFace TTS",
  "language": "Kyrgyz"
}
```

### 5. Тест STT сервиса

```bash
curl http://localhost:8000/api/stt/test
```

### 6. Тест QA сервиса

```bash
curl http://localhost:8000/api/qa/test
```

### 7. Генерация речи (TTS)

```bash
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Салам, бул тест\", \"language\": \"ky\"}" \
  --output test_audio.wav
```

### 8. Вопрос-ответ (требует OpenAI API ключ)

```bash
curl -X POST http://localhost:8000/api/qa \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Адам укуктары деген эмне?\", \"slide_context\": \"Адам укуктары - бул негизги укуктар\", \"slide_id\": 1}"
```

## Тестирование через браузер

### Swagger UI (рекомендуется)

Откройте в браузере:
```
http://localhost:8000/docs
```

Здесь вы можете:
- Просмотреть все доступные endpoints
- Протестировать каждый endpoint
- Увидеть схемы запросов и ответов
- Скачать OpenAPI спецификацию

### ReDoc (альтернатива)

```
http://localhost:8000/redoc
```

## PowerShell команды для Windows

### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

### Получить слайды
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/slides" -Method Get
```

### TTS запрос
```powershell
$body = @{
    text = "Салам, бул тест"
    language = "ky"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/tts" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body `
    -OutFile "test_audio.wav"
```

### QA запрос
```powershell
$body = @{
    question = "Адам укуктары деген эмне?"
    slide_context = "Адам укуктары контексти"
    slide_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/qa" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Python тестовый скрипт

Создайте файл `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health:", response.json())

def test_slides():
    response = requests.get(f"{BASE_URL}/api/slides")
    data = response.json()
    print(f"Всего слайдов: {data['total']}")

def test_tts():
    response = requests.post(
        f"{BASE_URL}/api/tts",
        json={"text": "Салам", "language": "ky"}
    )
    if response.status_code == 200:
        with open("test.wav", "wb") as f:
            f.write(response.content)
        print("TTS аудио сохранено в test.wav")

def test_qa():
    response = requests.post(
        f"{BASE_URL}/api/qa",
        json={
            "question": "Адам укуктары деген эмне?",
            "slide_context": "Адам укуктары контексти",
            "slide_id": 1
        }
    )
    data = response.json()
    print("Вопрос:", data["question"])
    print("Ответ:", data["answer"])

if __name__ == "__main__":
    print("Тестирование API...")
    test_health()
    test_slides()
    test_tts()
    # test_qa()  # Раскомментируйте если есть OpenAI ключ
```

Запустите:
```bash
python test_api.py
```

## JavaScript тестовый скрипт (Node.js)

Создайте файл `test_api.js`:

```javascript
const axios = require('axios');
const fs = require('fs');

const BASE_URL = 'http://localhost:8000';

async function testHealth() {
    const response = await axios.get(`${BASE_URL}/health`);
    console.log('Health:', response.data);
}

async function testSlides() {
    const response = await axios.get(`${BASE_URL}/api/slides`);
    console.log(`Всего слайдов: ${response.data.total}`);
}

async function testTTS() {
    const response = await axios.post(
        `${BASE_URL}/api/tts`,
        { text: 'Салам', language: 'ky' },
        { responseType: 'arraybuffer' }
    );
    
    fs.writeFileSync('test.wav', response.data);
    console.log('TTS аудио сохранено в test.wav');
}

async function testQA() {
    const response = await axios.post(`${BASE_URL}/api/qa`, {
        question: 'Адам укуктары деген эмне?',
        slide_context: 'Адам укуктары контексти',
        slide_id: 1
    });
    
    console.log('Вопрос:', response.data.question);
    console.log('Ответ:', response.data.answer);
}

async function runTests() {
    console.log('Тестирование API...');
    await testHealth();
    await testSlides();
    await testTTS();
    // await testQA();  // Раскомментируйте если есть OpenAI ключ
}

runTests().catch(console.error);
```

Запустите:
```bash
node test_api.js
```

## Ожидаемые статус коды

- `200 OK` - Успешный запрос
- `404 Not Found` - Ресурс не найден (неправильный ID слайда)
- `422 Unprocessable Entity` - Ошибка валидации данных
- `500 Internal Server Error` - Ошибка сервера (проблема с API ключом и т.д.)

## Логирование

Backend логи можно увидеть в терминале где запущен `python main.py`.

Для более детального логирования можно добавить в `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
