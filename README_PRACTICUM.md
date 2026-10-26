# Kittygram Практикум Текущий рейтинг

Базовая часть проекта: коты, достижения, токеновая аутентификация, личный профиль,
валидации, поиск, фильтры, сортировка, пагинация и OpenAPI. Дополнение «Кот дня»
сохранено; его контракт описан отдельно в README_THEME6.md.

## Зависимости и запуск

Python 3.10 в Linux-контейнере; Docker Desktop и Docker Compose на компьютере.
Прямые Python-зависимости зафиксированы в requirements.txt:
Django 3.2, DRF 3.12.4, asgiref 3.3.4, pytz 2021.1, sqlparse 0.4.1,
Gunicorn 23.0.0, WhiteNoise 6.7.0, drf-spectacular 0.27.2.
ReDoc CE 2.1.5 включён в cats/static/vendor вместе с лицензией MIT.

1. Запустите Docker Desktop и дождитесь Engine running.
2. Откройте терминал в папке проекта.
3. Выполните команды (Windows: вместо python3 можно использовать py):

```sh
python3 setup_env.py
docker compose up -d --build --wait
```

На Mac после Colima сначала переключите контекст: `docker context use desktop-linux`.
Без Python на компьютере скопируйте .env.example в .env и замените значения replace-…
своими случайными секретами; зависимости приложения установит Docker.

При старте автоматически применяются миграции, создаются группы, собирается статика.
С LOAD_DEMO_DATA=true создаётся справочник достижений и при первом старте — демонстрационные
пользователи, коты и голоса. SQLite хранится в томе kittygram_data. Запуск обслуживает
Gunicorn с двумя процессами, статику админки и ReDoc — WhiteNoise.

## Настройки окружения

| Переменная | Назначение |
|---|---|
| DJANGO_SECRET_KEY | Случайный ключ Django; обязателен |
| DJANGO_DEBUG | Режим отладки, по умолчанию True для локальной учебной работы |
| DJANGO_ALLOWED_HOSTS | Разрешённые имена, по умолчанию localhost,127.0.0.1,[::1] |
| DEMO_PASSWORD | Пароль только для первоначального создания демопользователей |
| LOAD_DEMO_DATA | true — добавить демонстрационные данные |
| PORT | Порт компьютера, по умолчанию 8000 |

setup_env.py не перезаписывает существующий .env. Изменение DEMO_PASSWORD не меняет
пароли аккаунтов, уже сохранённых в базе. .env и SQLite-база не входят в Git и архивы.

## Учётные записи и права

- demo_admin: суперпользователь; управляет всеми котами, достижениями, пользователями и группами.
- anna и boris: владельцы, видят и изменяют только своих котов.
- viewer: только просмотр своего кота без изменения.
- demo_voter_01…12: участники голосования через API, без входа в админку.

Личный API /api/cats/ требует входа. Чужой кот возвращает 404. is_staff не отменяет
проверку владельца. Публичная витрина /api/showcase/cats/ содержит лишь id, name, color.
Справочник достижений публичен и доступен через API только для чтения. Редактировать
справочник может администратор в /admin/. Владельцы выбирают достижения для своих котов.

## Основные эндпоинты

| Метод | Путь | Назначение |
|---|---|---|
| GET, POST | /api/cats/ | Свои коты / создать кота |
| GET, PUT, PATCH, DELETE | /api/cats/{id}/ | Карточка / замена / изменение / удаление своего кота |
| GET | /api/cats/mine/ | Только свои коты даже для администратора |
| GET | /api/achievements/ | Публичный список достижений |
| GET | /api/achievements/{id}/ | Одно достижение |
| POST | /api/auth/token/ | Вход по username/password |
| GET | /api/users/me/ | Собственный профиль и группы |
| GET | /api/openapi.json | Спецификация OpenAPI 3.0.3 |
| GET | /api/docs/ | ReDoc с локальным JavaScript без внешнего CDN |
| GET | /health/ | Проверка работы |

Вход: POST /api/auth/token/ с JSON {"username":"anna","password":"<DEMO_PASSWORD>"}.
Ответ: {"token":"<token>"}. Заголовок запросов: `Authorization: Token <token>`.
Поддерживаются также Session и Basic Authentication. Вход в браузере: /api-auth/login/.

Создание: POST /api/cats/ с JSON:

```json
{"name":"Мурка","color":"gray","birth_year":2022,"achievements":[1]}
```

Ответ 201 содержит id, name, color, birth_year, owner (ID пользователя), achievements
(массив ID). Владелец назначается сервером. PATCH принимает отдельные поля;
PUT требует name и color. achievements=[] снимает все достижения. Несуществующий
ID достижения возвращает 400. Старые записи получают пустой массив достижений.

Правила: имя 2–16 символов; цвет 3–16; birth_year 1900…текущий или null.
Название достижения уникально и имеет максимум 64 символа. Ранее существовавшие
короткие значения в старой базе сохраняются; при их редактировании действуют валидаторы.
Кота с историей рейтинга удалить нельзя (400).

Примеры фильтров личного API:

```text
/api/cats/?search=Луна&owner=anna&birth_year=2022&ordering=name&page_size=1
/api/cats/?color=black&ordering=-birth_year
```

search ищет по имени и цвету. owner — логин, birth_year — числовой год.
Сортировка разрешена по id, name, birth_year; минус задаёт обратный порядок.
Фильтры не расширяют права: owner=boris от anna возвращает пустой список.
Пагинация: 5 записей по умолчанию, максимум 100; поля count, next, previous, results.

## Проверки и управление

```sh
docker compose exec web python manage.py test cats showcase --verbosity 2
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web python manage.py spectacular --file /tmp/openapi.json --format openapi-json --validate --fail-on-warn
docker compose logs --tail=40 web
docker compose stop
docker compose up -d --wait
```

29 тестов: 7 проверяют базовый практикум, 22 — ранее реализованные роли и «Кота дня».
Проект развёрнут локально на Docker Desktop; сервер в интернете не используется.
