# FastAPI Backend (redparts-api)

## Установка

```bash
cd backend/fastapi
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Конфигурация

Создайте файл `.env` на основе переменных:

```
APP_NAME=redparts-api
API_V1_STR=/api/v1
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/redparts_shop
DEBUG=true
```

## Миграции (опционально)

Инициализируйте Alembic и создайте миграции из моделей.

```bash
alembic init alembic
# настройте alembic.ini (sqlalchemy.url) и env.py для app.db.base
# сгенерируйте миграцию
alembic revision --autogenerate -m "init"
# примените
alembic upgrade head
```

## Запуск

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте Swagger UI: http://localhost:8000/docs 