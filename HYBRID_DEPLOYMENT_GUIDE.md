# 🌐 Hybrid Deployment Guide - Облако + Ваш ПК

## 🎯 Рекомендуемая архитектура (Бесплатно!)

```
┌─────────────────────┐    ┌─────────────────────┐
│     Vercel Cloud    │    │    Ваш ПК (Local)   │
│   (Бесплатно)       │    │   (RTX 2080)        │
├─────────────────────┤    ├─────────────────────┤
│ • Frontend UI       │◄──►│ • SD AI Server      │
│ • Admin Panel       │    │ • PyTorch Models    │
│ • API Gateway       │    │ • CUDA Acceleration │
│ • Static Files      │    │ • Real ML Power     │
└─────────────────────┘    └─────────────────────┘
```

## 🚀 Пошаговое развертывание

### 1. **Подготовка GitHub репозитория**

```bash
# Создайте GitHub репозиторий
git init
git add .
git commit -m "Clean WeatherNFT project structure"
git remote add origin https://github.com/your-username/weather-nft-live.git
git push -u origin main
```

### 2. **Настройка локального SD AI сервера**

На вашем ПК создайте файл `start-sd-local.bat`:
```cmd
@echo off
echo 🧠 Starting Local SD AI Server for Cloud Integration
echo =====================================================

REM Activate SD environment
call conda activate SD

REM Navigate to project
cd /d "E:\SDfu-master\SDfu-masterOSC\weather-nft-live"

REM Start SD AI server
echo Starting SD AI server on port 8000...
python sd-pytorch-integration.py --server

pause
```

### 3. **Настройка ngrok (бесплатный туннель)**

```bash
# Установите ngrok
# Windows: скачайте с https://ngrok.com/download
# Или через chocolatey: choco install ngrok

# Запустите туннель
ngrok http 8000

# Получите URL типа: https://abc123.ngrok.io
```

### 4. **Deploy на Vercel**

```bash
# Установите Vercel CLI
npm i -g vercel

# В папке проекта
vercel

# Настройте environment variables в Vercel dashboard:
# SD_AI_API_URL = https://your-ngrok-url.ngrok.io
```

### 5. **Конфигурация для hybrid режима**

Создайте `ecosystem.config.js`:
```javascript
module.exports = {
  apps: [
    {
      name: 'weather-nft-hybrid',
      script: 'simple-frontend-server.js',
      env: {
        NODE_ENV: 'production',
        PORT: 8080,
        SD_AI_API_URL: process.env.SD_AI_API_URL || 'https://your-ngrok-url.ngrok.io',
        AI_API_URL: 'http://localhost:3006',
        ADMIN_API_URL: 'http://localhost:3008',
        BLOCKCHAIN_API_URL: 'http://localhost:3007'
      }
    }
  ]
};
```

## 📋 **Hosting Platforms Comparison**

### 🌟 **Vercel (Рекомендуется для начала)**
```
✅ Бесплатный план: Unlimited static sites
✅ Автодеплой: Из GitHub
✅ Custom domains: Бесплатно
✅ Serverless functions: 100GB-hrs/месяц
❌ Нет GPU: Нужен external SD AI
💰 Стоимость: $0/месяц
```

**Настройка:**
```bash
vercel --prod
# Добавьте в Vercel dashboard:
# Environment Variables → SD_AI_API_URL → https://your-ngrok-url.ngrok.io
```

### 🚂 **Railway (Full Stack)**
```
✅ Free Tier: $5 credit каждый месяц
✅ PostgreSQL: Включена
✅ Custom domains: Бесплатно
✅ Docker support: Полная поддержка
⚠️ GPU Support: Дорогие планы ($50+/месяц)
💰 Стоимость: ~$5-15/месяц без GPU
```

**Настройка:**
```bash
# Подключите GitHub репозиторий
# Используйте Dockerfile.railway
# Добавьте SD_AI_API_URL в environment variables
```

### 🎨 **Render**
```
✅ Free Tier: 750 часов/месяц
✅ PostgreSQL: Бесплатная база
✅ Auto-deploy: Из GitHub
✅ SSL certificates: Автоматически
⚠️ GPU Plans: От $10/месяц
💰 Стоимость: $0-25/месяц
```

### ☁️ **Google Cloud Run**
```
✅ Pay-per-use: Платите только за запросы
✅ Auto-scaling: 0 → 1000+ инстансов
✅ Custom domains: Поддерживаются
⚠️ Cold starts: Возможны задержки
💰 Стоимость: ~$1-10/месяц при небольшом трафике
```

## 🧠 **SD AI Options**

### 🏠 **Local + ngrok (Рекомендуется)**
```
Плюсы:
✅ Используете вашу RTX 2080
✅ Полная мощность SD среды  
✅ Бесплатно для GPU части
✅ Низкая latency (локальная обработка)

Минусы:
❌ Нужно держать ПК включенным
❌ Зависит от вашего интернета
❌ ngrok free: 1 одновременное подключение
```

**Setup:**
```bash
# 1. Запустите SD AI локально
python sd-pytorch-integration.py --server

# 2. Запустите ngrok
ngrok http 8000

# 3. Используйте ngrok URL в облачном деплое
```

### ☁️ **Google Colab Pro ($10/месяц)**
```
✅ T4/V100 GPU: Бесплатно/дешево
✅ Pre-installed PyTorch: Готов к работе
✅ Jupyter interface: Удобная разработка
❌ Session limits: 12-24 часа максимум
❌ Не всегда доступны GPU
```

**Setup в Colab:**
```python
# Установите ngrok в Colab
!pip install pyngrok
from pyngrok import ngrok

# Запустите ваш SD AI
!git clone https://github.com/your-username/weather-nft-live
%cd weather-nft-live
!pip install -r requirements-pytorch.txt

# Запустите сервер с туннелем
!python sd-pytorch-integration.py --server &
public_url = ngrok.connect(8000)
print(f"SD AI доступен по: {public_url}")
```

### 🚀 **RunPod (Специализированный AI хостинг)**
```
✅ RTX 4090: $0.34/час (~$25/месяц при 24/7)
✅ A100: $1.10/час (~$80/месяц)
✅ Pre-installed environments: PyTorch готов
✅ SSH + Jupyter: Полный доступ
✅ Persistent storage: Данные сохраняются
```

**Setup на RunPod:**
```bash
# 1. Создайте инстанс с PyTorch template
# 2. Загрузите ваш код
git clone https://github.com/your-username/weather-nft-live
cd weather-nft-live

# 3. Запустите SD AI
python sd-pytorch-integration.py --server

# 4. Используйте RunPod public IP в облачном деплое
```

## 🎯 **Рекомендуемый Stack для начала**

### **Бесплатный вариант:**
```
Frontend: Vercel (бесплатно)
Backend APIs: Vercel Serverless (бесплатно)  
SD AI: Ваш ПК + ngrok (бесплатно)
Database: Supabase (бесплатно)
Monitoring: Vercel Analytics (бесплатно)

💰 Стоимость: $0/месяц
```

### **Продакшн вариант:**
```
Frontend: Vercel Pro ($20/месяц)
Backend: Railway ($15/месяц)
SD AI: RunPod RTX4090 ($25/месяц)
Database: Railway PostgreSQL (включено)
Monitoring: Railway Metrics (включено)

💰 Стоимость: ~$60/месяц
```

## 🔧 **Следующие шаги**

1. **Выберите платформу** (рекомендую начать с Vercel)
2. **Создайте GitHub репозиторий**
3. **Настройте ngrok для SD AI**
4. **Deploy и тестируйте**
5. **Масштабируйте по необходимости**

Какой вариант хотите попробовать первым? 🤔