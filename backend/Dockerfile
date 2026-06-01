FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml alembic.ini ./
COPY src ./src
COPY alembic ./alembic
RUN pip install --no-cache-dir .
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]
