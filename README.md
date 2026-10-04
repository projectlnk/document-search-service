# Document Search Service

Тестовое задание для позиции Junior Python Backend Developer.

Сервис для полнотекстового поиска по документам. Данные хранятся в **PostgreSQL**, полнотекстовый индекс — в **Elasticsearch**, API реализовано на **FastAPI**.

## 🛠 Стек технологий

- **Python 3.12**
- **FastAPI** — асинхронный веб-фреймворк
- **SQLAlchemy 2.0 (async)** + **asyncpg** — работа с PostgreSQL
- **Elasticsearch 8** (async client) — полнотекстовый поиск
- **PostgreSQL 16** — реляционная БД
- **Docker / Docker Compose** — контейнеризация
- **Pytest** — функциональные тесты
- **Pydantic v2** — валидация данных

## 🚀 Быстрый старт

### Требования
- Docker и Docker Compose

### 1. Клонировать репозиторий и перейти в папку
```bash
git clone <repo_url>
cd <repo_name>
```

### 2. Создать файл `.env` в корне проекта (Скопируйте .env.example в .env)
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=test_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

ELASTIC_HOST=elasticsearch
ELASTIC_PORT=9200
```

### 3. Положить файл `posts.csv` в корень проекта

### 4. Запустить сервисы
```bash
docker-compose up --build -d
```

### 5. Загрузить документы из CSV в БД и Elasticsearch
```bash
docker-compose exec app python -m app.scripts.load_data
```

### 6. Открыть Swagger UI
Перейти в браузере по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📚 API Endpoints

### `GET /health`
Проверка работоспособности сервиса.

### `GET /documents/search?q={query}`
Полнотекстовый поиск по документам.
- **Параметры:** `q` — поисковый запрос (строка)
- **Возвращает:** до 20 документов, отсортированных по `created_date` (от новых к старым)
- **Пример:**
  ```bash
  curl "http://localhost:8000/documents/search?q=тюнинг"
  ```

### `DELETE /documents/{id}`
Удаление документа из БД и из индекса Elasticsearch по `id`.
- **Пример:**
  ```bash
  curl -X DELETE "http://localhost:8000/documents/42"
  ```

## 📄 Документация

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI (JSON):** файл `docs.json` в корне проекта

Для перегенерации `docs.json` после изменений:
```bash
docker-compose exec app python -m app.scripts.dump_openapi
```

## 🧪 Тесты

Функциональные тесты находятся в папке `tests/`. Для запуска:
```bash
docker-compose exec app pytest -v
```

## 📁 Структура проекта

```
.
├── app/
│   ├── api/              # Роутеры FastAPI (endpoints)
│   ├── core/             # Конфигурация (settings)
│   ├── db/               # Подключения к Postgres и Elasticsearch
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic-схемы
│   ├── scripts/          # Скрипты (загрузка данных, генерация OpenAPI)
│   ├── services/         # Бизнес-логика (поиск, индексация)
│   └── main.py           # Точка входа FastAPI
├── tests/                # Функциональные тесты (pytest)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── docs.json
└── README.md
```

## 🧠 Принятые архитектурные решения

- **Разделение БД и поискового индекса.** В PostgreSQL хранится вся информация о документе (`rubrics`, `created_date`), а Elasticsearch используется только как индекс для быстрого полнотекстового поиска.
- **Сортировка по дате создания.** Elasticsearch возвращает документы по релевантности, но требование ТЗ — сортировка по `created_date`. Поэтому мы сначала получаем список `id` из ES, а затем достаем полные документы из Postgres и сортируем их в Python.
- **Асинхронность.** Все слои (роутеры, сервисы, работа с БД и ES) полностью асинхронные — это позволяет сервису эффективно обрабатывать много параллельных запросов.
- **Батчевая загрузка CSV.** Загрузчик обрабатывает данные порциями по 1000 записей, чтобы не держать в памяти весь файл.