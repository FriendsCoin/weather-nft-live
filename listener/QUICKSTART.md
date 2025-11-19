# Quick Start - THE LISTENER 🧘

**5-минутный старт** / **5-Minute Setup**

Быстрое руководство по запуску и первой медитации.
Quick guide to get started with your first meditation session.

---

## 📋 Prerequisites / Предварительные требования

- Python 3.8+
- Muse S headband (для записи EEG / for EEG recording)
- CUDA-capable GPU (optional, для ускорения / for acceleration)

---

## 🚀 Step 1: Installation / Установка

```bash
# Clone repository / Клонировать репозиторий
git clone https://github.com/yourusername/weather-nft-live.git
cd weather-nft-live/listener

# Install dependencies / Установить зависимости
pip install -r requirements.txt

# Optional: GPU support / Опционально: поддержка GPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

## ✅ Step 2: Health Check / Проверка системы

Проверьте готовность системы:
Check if your system is ready:

```bash
python scripts/health_check.py
```

**Expected output / Ожидаемый вывод:**
```
🏥 THE LISTENER - Health Check
═════════════════════════════════════════
✓ Python Version       3.10.12
✓ Required Packages    All installed
✓ Config Module        Loaded
✓ Database             Connected (0 sessions)
✓ GPU                  NVIDIA RTX 2080 (8.0 GB)
⚠ Muse S Stream        No EEG stream found
```

**Решение проблем / Troubleshooting:**
- ❌ Missing packages → `pip install -r requirements.txt`
- ❌ No Muse S stream → See Step 3
- ❌ GPU not detected → Check CUDA installation

---

## 🎧 Step 3: Connect Muse S / Подключение Muse S

### 3.1 Установка muselsl / Install muselsl

```bash
pip install muselsl
```

### 3.2 Сопряжение / Pairing

**На Linux:**
```bash
# Find Muse S / Найти Muse S
bluetoothctl
> scan on
> connect XX:XX:XX:XX:XX:XX  # Your Muse MAC address
```

**На macOS/Windows:**
Use Bluetooth settings in system preferences

### 3.3 Start streaming / Запуск трансляции

```bash
muselsl stream
```

**Expected output:**
```
Connecting to Muse-XXXX...
Connected!
Streaming...
```

**Оставьте это окно открытым!** / **Keep this window open!**

---

## 🧘 Step 4: First Meditation Session / Первая сессия

В **новом терминале** / In a **new terminal**:

```bash
# Record 5-minute session / Запись 5-минутной сессии
python scripts/meditation_session.py --duration 300 --name "My First Session"
```

**Что происходит / What happens:**
1. Connects to Muse S EEG stream
2. Records brain activity for 5 minutes
3. Extracts features from EEG
4. Saves session to `data/sessions/session_YYYYMMDD_HHMMSS.h5`

**During meditation / Во время медитации:**
- Sit comfortably / Сядьте удобно
- Close your eyes / Закройте глаза
- Focus on breath / Сфокусируйтесь на дыхании
- The script will auto-stop after 5 minutes

---

## 📊 Step 5: View Your Results / Просмотр результатов

### 5.1 Quick Stats / Быстрая статистика

```bash
python scripts/quick_stats.py
```

**Output / Вывод:**
```
📊 Session Summary:
   ID:            session_20241119_103000
   Duration:      5m 0s
   Depth:         72.3 / 100  ⭐⭐⭐
   Quality:       89.1 / 100  ✨✨✨
   Alpha+:        +0.45       (good!)
   State:         Relaxed focus
```

### 5.2 Visualization / Визуализация

```bash
python scripts/visualize.py --session session_20241119_103000
```

Opens interactive plots:
- Brain wave bands (Alpha, Beta, Theta, Delta)
- Meditation depth over time
- Signal quality
- Spectrogram

### 5.3 Web Dashboard / Веб-дашборд

```bash
python scripts/start_dashboard.py
```

Open http://localhost:8000 in browser

**Features / Возможности:**
- View all sessions
- Compare sessions
- Progress tracking
- Export data

---

## 🎯 Step 6: Advanced Features / Продвинутые функции

### 6.1 Real-Time Neurofeedback / Нейрофидбек в реальном времени

```bash
# Console-only mode / Режим консоли
python scripts/live_neurofeedback.py

# With browser visualization / С визуализацией в браузере
python scripts/live_neurofeedback.py --save-client
# Then open test_client.html
```

### 6.2 Train VAE Model / Обучение VAE модели

After recording 10+ sessions:

```bash
# Train on all sessions / Обучить на всех сессиях
python scripts/train.py --sessions-dir data/sessions --epochs 100

# With GPU acceleration / С ускорением GPU
python scripts/train.py --sessions-dir data/sessions --epochs 100 --device cuda
```

### 6.3 3D Visualization / 3D визуализация

After training VAE model:

```bash
# Create 3D latent space / Создать 3D латентное пространство
python scripts/create_3d_viz.py --latent-space

# Journey through meditation / Путешествие по медитациям
python scripts/create_3d_viz.py --journey

# All visualizations / Все визуализации
python scripts/create_3d_viz.py --all
```

### 6.4 Generate Multimedia / Создание мультимедиа

```bash
# AI-generated art from session / Искусство из сессии
python scripts/generate_multimedia.py --session session_001 --image

# Music generation / Генерация музыки
python scripts/generate_multimedia.py --session session_001 --audio

# AI interpretation / AI интерпретация
python scripts/generate_multimedia.py --session session_001 --llm

# Everything / Всё сразу
python scripts/generate_multimedia.py --session session_001 --all
```

### 6.5 Batch Processing / Пакетная обработка

```bash
# Process all sessions in parallel (10x faster!) / Параллельная обработка (в 10 раз быстрее!)
python scripts/batch_process.py --sessions-dir data/sessions --workers 8

# With VAE encoding / С VAE кодированием
python scripts/batch_process.py --sessions-dir data/sessions --vae-model models/vae_model.pt
```

---

## 🔧 Common Commands / Частые команды

### Session Management / Управление сессиями

```bash
# List all sessions / Список всех сессий
python scripts/quick_stats.py --list

# Compare two sessions / Сравнить две сессии
python scripts/compare_sessions.py session_001 session_010

# Check data integrity / Проверить целостность данных
python scripts/check_integrity.py --sessions-dir data/sessions --verbose

# Migrate to database / Миграция в БД
python src/database/migration.py --sessions-dir data/sessions --database sqlite:///data/listener.db
```

### Export & Backup / Экспорт и бэкап

```bash
# Export all sessions to CSV / Экспорт в CSV
python scripts/generate_exports.py --csv --output-dir exports

# Create complete backup / Полный бэкап
python scripts/generate_exports.py --archive --output-dir backups

# Generate PDF report / Создать PDF отчёт
python scripts/generate_exports.py --report --output-dir reports
```

### System / Система

```bash
# Health check / Проверка системы
python scripts/health_check.py --verbose

# Test GPU setup / Тест GPU
python scripts/test_gpu_setup.py

# Upgrade database / Обновить БД
python scripts/upgrade_database.py --database sqlite:///data/listener.db
```

---

## 🎮 Biofeedback Game / Биофидбек игра

```bash
# Launch visualization game / Запуск игры
python scripts/biofeedback_game.py
```

**Controls / Управление:**
- Just meditate! / Просто медитируйте!
- Deeper meditation = more visual effects
- Press ESC to quit

**Visual effects respond to:**
- Meditation depth → particle speed
- Alpha waves → color warmth
- Signal quality → clarity

---

## 📚 Next Steps / Следующие шаги

1. **Record more sessions** (aim for 10+) to train VAE
2. **Explore patterns** using 3D visualization
3. **Track progress** with session comparison
4. **Generate art** from your meditation states
5. **Share insights** (optional, anonymous)

---

## ⚙️ Configuration / Конфигурация

### Environment Variables / Переменные окружения

Create `.env` file:

```bash
# API Keys (optional, для AI генерации / for AI generation)
ANTHROPIC_API_KEY=sk-ant-xxxxx
REPLICATE_API_TOKEN=r8_xxxxx

# Paths
LISTENER_DATA_DIR=/custom/path/to/data
LISTENER_DATABASE_URL=sqlite:////custom/path/listener.db

# Performance
LISTENER_USE_GPU=true
LISTENER_BATCH_SIZE=32
```

### Custom Settings / Пользовательские настройки

Edit `src/config.py` for advanced configuration:
- Sampling rates
- Feature extraction parameters
- Model architectures
- Visualization themes

---

## 🐛 Troubleshooting / Решение проблем

### Muse S не подключается / Muse S not connecting

```bash
# Check Bluetooth / Проверить Bluetooth
bluetoothctl
> devices  # Should show Muse-XXXX

# Restart muselsl
pkill -f muselsl
muselsl stream
```

### CUDA Out of Memory / Переполнение памяти CUDA

```bash
# Reduce batch size / Уменьшить batch size
python scripts/train.py --batch-size 16  # Default: 32

# Or use CPU / Или использовать CPU
python scripts/train.py --device cpu
```

### Slow 3D Visualization / Медленная 3D визуализация

```bash
# Clear UMAP cache / Очистить кэш UMAP
rm -rf data/cache/umap/*

# Use t-SNE instead / Использовать t-SNE
python scripts/create_3d_viz.py --latent-space --method tsne
```

### Session quality low / Низкое качество сессии

**Tips / Советы:**
- Wet the Muse S sensors / Смочите датчики Muse S
- Ensure tight fit / Убедитесь в плотной посадке
- Minimize jaw movement / Минимизируйте движение челюсти
- Reduce eye movement / Снизьте движение глаз
- Use in quiet environment / Используйте в тихой обстановке

---

## 📖 Further Reading / Дополнительная информация

- **Full Documentation:** [README.md](README.md)
- **Architecture:** [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md)
- **Migration Guide:** [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Improvements:** [IMPROVEMENTS_NEXT.md](IMPROVEMENTS_NEXT.md)
- **API Docs:** (coming soon)

---

## 💬 Community / Сообщество

- **GitHub Issues:** Report bugs / Сообщить об ошибке
- **Discussions:** Share insights / Поделиться опытом
- **Wiki:** Community guides / Руководства сообщества

---

## ✨ You're Ready! / Вы готовы!

Congratulations! You've completed the quick start.
Поздравляем! Вы завершили быстрый старт.

**Happy meditating!** 🧘‍♀️🧘‍♂️

**Приятной медитации!** 🙏
