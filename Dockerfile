# Используйте официальный образ Python
FROM python:3.10

# Устанавливаем переменную окружения PYTHONUNBUFFERED
# для предотвращения буферизации вывода Python
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем зависимости (файлы `pyproject.toml` и `poetry.lock`)
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости с использованием Poetry
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

# Копируем остальные файлы проекта в рабочую директорию
COPY . /app/

# Запускаем приложение при старте контейнера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
