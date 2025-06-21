# 🐳 Docker Quick Start для WeatherNFT

## 🚀 Быстрый запуск с Docker

### 1. Установка Docker
```bash
# Windows/Mac: Скачайте Docker Desktop
# https://www.docker.com/products/docker-desktop

# Linux:
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2. Запуск всего проекта
```bash
# Клонируйте проект
cd weather-nft-live

# Запустите все сервисы
docker-compose -f docker-compose.dev.yml up

# Или в фоновом режиме
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Проверка статуса
```bash
# Посмотреть запущенные контейнеры
docker ps

# Посмотреть логи
docker-compose -f docker-compose.dev.yml logs -f

# Логи конкретного сервиса
docker-compose -f docker-compose.dev.yml logs -f weather-nft-ai
```

### 4. Доступные сервисы
После запуска доступны:
- **Frontend**: http://localhost:8081
- **Admin Panel**: http://localhost:8081/admin-futuristic.html
- **AI Backend**: http://localhost:3006
- **Blockchain**: http://localhost:3007
- **Admin API**: http://localhost:3008
- **SD AI**: http://localhost:8000

## 🛠️ Управление

### Остановка
```bash
# Остановить все сервисы
docker-compose -f docker-compose.dev.yml down

# Остановить и удалить volumes
docker-compose -f docker-compose.dev.yml down -v
```

### Перезапуск сервиса
```bash
# Перезапустить конкретный сервис
docker-compose -f docker-compose.dev.yml restart weather-nft-ai
```

### Обновление кода
```bash
# Пересобрать образы после изменений
docker-compose -f docker-compose.dev.yml build

# Запустить с пересборкой
docker-compose -f docker-compose.dev.yml up --build
```

## 🔧 Отладка

### Войти в контейнер
```bash
# Открыть bash в контейнере
docker exec -it weather-nft-frontend sh

# Выполнить команду в контейнере
docker exec weather-nft-ai node --version
```

### Просмотр логов
```bash
# Последние 100 строк логов
docker-compose -f docker-compose.dev.yml logs --tail=100

# Следить за логами в реальном времени
docker-compose -f docker-compose.dev.yml logs -f
```

## 🌟 Преимущества Docker

1. **Изолированное окружение** - нет конфликтов зависимостей
2. **Легкий деплой** - один файл для запуска всего
3. **Масштабируемость** - легко добавить новые сервисы
4. **Воспроизводимость** - работает одинаково везде

## 📝 Для Production

Для production используйте оптимизированный `docker-compose.yml`:
- SSL/TLS сертификаты
- Nginx reverse proxy
- Оптимизированные образы
- Health checks
- Restart policies
- Resource limits

## 🆘 Troubleshooting

### Порты заняты
```bash
# Найти процесс на порту
lsof -i :3006
netstat -ano | findstr :3006  # Windows

# Изменить порты в docker-compose.dev.yml
```

### Нет места на диске
```bash
# Очистить неиспользуемые образы
docker system prune -a

# Очистить volumes
docker volume prune
```

### Медленная работа на Windows
- Используйте WSL2
- Включите виртуализацию в BIOS
- Выделите больше памяти Docker Desktop