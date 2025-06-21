# 🧠 SD AI Integration Guide для WeatherNFT

## 🎉 Отличные новости!

Ваша SD среда с PyTorch и CUDA работает идеально! Мы видим:

- ✅ **SD Environment detected: SD**
- ✅ **PyTorch 2.1.2+cu118 available**  
- ✅ **CUDA available: NVIDIA GeForce RTX 2080**
- ✅ **5 AI algorithms loaded**

## 🔧 Быстрая настройка для полной интеграции

### 1. Установите API зависимости

Выполните в Windows PowerShell/CMD:

```cmd
# Переключитесь в SD среду
conda activate SD

# Перейдите в папку проекта
cd E:\SDfu-master\SDfu-masterOSC\weather-nft-live

# Установите API зависимости
pip install fastapi
pip install "uvicorn[standard]"
pip install aiohttp
pip install python-multipart
```

**Или запустите готовый скрипт:**
```cmd
install-sd-api-deps.bat
```

### 2. Запустите реальный SD AI сервер

```cmd
# В активированной SD среде
python sd-pytorch-integration.py --server
```

Вы должны увидеть:
```
🚀 Starting API server on http://localhost:8000
📝 API docs: http://localhost:8000/docs
INFO:     Started server process [PID]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Переключите админ панель на реальный SD AI

Перейдите в админ панель: http://localhost:8081/admin-futuristic.html

1. **Откройте терминал** (зеленая кнопка справа внизу)
2. **Выполните команду**: `sd-info`
3. **Убедитесь**, что показывает "Real SD AI Active!"

## 🚀 Использование

### В админ панели

**Терминальные команды:**
- `sd-info` - Подробная информация о SD AI
- `test-ai` - Тест предсказания с реальным PyTorch
- `status` - Статус всех сервисов
- `start-sd` - Инструкции по запуску SD AI

**Быстрые кнопки:**
- **SD Info** - Детали SD окружения
- **Test AI** - Тест с реальными моделями
- **Start SD AI** - Помощь по запуску

### Вкладка PyTorch AI

1. **Deploy PyTorch** - Проверит подключение к реальному SD AI
2. **Test Prediction** - Запустит предсказание с вашими PyTorch моделями
3. **View Status** - Покажет детальный статус SD среды

## 🔍 Отличия Real vs Mock

### Mock SD AI (по умолчанию):
- ❌ SD Environment: Not detected
- ❌ PyTorch: Fallback mode  
- 🎭 Простые математические модели
- 🚀 Быстрый запуск для демо

### Real SD AI (ваша среда):
- ✅ SD Environment: Active (SD)
- ✅ PyTorch: Available (2.1.2+cu118)
- 🔥 CUDA: NVIDIA GeForce RTX 2080
- 🧠 Настоящие LSTM/CNN/Transformer модели
- 🎯 Высокая точность предсказаний

## 📊 Мониторинг

### Проверка статуса SD AI:
```bash
curl http://localhost:8000/health
```

### Тест предсказания:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature": 35, "humidity": 85, "pressure": 995, "wind_speed": 45}'
```

### API документация:
http://localhost:8000/docs

## 🔄 Переключение между режимами

### Перейти на Real SD AI:
```bash
./switch-to-real-sd.sh
```

### Вернуться к Mock (для демо):
```bash
# Остановите SD AI сервер (Ctrl+C)
# Перезапустите все сервисы
./restart-all.sh
```

## 🐛 Troubleshooting

### "uvicorn not defined" ошибка:
```cmd
conda activate SD
pip install "uvicorn[standard]"
```

### "FastAPI not available":
```cmd
pip install fastapi
```

### Порт 8000 занят:
```cmd
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Linux
lsof -i :8000
kill <PID>
```

### Проверка CUDA:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name()}")
```

## 🏆 Production Tips

1. **Автозапуск**: Добавьте SD AI в автозагрузку Windows
2. **Мониторинг**: Используйте админ панель для отслеживания
3. **Логи**: Проверяйте `logs/sd-ai.log` при проблемах
4. **Масштабирование**: Используйте Docker для множественных инстансов

## 🎯 Результат

После настройки у вас будет:

- 🧠 **Реальный PyTorch AI** с CUDA ускорением
- 🎯 **5 продвинутых алгоритмов** для предсказания погоды
- 🖥️ **Полная интеграция** с админ панелью
- 📊 **Мониторинг в реальном времени**
- 🔄 **Легкое переключение** между режимами

Ваш WeatherNFT проект теперь использует настоящий AI! 🔥