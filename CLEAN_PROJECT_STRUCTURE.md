# 🧹 Clean Project Structure

## 📁 Актуальная структура (Core Files)

```
weather-nft-live/
├── 🚀 CORE SERVICES
│   ├── simple-test-server.js          # AI Backend (port 3006)
│   ├── blockchain-service.js          # Blockchain (port 3007)
│   ├── admin-backend.js               # Admin API (port 3008)
│   ├── simple-frontend-server.js      # Frontend (port 8081)
│   ├── sd-pytorch-integration.py      # Real SD AI (port 8000)
│   └── simple-sd-ai-mock.py           # Mock SD AI (fallback)
│
├── 🌐 WEB INTERFACES (3 файла)
│   ├── marketplace-inspired.html      # Main page
│   ├── admin-futuristic.html         # Admin panel + terminal
│   └── test-purchase.html            # Purchase flow
│
├── 🔧 MANAGEMENT SCRIPTS (8 файлов)
│   ├── restart-all.sh / .bat         # Start all services
│   ├── stop-all.sh                   # Stop all services
│   ├── status.sh                     # Check status
│   ├── switch-to-real-sd.sh          # Switch SD AI modes
│   ├── test-real-sd.sh               # Test SD AI connection
│   ├── start-pytorch-ai.sh/.bat      # Start PyTorch AI
│   └── start-sd-ai.sh                # Start SD AI
│
├── 📝 ESSENTIAL DOCS (6 файлов)
│   ├── README.md                      # Main documentation
│   ├── SD_AI_INTEGRATION_GUIDE.md    # SD AI setup
│   ├── MANAGEMENT_SCRIPTS.md         # Scripts usage
│   ├── CONNECT_REAL_SD.md            # Real SD connection
│   ├── DOCKER_QUICK_START.md         # Docker usage
│   └── PRODUCTION_ARCHITECTURE.md    # Production info
│
├── 🐳 DEPLOYMENT
│   ├── docker-compose.dev.yml        # Docker development
│   ├── Dockerfile.sd-dev             # SD AI container
│   └── install-sd-api-deps.bat       # Windows installer
│
├── 📦 CONFIG
│   ├── package.json                  # Node.js dependencies
│   ├── requirements-pytorch.txt      # Python dependencies
│   └── requirements.txt              # Basic Python deps
│
├── 📊 LOGS
│   └── logs/                         # Runtime logs
│
└── 📦 ARCHIVE
    ├── docs-old/                     # 15 старых .md файлов
    ├── experimental/                 # 7 экспериментальных AI
    ├── frontend-alternatives/        # 7 альтернативных UI
    ├── proxy-servers/               # 6 прокси решений
    ├── test-files/                  # 8 тестовых файлов
    ├── build-scripts/               # 7 старых скриптов
    └── legacy/                      # React backend/frontend
```

## 📊 Статистика очистки

### ✅ **Оставлено (Core)**
- **Сервисы**: 6 файлов
- **Web UI**: 3 файла
- **Скрипты**: 8 файлов
- **Документация**: 6 файлов
- **Deploy**: 3 файла
- **Итого**: **26 основных файлов**

### 📦 **Архивировано**
- **Старая документация**: 15 файлов
- **Экспериментальные AI**: 7 файлов
- **Альтернативные UI**: 7 файлов
- **Прокси сервера**: 6 файлов
- **Тестовые файлы**: 8 файлов
- **Старые скрипты**: 7 файлов
- **Legacy проекты**: React backend + frontend
- **Итого**: **50+ архивных файлов**

## 🎯 **Что используется сейчас**

### **Для разработки:**
```bash
./restart-all.sh                    # Запуск всех сервисов
./status.sh                         # Проверка статуса
./stop-all.sh                       # Остановка
```

### **Веб интерфейсы:**
- http://localhost:8081/ → marketplace-inspired.html
- http://localhost:8081/admin-futuristic.html → админ панель
- http://localhost:8081/test-purchase.html → покупки

### **SD AI:**
```bash
python sd-pytorch-integration.py --server  # Реальный SD AI
# или
./start-sd-ai.sh --server                  # Через скрипт
```

## 🚀 **Готово к деплою**

Проект теперь организован и готов для:
1. **Local development** ✅
2. **Docker deployment** ✅  
3. **Cloud hosting** ✅
4. **Production scaling** ✅

### **Размер проекта:**
- **Core**: ~2MB (без node_modules)
- **Archive**: ~50MB (полная история)
- **Total**: ~52MB