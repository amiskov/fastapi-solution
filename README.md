# Асинхронный API для кинотеатра
[Команда №17](https://yandex-students.slack.com/archives/C03833GPQGH/p1652369332840549), @amiskov и @vitaliyrakitin.

## Документация Open API
См. URI `/api/openapi`.

## Запуск через docker-compose

Для запуска через docker-compose достаточно определить все env-файлы в папке `enviroments/` на основе шаблонов из этой же папки и использовать команду:

```bash
docker-compose up --build
```

При этом запускаются контейнеры в следующем порядке:

1. DB PostgreSQL (`db`);
2. Django App[^*] с админкой для онлайн-кинотеатра из спринта 2 (`app`);
3. Nginx (`nginx`);
4. Elastic Search (`elasticsearch`);
5. ETL-процесс[^**] по выгрузке данных из PostgreSQL в Elastic Search из спринта 3 (`etl`);
6. Redis;
7. Сервис FastAPI из данного спринта (`app`).

[^*]: Образ `ghcr.io/vitaliyrakitin/cinema-django-app:latest` залит в github registry. Сам код можно посмотреть в [репозитории](https://github.com/VitaliyRakitin/new_admin_panel_sprint_2/tree/main/01_docker_compose/app).

[^**]: Образ `ghcr.io/vitaliyrakitin/cinema-etl:latest` залит в github registry. Сам код можно посмотреть в [репозитории](https://github.com/VitaliyRakitin/new_admin_panel_sprint_3/tree/main/01_etl).

## Тесты
В проекте настроены фцавтотесты.

Для запуска достаточно выполнить следующий код:
```bash
bash functional_tests.sh
```

## Я хочу контрибьютить!

Прежде, чем заливать любой PR в проект, необходимо пройти минимальные требования по flake8.

**Правила простые:** *качество кода не должно падать, документация должна быть у каждого модуля.*

Для упрощения процесса в проекте настроен `pre-commit`. 
Чтобы его подключить, необходимо проделать следующее:

```bash
pip3 install -r requirements-dev.txt
pre-commit install
```
