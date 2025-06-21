# 🚀 Финальные шаги деплоя

## ✅ Что уже сделано:
- Код подготовлен и закоммичен в git
- Созданы все конфиги для деплоя (vercel.json, package.json)
- Добавлены инструкции по установке ngrok

## 🎯 Следующие шаги:

### 1. Установите ngrok (если еще не сделали)
```cmd
# Следуйте инструкции в INSTALL_NGROK_WINDOWS.md
choco install ngrok
# или скачайте с https://ngrok.com/download
```

### 2. Push в GitHub
```cmd
cd E:\SDfu-master\SDfu-masterOSC\weather-nft-live
git push
# Введите логин: FriendsCoin
# Пароль: используйте Personal Access Token
```

**Создание токена**: GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic) → отметьте `repo`

### 3. Deploy на Vercel
```cmd
# Установите Vercel CLI
npm i -g vercel

# Войдите в аккаунт
vercel login

# Deploy проекта
vercel --prod

# Выберите:
# - Link to existing project? No
# - Project name: weather-nft-live
# - Directory: ./
```

### 4. Запустите SD AI с ngrok туннелем

#### В первом терминале:
```cmd
conda activate SD
cd E:\SDfu-master\SDfu-masterOSC\weather-nft-live
python sd-pytorch-integration.py --server
```

#### Во втором терминале:
```cmd
ngrok http 8000
# Скопируйте URL типа: https://abc123.ngrok.io
```

### 5. Добавьте ngrok URL в Vercel

1. Откройте Vercel Dashboard: https://vercel.com/dashboard
2. Найдите проект `weather-nft-live` 
3. Settings → Environment Variables
4. Добавьте:
```
SD_AI_API_URL = https://your-ngrok-url.ngrok.io
```
5. Redeploy: `vercel --prod`

## 🎉 Результат

После всех шагов у вас будет:

- **GitHub**: https://github.com/FriendsCoin/weather-nft-live
- **Live App**: https://weather-nft-live-xxx.vercel.app  
- **Admin Panel**: https://weather-nft-live-xxx.vercel.app/admin-futuristic.html

### Тестирование:
1. Откройте admin panel
2. В терминале выполните: `sd-info`
3. Должен показать статус вашего SD AI сервера с RTX 2080

## 🔧 Если что-то не работает:

### ngrok не найден:
- Перезапустите CMD/PowerShell после установки
- Проверьте PATH: `echo %PATH%`

### GitHub push не работает:
- Используйте Personal Access Token вместо пароля
- Или настройте SSH ключ (см. GITHUB_PUSH_GUIDE.md)

### Vercel deploy ошибки:
- Проверьте что все зависимости в package.json
- Убедитесь что start script корректный

### SD AI недоступен в облаке:
- Проверьте что ngrok запущен: `curl https://your-url.ngrok.io/health`
- Убедитесь что URL добавлен в Vercel Environment Variables
- Redeploy после добавления переменных

## 💡 Pro Tips:

1. **Оставьте ngrok запущенным** - ваш SD AI будет доступен из облака
2. **Каждый git push** автоматически деплоится на Vercel
3. **Админ панель** работает в реальном времени с вашим локальным AI
4. **RTX 2080** обрабатывает AI запросы из интернета через ngrok

**Готово! Ваш AI Weather NFT проект теперь live! 🌦️✨**