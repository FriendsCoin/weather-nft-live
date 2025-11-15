# 🚀 Vercel Deployment Guide

## 🎯 Быстрый деплой WeatherNFT на Vercel

### **Шаг 1: Подготовка GitHub**

```bash
# Создайте GitHub репозиторий
# Идите на github.com → New repository
# Название: weather-nft-live
# Visibility: Public
# Не добавляйте README (у нас уже есть)

# В терминале WSL/Linux:
cd /mnt/e/SDfu-master/SDfu-masterOSC/weather-nft-live
git remote add origin https://github.com/YOUR_USERNAME/weather-nft-live.git
git branch -M main
git push -u origin main
```

### **Шаг 2: Установка Vercel CLI**

```bash
# Установите Vercel CLI
npm i -g vercel

# Войдите в аккаунт (откроется браузер)
vercel login
```

### **Шаг 3: Deploy на Vercel**

```bash
cd /mnt/e/SDfu-master/SDfu-masterOSC/weather-nft-live

# Deploy проекта
vercel

# Ответьте на вопросы:
# ? Set up and deploy? [Y/n] y
# ? Which scope? [Your account]
# ? Link to existing project? [y/N] n
# ? What's your project's name? weather-nft-live
# ? In which directory is your code located? ./

# Дождитесь деплоя...
# ✅ Deploy successful!
# 🔗 URL: https://weather-nft-live-xxx.vercel.app
```

### **Шаг 4: Настройка SD AI (Hybrid)**

#### **На вашем Windows ПК:**

```cmd
# 1. Запустите SD AI сервер
conda activate SD
cd E:\SDfu-master\SDfu-masterOSC\weather-nft-live
python sd-pytorch-integration.py --server

# Сервер запустится на http://localhost:8000
```

#### **Установите ngrok:**

```cmd
# Скачайте ngrok с https://ngrok.com/download
# Или через chocolatey:
choco install ngrok

# Создайте туннель
ngrok http 8000

# Получите URL типа: https://abc123.ngrok.io
# СКОПИРУЙТЕ ЭТОТ URL!
```

### **Шаг 5: Настройка Environment Variables в Vercel**

1. **Откройте Vercel Dashboard**: https://vercel.com/dashboard
2. **Найдите ваш проект**: weather-nft-live
3. **Settings → Environment Variables**
4. **Добавьте переменные:**

```env
SD_AI_API_URL = https://your-ngrok-url.ngrok.io
NODE_ENV = production
AI_API_URL = http://localhost:3006
ADMIN_API_URL = http://localhost:3008
BLOCKCHAIN_API_URL = http://localhost:3007
```

### **Шаг 6: Redeploy**

```bash
# После добавления переменных, redeploy:
vercel --prod

# Или push в GitHub (автодеплой):
git add .
git commit -m "Add environment variables"
git push
```

## 🎉 **Результат**

После успешного деплоя у вас будет:

### **🌐 Live URLs:**
- **Main App**: https://weather-nft-live-xxx.vercel.app
- **Admin Panel**: https://weather-nft-live-xxx.vercel.app/admin-futuristic.html
- **Purchase Flow**: https://weather-nft-live-xxx.vercel.app/test-purchase.html

### **🧠 SD AI Integration:**
- Ваш ПК с RTX 2080 обрабатывает AI
- ngrok туннель связывает облако с вашим ПК
- Полная мощность PyTorch доступна в облаке

### **📊 Features доступны:**
- Real-time admin panel с встроенным терминалом
- Тестирование AI предсказаний
- Marketplace с анимациями
- Полный мониторинг системы

## 🔧 **Troubleshooting**

### **404 Error на страницах:**
```bash
# Проверьте vercel.json конфигурацию
# Должны быть routes для всех HTML файлов
```

### **SD AI недоступен:**
```bash
# Проверьте что ngrok запущен
curl https://your-ngrok-url.ngrok.io/health

# Проверьте что SD AI сервер работает на вашем ПК
# В админ панели: команда "sd-info"
```

### **Environment Variables не работают:**
1. Vercel Dashboard → Settings → Environment Variables
2. Убедитесь что переменные добавлены
3. Redeploy: `vercel --prod`

### **Build ошибки:**
```bash
# Проверьте package.json scripts
# Убедитесь что start script указывает на simple-frontend-server.js
```

## 💡 **Pro Tips**

1. **Custom Domain**: 
   - Vercel Dashboard → Domains → Add domain
   - Бесплатно для .vercel.app поддоменов

2. **Analytics**:
   - Vercel Dashboard → Analytics
   - Бесплатный мониторинг трафика

3. **Auto-deploy**:
   - Каждый push в GitHub автоматически деплоится
   - Пулл реквесты создают preview deployments

4. **Logs**:
   ```bash
   vercel logs
   # или в Dashboard → Functions → View logs
   ```

## 🎯 **Следующие шаги**

После успешного деплоя:

1. **Протестируйте admin panel** с командой `sd-info`
2. **Проверьте AI prediction** с командой `test-ai`
3. **Поделитесь ссылкой** с друзьями для тестирования
4. **Мониторьте через Vercel Analytics**

## 🆘 **Нужна помощь?**

- **Vercel Docs**: https://vercel.com/docs
- **ngrok Docs**: https://ngrok.com/docs
- **Issues**: Создайте issue в GitHub репозитории

---

**Готово! Ваш WeatherNFT.live теперь live в интернете! 🎉**