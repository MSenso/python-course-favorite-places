Любимые места
=============

Сервис для сохранения информации о любимых местах.

Зависимости
===========
Установите необходимое ПО:

1. [Docker Desktop](https://www.docker.com).
2. [Git](https://github.com/git-guides/install-git).
3. [PyCharm](https://www.jetbrains.com/ru-ru/pycharm/download) (опционально).


Установка
=========
Склонируйте репозиторий:
.. code-block::console
    git clone https://github.com/mnv/python-course-favorite-places.git

1. Для конфигурации приложения скопируйте содержимое `.env.sample` в `.env` файл:
.. code-block::console
    cp .env.sample .env

   Этот файл содержит переменные окружения, значения которых будут общими для всего приложения.
   Файл-образец (`.env.sample`) содержит набор переменных со значениями по умолчанию,
   поэтому он может быть настроен в зависимости от окружения.

2. Соберите контейнер с помощью Docker Compose:
.. code-block::console
     docker compose build

    Эта команда должна быть запущена из корневого каталога, в котором находится `Dockerfile`.
    Вам также необходимо собрать контейнер docker заново в случае, если вы обновили `requirements.txt`.

3. Для корректной работы приложения настройте базу данных.
   Примените миграции для создания таблиц в базе данных:
.. code-block::console
     docker compose run favorite-places-app alembic upgrade head

4. Теперь можно запустить проект внутри контейнера Docker:
.. code-block::console
    docker compose up

   Когда контейнеры подняты, сервер запускается по адресу [http://0.0.0.0:8010/docs](http://0.0.0.0:8010/docs).
   Вы можете открыть его в браузере.


Использование
=============



Работа с базой данных
---------------------
Чтобы инициализировать функциональность миграции, выполните первый запуск:
.. code-block::console
    docker compose exec favorite-places-app alembic init -t async migrations

Эта команда создаст каталог с конфигурационными файлами для настройки функциональности асинхронных миграций.

Для создания новых миграций, которые будут обновлять таблицы базы данных в соответствии с обновленными моделями,
выполните эту команду:
.. code-block::console
    docker compose run favorite-places-app alembic revision --autogenerate  -m "your description"

Чтобы применить созданные миграции, выполните следующие действия:
.. code-block::console
    docker compose run favorite-places-app alembic upgrade head


Автоматизация
=============
Проект содержит специальный `Makefile`, который предоставляет ярлыки для набора команд:
1. Build the Docker container:
.. code-block::console
    make build

2. Создание документации Sphinx:
.. code-block::console
    make docs-html

3. Автоформатирование исходного кода:
.. code-block::console
    make format

4. Статический анализ (линтеры):
.. code-block::console
    make lint

5. Автотесты:
.. code-block::console
    make test

    Отчет о покрытии тестами будет расположен по адресу `src/htmlcov/index.html`.
    Таким образом, вы можете оценить качество покрытия автоматизированных тестов.

6. Запуск автоформата, линтеров и тестов одной командой:
.. code-block::console
    make all

Выполните эти команды из исходного каталога, в котором находится `Makefile`.

Документация
============

Клиенты
=======
Базовый
--------
.. automodule:: clients.base.base
    :members:

Гео-клиент
---
.. automodule:: clients.geo
    :members:

Интеграции
============
БД
--------
.. automodule:: integrations.db.session
    :members:

Модели
======
.. automodule:: models.mixins
    :members:
.. automodule:: models.places
    :members:

Репозитории
============
.. automodule:: repositories.base_repository
    :members:
.. automodule:: repositories.places_repository
    :members:



Схемы
=======
.. automodule:: schemas.base
    :members:
.. automodule:: schemas.places
    :members:
.. automodule:: schemas.routes
    :members:

Сервисы
========
.. automodule:: services.places_service
    :members:

Транспорт
=========
.. automodule:: transport.handlers.places
    :members:


