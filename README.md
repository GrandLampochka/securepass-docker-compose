# SecurePass

Лабораторная работа №22.
Контейнеризация многокомпонентного приложения с Docker Compose.

## Описание

SecurePass — генератор безопасных паролей и криптографических хэшей.

## Технологии

- Frontend: HTML, CSS, JavaScript, Nginx
- Backend: Python, FastAPI
- Database: PostgreSQL 16
- Web-service: Python, FastAPI
- Docker Compose

## Возможности

- Генерация безопасных паролей
- Вычисление SHA-256
- Хэширование bcrypt
- Проверка bcrypt-хэшей
- Журнал аудита PostgreSQL

## Запуск

Команда запуска:

docker compose up -d --build

Открыть приложение в браузере:

http://localhost:8080

## Проверка контейнеров

docker compose ps

## Остановка

docker compose down

## Архитектура

Frontend -> Backend -> Web-service

Backend <-> PostgreSQL

Все четыре контейнера работают в общей Docker bridge-сети.
