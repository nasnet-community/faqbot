FROM python:3.11-slim

RUN pip install poetry
RUN poetry config virtualenvs.create false
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-dev
COPY . /app
CMD ["python3", "main.py"]
