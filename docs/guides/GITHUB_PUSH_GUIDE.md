# 📤 GitHub Push Guide

## 🚀 Как запушить код на GitHub

### **В Windows PowerShell/CMD:**

```cmd
# Перейдите в папку проекта
cd E:\SDfu-master\SDfu-masterOSC\weather-nft-live

# Проверьте статус
git status

# Push на GitHub (появится окно аутентификации)
git push -u origin main
```

### **Если просит логин:**

1. **Username**: `FriendsCoin` 
2. **Password**: Используйте **Personal Access Token** (не обычный пароль)

### **Создание Personal Access Token:**

1. Идите на GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Name: `weather-nft-deployment`
4. Expiration: `90 days`
5. Scopes: отметьте `repo` (полный доступ к репозиториям)
6. Generate token
7. **СКОПИРУЙТЕ TOKEN** (показывается только один раз!)

### **Альтернативный способ - SSH ключ:**

```cmd
# Генерируйте SSH ключ
ssh-keygen -t ed25519 -C "your-email@example.com"

# Добавьте ключ в GitHub
# GitHub → Settings → SSH and GPG keys → New SSH key
# Вставьте содержимое файла .ssh/id_ed25519.pub

# Смените remote на SSH
git remote set-url origin git@github.com:FriendsCoin/weather-nft-live.git
git push -u origin main
```

## ✅ **После успешного push:**

Ваш код будет доступен на:
https://github.com/FriendsCoin/weather-nft-live

### **Следующий шаг - Vercel Deploy:**

```bash
# В Windows PowerShell/CMD:
npm i -g vercel
vercel login
vercel

# Выберите:
# - Link to existing project? No
# - Project name: weather-nft-live  
# - Directory: ./
```

## 🔗 **Результат**

После push + Vercel deploy:
- 📦 **GitHub**: https://github.com/FriendsCoin/weather-nft-live
- 🌐 **Live App**: https://weather-nft-live-xxx.vercel.app
- 👨‍💼 **Admin Panel**: https://weather-nft-live-xxx.vercel.app/admin-futuristic.html

## 💡 **Pro Tip**

После первого push все последующие будут автоматически деплоиться на Vercel при каждом `git push`!