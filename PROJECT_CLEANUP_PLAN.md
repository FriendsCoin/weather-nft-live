# 🧹 Project Cleanup & Organization Plan

## 📁 Новая структура проекта

### 🚀 **CORE (активные файлы)**
```
weather-nft-live/
├── 📊 CORE SERVICES
│   ├── simple-test-server.js          # AI Backend (3006)
│   ├── blockchain-service.js          # Blockchain Service (3007)
│   ├── admin-backend.js               # Admin API (3008)
│   ├── simple-frontend-server.js      # Frontend Server (8081)
│   └── sd-pytorch-integration.py      # Real SD AI (8000)
│
├── 🌐 WEB INTERFACES
│   ├── marketplace-inspired.html      # Main page
│   ├── admin-futuristic.html         # Admin panel (with terminal)
│   └── test-purchase.html            # Purchase flow
│
├── 🔧 MANAGEMENT
│   ├── restart-all.sh / .bat         # Start all services
│   ├── stop-all.sh                   # Stop all services
│   ├── status.sh                     # Check status
│   └── switch-to-real-sd.sh          # Switch to real SD AI
│
├── 📝 DOCUMENTATION
│   ├── SD_AI_INTEGRATION_GUIDE.md    # SD AI setup
│   ├── MANAGEMENT_SCRIPTS.md         # Scripts usage
│   └── CONNECT_REAL_SD.md            # Real SD connection
│
├── 🐳 DOCKER
│   ├── docker-compose.dev.yml        # Development setup
│   └── Dockerfile.sd-dev             # SD AI container
│
└── 📦 CONFIG
    ├── package.json                  # Dependencies
    ├── requirements-pytorch.txt      # Python deps
    └── install-sd-api-deps.bat       # Windows installer
```

### 📦 **ARCHIVE (переместить в archive/)**
```
archive/
├── 📚 docs-old/                      # Старая документация
│   ├── AI_ARCHITECTURE_PROPOSAL.md
│   ├── AI_PRODUCTION_READY.md
│   ├── CURRENT_STATUS.md
│   ├── FINAL_PRODUCTION_STATUS.md
│   ├── PRODUCTION_READY.md
│   └── ... (все старые .md файлы)
│
├── 🧪 experimental/                  # Экспериментальные решения
│   ├── advanced-ai-engine.js
│   ├── production-ai-server.js
│   ├── production-server.js
│   ├── pytorch-ai-engine.py
│   ├── pytorch-api-integration.py
│   └── real-ai-engine.js
│
├── 🎨 frontend-alternatives/         # Альтернативные фронтенды
│   ├── simple-frontend.html
│   ├── futuristic-main.html
│   ├── animated-events.html
│   ├── working-frontend.html
│   └── navigation.html
│
├── 🔗 proxy-servers/                 # Прокси решения
│   ├── frontend-proxy.js
│   ├── proxy-server.js
│   ├── quick-proxy.js
│   ├── simple-proxy.js
│   └── redirect-proxy.js
│
├── 🧪 test-files/                    # Тестовые файлы
│   ├── test-ai-algorithms.js
│   ├── test-ai-server.js
│   ├── test-api.html
│   ├── test-backend.js
│   └── ... (все test-*.js)
│
├── 🏗️ build-scripts/                 # Старые скрипты сборки
│   ├── check-services.bat
│   ├── clean-rebuild.bat
│   ├── fix-backend.bat
│   └── setup-production.js
│
└── 🗃️ legacy/                        # Устаревшие решения
    ├── backend/                       # React backend
    ├── frontend/                      # React frontend
    ├── legacy-algorithms/
    ├── smart-contracts/
    └── bridge-3004.js
```

## 🎯 **Hosting Options для песочницы**

### 🌟 **Рекомендуемые платформы:**

#### 1. **Vercel** (Frontend + API)
- ✅ **Бесплатный план**: Отлично для демо
- ✅ **Автодеплой**: Из GitHub
- ✅ **Serverless**: Node.js API routes
- ❌ **Ограничения**: Нет GPU, ограниченное время выполнения

```bash
# Развертывание
npm i -g vercel
vercel --prod
```

#### 2. **Railway** (Full Stack)
- ✅ **GPU Support**: Доступны GPU инстансы
- ✅ **Docker**: Полная поддержка контейнеров
- ✅ **Databases**: PostgreSQL, Redis включены
- 💰 **Цена**: $5/месяц базовый план

```yaml
# railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile.sd-dev"
```

#### 3. **Render** (Docker + GPU)
- ✅ **Free Tier**: Для простых приложений
- ✅ **GPU Support**: Платные планы с GPU
- ✅ **Auto-deploy**: Из GitHub
- 💰 **GPU**: От $10/месяц

#### 4. **Google Cloud Run** (Serverless)
- ✅ **Serverless**: Платите только за использование
- ✅ **GPU Support**: T4, V100 доступны
- ✅ **Scale to Zero**: Экономия на демо
- 💰 **GPU**: ~$0.35/час T4

#### 5. **Hugging Face Spaces** (AI специализированный)
- ✅ **Бесплатный GPU**: Для AI моделей
- ✅ **Gradio/Streamlit**: Готовые UI
- ✅ **Model Hub**: Интеграция с моделями
- ❌ **Ограничения**: Только AI интерфейсы

## 🧠 **Варианты для SD AI среды:**

### 🏠 **Локальное решение (Hybrid)**
```
┌─────────────────┐    ┌──────────────────┐
│   Cloud Web     │    │   Local SD AI    │
│   (Frontend)    │◄──►│   (Your PC)      │
│   - Admin Panel │    │   - PyTorch      │
│   - API Gateway │    │   - CUDA RTX2080 │
└─────────────────┘    └──────────────────┘
```

**Плюсы:**
- ✅ Используете вашу RTX 2080
- ✅ Полная мощность SD среды
- ✅ Бесплатно для GPU части

**Реализация:**
1. SD AI на вашем компе с ngrok
2. Веб интерфейс в облаке
3. Webhook коннекция

```bash
# На вашем ПК
ngrok http 8000
# Получаете URL типа: https://abc123.ngrok.io
```

### ☁️ **Полностью облачное решение**

#### **Google Colab Pro** (Бесплатный GPU)
```python
# В Colab
!git clone https://github.com/your-repo/weather-nft
!pip install -r requirements-pytorch.txt
# Запускаете SD AI в Colab
```

#### **RunPod** (Специализированно для AI)
- 🔥 **RTX 4090**: $0.34/час
- 🔥 **A100**: $1.10/час
- ✅ **Предустановленный PyTorch**
- ✅ **Jupyter + SSH доступ**

#### **Vast.ai** (Дешевые GPU)
- 💰 **RTX 3080**: $0.15/час
- 💰 **RTX 4090**: $0.25/час
- ✅ **Docker support**
- ✅ **SSH доступ**

## 🎯 **Рекомендуемая архитектура для демо:**

### **Вариант 1: Hybrid (Рекомендуемый)**
```
Frontend + API → Vercel (бесплатно)
SD AI Server → Ваш ПК + ngrok (бесплатно)
Database → Supabase (бесплатно)
```

**Стоимость**: $0/месяц

### **Вариант 2: Cloud Medium**
```
Frontend + API → Railway ($5/месяц)
SD AI Server → RunPod RTX4090 (по требованию ~$8/день)
Database → Railway PostgreSQL (включено)
```

**Стоимость**: ~$25/месяц при активном использовании

### **Вариант 3: Cloud Premium**
```
Frontend → Vercel (бесплатно)
Backend API → Google Cloud Run ($10/месяц)
SD AI → Google Cloud Run GPU T4 ($25/месяц)
Database → Google Cloud SQL ($15/месяц)
```

**Стоимость**: ~$50/месяц

## 📋 **План действий:**

1. **Создать archive/ папку** ✅
2. **Переместить неиспользуемые файлы** ✅
3. **Очистить root папку** ✅
4. **Создать deployment конфиги** ✅
5. **Выбрать hosting платформу** ✅
6. **Настроить CI/CD** ✅

## 🚀 **Следующие шаги:**

1. **Хотите начать с Hybrid решения?** (Vercel + ваш ПК)
2. **Или предпочитаете полностью облачное?** (Railway/RunPod)
3. **Какой бюджет готовы тратить?** ($0, $25, $50+/месяц)

Что выберете? 🤔