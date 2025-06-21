# 📡 Установка ngrok на Windows

## 🚀 Способ 1: Chocolatey (Рекомендуется)

### **Установка Chocolatey:**
```cmd
# Откройте PowerShell как Администратор
# Вставьте и выполните:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### **Установка ngrok:**
```cmd
# После установки Chocolatey:
choco install ngrok
```

## 🔧 Способ 2: Прямая загрузка

### **Скачайте ngrok:**
1. Идите на https://ngrok.com/download
2. Выберите Windows (64-bit)
3. Скачайте ngrok.exe

### **Установка:**
```cmd
# Создайте папку
mkdir C:\ngrok
# Скопируйте ngrok.exe в C:\ngrok\

# Добавьте в PATH:
# Windows → Edit the system environment variables → Environment Variables
# System Variables → Path → Edit → New → C:\ngrok
```

## 🔧 Способ 3: Winget (Windows 10+)

```cmd
# В PowerShell или CMD:
winget install ngrok.ngrok
```

## ✅ **Проверка установки:**

```cmd
# Перезапустите CMD/PowerShell
ngrok version
# Должно показать версию ngrok
```

## 🎯 **Использование:**

```cmd
# Перейдите в папку проекта
cd E:\SDfu-master\SDfu-masterOSC\weather-nft-live

# Запустите SD AI (в одном терминале)
conda activate SD
python sd-pytorch-integration.py --server

# Создайте туннель (в другом терминале)
ngrok http 8000
```

## 📋 **Результат:**

После установки и запуска вы увидите:
```
ngrok                                                                           
                                                                                
Session Status                online                                            
Account                       your-email@example.com (Plan: Free)              
Version                       3.x.x                                             
Region                        United States (us)                               
Latency                       45ms                                              
Web Interface                 http://127.0.0.1:4040                           
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
                                                                                
Connections                   ttl     opn     rt1     rt5     p50     p90      
                              0       0       0.00    0.00    0.00    0.00     
```

**Скопируйте URL**: `https://abc123.ngrok.io`

## 🆘 **Troubleshooting:**

### **"ngrok not found" после установки:**
```cmd
# Перезапустите терминал
# Или проверьте PATH:
echo %PATH%
```

### **Chocolatey не установился:**
- Запустите PowerShell как Администратор
- Проверьте ExecutionPolicy: `Get-ExecutionPolicy`
- Должно быть Unrestricted или Bypass

### **ngrok требует аутентификацию:**
1. Создайте аккаунт на https://ngrok.com
2. Скопируйте authtoken из dashboard
3. Выполните: `ngrok authtoken YOUR_TOKEN`

## 💡 **Pro Tips:**

1. **Веб интерфейс**: http://127.0.0.1:4040 (мониторинг запросов)
2. **Статичный URL**: Платные планы дают постоянные URL
3. **Конфиг файл**: `~/.ngrok2/ngrok.yml` для сохранения настроек

---

**После установки вернитесь к настройке деплоя! 🚀**