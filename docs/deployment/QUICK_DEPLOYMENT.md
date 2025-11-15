# 🚀 Быстрый деплой - Финальные шаги

## ✅ Текущий статус:
- ✅ Chocolatey установлен
- ✅ Код готов в git
- 🔄 Осталось: ngrok + GitHub push + Vercel

## 🎯 Следующие действия (в PowerShell):

### 1. Установите ngrok
```cmd
# Попробуйте через Winget (не требует админ прав):
winget install ngrok.ngrok

# Или запустите готовый скрипт:
.\install-ngrok.bat

# Проверьте установку:
ngrok version
```

### 2. Push в GitHub  
```cmd
git push
# Логин: FriendsCoin
# Пароль: Personal Access Token (создайте на GitHub → Settings → Developer settings → Personal access tokens)
```

### 3. Deploy на Vercel
```cmd
npm i -g vercel
vercel login
vercel --prod
```

### 4. Запустите SD AI сервер
```cmd
# В первом терминале:
conda activate SD
python sd-pytorch-integration.py --server

# Во втором терминале:
ngrok http 8000
# Скопируйте URL типа: https://abc123.ngrok.io
```

### 5. Добавьте ngrok URL в Vercel
1. https://vercel.com/dashboard → ваш проект
2. Settings → Environment Variables  
3. Добавьте: `SD_AI_API_URL = https://your-ngrok-url.ngrok.io`
4. Redeploy: `vercel --prod`

## 🎉 Результат
После всех шагов:
- **Live App**: https://weather-nft-live-xxx.vercel.app
- **Admin Panel**: добавьте `/admin-futuristic.html`
- **SD AI**: ваш RTX 2080 работает из облака!

## 🆘 Если ngrok не устанавливается:
1. Скачайте вручную: https://ngrok.com/download
2. Распакуйте ngrok.exe в `C:\ngrok\`
3. Добавьте `C:\ngrok` в PATH
4. Перезапустите PowerShell

**Готово! Осталось только выполнить шаги выше! 🚀**