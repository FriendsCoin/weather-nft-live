# 🛠️ WeatherNFT Management Scripts

## 📋 Доступные скрипты

### 🔄 **restart-all.sh / restart-all.bat**
Полная перезагрузка всех сервисов
```bash
./restart-all.sh        # Linux/Mac
restart-all.bat          # Windows
```

**Что делает:**
- Останавливает все запущенные сервисы
- Проверяет доступность портов
- Запускает все 5 сервисов по очереди
- Показывает статус каждого сервиса
- Создает логи в папке `logs/`

### 🛑 **stop-all.sh**
Останавливает все сервисы
```bash
./stop-all.sh           # Linux/Mac
```

**Что делает:**
- Находит и корректно останавливает все процессы WeatherNFT
- Показывает результат для каждого сервиса

### 📊 **status.sh**
Проверяет статус всех сервисов
```bash
./status.sh             # Linux/Mac
```

**Что показывает:**
- Статус каждого сервиса (запущен/остановлен)
- Доступность портов
- Health check API endpoints
- Количество активных событий
- Использование системных ресурсов
- Быстрые команды для управления

## 🚀 Быстрый старт

### Первый запуск:
```bash
# 1. Перейти в папку проекта
cd weather-nft-live

# 2. Запустить все сервисы
./restart-all.sh

# 3. Проверить статус
./status.sh

# 4. Открыть админ панель
# http://localhost:8081/admin-futuristic.html
```

### Ежедневное использование:
```bash
# Быстрая перезагрузка
./restart-all.sh

# Проверить что все работает
./status.sh

# Посмотреть логи
tail -f logs/*.log

# Остановить все в конце дня
./stop-all.sh
```

## 📁 Структура логов

После запуска создается папка `logs/` с файлами:
```
logs/
├── ai-backend.log      # AI сервис (порт 3006)
├── blockchain.log      # Блокчейн сервис (порт 3007)
├── admin-backend.log   # Админ API (порт 3008)
├── frontend.log        # Фронтенд (порт 8081)
└── sd-ai.log          # SD AI Mock (порт 8000)
```

## 🔧 Troubleshooting

### Порт занят
```bash
# Найти процесс на порту
lsof -i :3006
netstat -ano | findstr :3006  # Windows

# Убить процесс
kill <PID>
taskkill /F /PID <PID>        # Windows
```

### Сервис не запускается
```bash
# Посмотреть логи
cat logs/ai-backend.log

# Запустить вручную для отладки
node simple-test-server.js
```

### Очистить все
```bash
# Остановить все
./stop-all.sh

# Удалить логи
rm -rf logs/

# Запустить заново
./restart-all.sh
```

## 🌐 URL-адреса сервисов

После успешного запуска доступны:

| Сервис | URL | Описание |
|--------|-----|----------|
| **Frontend** | http://localhost:8081 | Главная страница |
| **Admin Panel** | http://localhost:8081/admin-futuristic.html | Админ панель с терминалом |
| **Test Page** | http://localhost:8081/admin-test.html | Страница тестирования |
| **AI Backend** | http://localhost:3006 | AI API |
| **Blockchain** | http://localhost:3007 | Blockchain API |
| **Admin API** | http://localhost:3008 | Admin Backend API |
| **SD AI Mock** | http://localhost:8000 | SD AI Mock Server |

## 💡 Pro Tips

1. **Терминал в админ панели** - кликните на зеленую кнопку в правом нижнем углу
2. **Мониторинг логов** - используйте `tail -f logs/*.log` для отслеживания в реальном времени
3. **Docker альтернатива** - для production используйте `docker-compose -f docker-compose.dev.yml up`
4. **Автозапуск** - добавьте `./restart-all.sh` в автозагрузку системы

## 🔒 Безопасность

- Скрипты работают только с локальными процессами
- Нет удаления важных файлов
- Логи содержат только служебную информацию
- Все порты только для локального доступа (localhost)