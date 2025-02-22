# AdNova

[![wakatime](https://wakatime.com/badge/user/cb406c1c-8eb4-4829-b9f9-816a0d284d7e/project/2b690440-fe32-49f5-87ea-b1def19de612.svg)](https://wakatime.com/badge/user/cb406c1c-8eb4-4829-b9f9-816a0d284d7e/project/2b690440-fe32-49f5-87ea-b1def19de612)

Service for advertisers to provide their ads and get profit!

## 🗺️ ER diagram

![ER diagram](./assets/images/er-diagram.png)

Not all tables inlcuded in this diagram (some django utility tables which makes no sense to business logic). On the left side there is default django models and on the right side there is developed models.

Tables that are not mentioned in task (btw, you can see them on diagram):

Table Report:

- campaign_id - relation to Campaign
- client_id - relation to Client
- state - could be `s` (Sent), `r` (Under review), `t` (Took action), `f` (Skipped)
- message - optional text, helps moderator better understand report context
- flagged_by_llm - boolean, if true, then llm thinks that campaign is unacceptable, if false, then campaign is acceptable, if null, then llm has not provided response yet

## 📋 Instructions

### Dedicated services setup

[Backend](./services/backend/README.md)

[Telegram bot](./services/telegram_bot/README.md)

### Setup with docker compose

#### Warning

Plese note that containers will use ports from 13241 to 13245 and 8080, so there is must be no listeners on this ports range.

#### Configure

There is an [infrastructure](./infrastructure/) folder where stored all configs for services inside docker compose, so feel free to change them. In folders where you see `.env.template` you can create `.env` file to override defaults.

#### Pull images

```bash
docker compose pull
```

#### Build images

```bash
docker compose build
```

#### Start services

```bash
docker compose up -d
```

#### Notes

You can just use this command to do all stuff listed above:

```bash
docker compose up -d --build
```

#### Structure

- **backend**: [127.0.0.1:8080](http://127.0.0.1:8080) -> `8080`
  - Depends on: `postgres`, `redis`, `minio`, `backend-initdb`
- **backend-initdb**
  - Depends on: `postgres`, `redis`, `minio`
- **backend-staticfiles**: [127.0.0.1:13241](http://127.0.0.1:13241) -> `80`
- **backend-celery-worker**
  - Depends on: `redis`
- **telegram_bot**
  - Depends on: `backend`, `redis`
- **postgres**
  - Volume: `postgres_data`
- **redis**
  - Volume: `redis_data`
- **pgadmin**: [127.0.0.1:13242](http://127.0.0.1:13242) -> `80`
  - Depends on: `postgres`
  - Volume: `pgadmin_data`
- **grafana**: [127.0.0.1:13243](http://127.0.0.1:13243) -> `3000`
  - Volume: `grafana_data`
- **minio**
  - API: [127.0.0.1:13244](http://127.0.0.1:13244) -> `9000`
  - Console: [127.0.0.1:13245](http://127.0.0.1:13245) -> `9001`
  - Volume: `minio_data`

## ⚙️ Technologies

### [Python](https://www.python.org/)

Python is a high-level programming language renowned for its readability and simplicity. Its extensive standard library and active community make it an ideal choice for rapid prototyping and development. It not so fast as Go or Java, but development speed is rather faster them and systax is very simple and intuitive. Also there is a lot of python developers available on market. Used and trusted by many companies around the world. In project used for `backend` and `telegram_bot` services.

### [Django](https://www.djangoproject.com/)

Django is a powerful web framework for Python that provides rapid development capabilities through built-in tools such as ORM, authentication, and administration systems. It promotes the creation of secure and scalable web appwill write here somethinglications. Used and trusted by many companies around the world. Lets write less boilerplate and more actual logic!). In project used for `backend` service.

### [Django Ninja](https://django-ninja.dev/)

Django Ninja is a web framework that integrates seamlessly with Django, offering high performance (compared to DRF) and ease of use. It is designed to build APIs with minimal code and includes features like data validation and serialization with Pydantic. Not so popular, but much less complex than DRF. I prefer this to FastAPI actually). In project used for `backend` service.

### [aiogram](https://aiogram.dev/)

aiogram is a modern and fully asynchronous framework for Telegram bot development in Python. It allows efficient handling of multiple requests and provides a straightforward interface for building complex bots. Very popular and has big community for today. Known for its speed. In project used for `telegram_bot` service.

### [Redis](https://redis.io/)

Redis is an in-memory data structure store often used as a database, cache, and message broker. It supports various data structures and offers high performance for read and write operations, making it suitable for caching and real-time analytics. Very popular and has big community for today. In project used as fsm for aiogram (to avoid data loss on restart), caches (current_date, mlscores, clicks, views) for backend and as broker for Celery.

### [Postgres](https://www.postgresql.org/)

PostgreSQL is a powerful, open-source relational database system known for its robustness and feature richness. It supports advanced data types and performance optimization features, making it a reliable choice for handling complex queries and large datasets. And the one quote i really as main database for storing data.like: "The best database is that that you know". In project used as main database for storing data.

### [Grafana](https://grafana.com/)

Grafana is an open-source analytics and monitoring platform that allows for the visualization of metrics from various data sources. It provides customizable dashboards and alerting features, aiding in real-time monitoring and analysis. No-dealer winner in the dashboards solution and i really like it. In project used for advertisers' analytics dashboards.

### [MinIO](https://min.io/)

MinIO is a high-performance, S3-compatible object storage system. It is designed for large-scale data infrastructures and is suitable for storing unstructured data such as photos, videos, log files, backups, and container images. Best open-source alternative to AWS S3 for now. In project used to store advertisments' images. Allows us to scale easily (very native replication feature) and soon we can store other things such as user avatars (if we countinue developing project), etc.

### [Celery](https://github.com/celery/celery)

The most popular distributed task queue for Python. Task queues are used as a mechanism to distribute work across threads or machines. In project used for AI features like text generation, moderation, so client gets response on such endpoints immediately and spreads less resources of server (after of course he can get task result by uuid). For now only ad_text generation and moderation add-on uses celery, but soon we can add more features to do with tasks and scale easily!))

### [Docker & docker compose](https://www.docker.com/)

Forced by organizators :)

### Notes

You may say: "For what we need a lot of complex technologies for now". I have an answer. More complex solutions (at first glance) will really help us to scale in the future and have less pain on refactoring system.

## ➡️ Entrypoints

### Restful API

API Base endpoint when deployed with default docker compose: [127.0.0.1:8080](http://127.0.0.1:8080), also see [docs](#openapi-docs).

### Admin panel

Django admin panel, used for moderation, see [this](#moderation).

### Telegram Bot

Link: [t.me/adnova_bot](https://t.me/adnova_bot)

Basic commands:

/start - Start the bot and authenticate as advertiser

/help - Get list of all commands

/campaigns - Manage advertiser campaigns (only after authentication)

/statistics - See advertiser overall statistics (only after authentication)

/logout - Logout of current advertiser account (only after authentication)

See [this](#telegram-bot-1).

### Grafana

When deployed with default docker compose: [127.0.0.1:13243](http://127.0.0.1:13243). See more details about this [here](#grafana-dashboard).

## ✨ Features

### Notes about basic features

I cache every mlscore in redis (btw, on startup of docker compose i upload each cache in db for stability) and also i cache clicks and impressions count for campaigns. This increases perfomance of suggesting algorithm and increases clients satisfaction!_)

### Clever suggesting algotithm

Here is how suggesting algotitm looks like:

1. Filter all campaigns and left only that currently active and matches user targeting.
2. Filter all campaigns with exceeded impressions, but to make more money i let exceed limit by 10% with chance 25%
3. Creating metrics for each campaign
   1. Profit: cost_per_impression (=0 if already viewed), cost_per_click (=0 if already clicked)
   2. Mlscores: from cache
   3. Capacity: 1 - ((impressions_limit - actual_impressions) / impressions_limit)
4. Normalization
   1. Normalizing profit from 0 to 1
   2. Normalizing mlscores from 0 to 1
   3. Capacity already normalized
5. Scoring each campaign: `0.8 * normalized_profit + 0.4 * normalized_ml + 0.05 * capacity`
6. Finding campaign with max score and returning it to user

### Telegram bot

With this bot you can easily manage your campaigns and see statistics.

Demonstration:

![telegram](./assets/gifs/telegram.gif)

### Campaign image upload

Advertisers can upload images to campaigns and delete with endpoints: `POST /advertisers/{advertiser_id}/campaigns/{campaign_id}/ad_image` and `DELETE /advertisers/{advertiser_id}/campaigns/{campaign_id}/ad_image`, for more details see [docs](#openapi-docs).

![ad_image](./assets/gifs/ad_image.gif)

### Campaign text generation

Advertisers can generate text for their campaigns with their name and campaign title with `/generate/ad_text` endpoint, but it just returns a promise with `task_id` and client can get generation result at `/generate/ad_text/{task_id}/result`, for detailed info see [docs](#openapi-docs).

Prompt used to generate:

```text
Сгенерируй креативный рекламный текст для рекламодателя: "{advertiser_name}", 
который проводит рекламную кампанию с названием: "{ad_title}"

Требования:
1. Текст должен быть максимально привлекательным и продающим
2. Использовать современные маркетинговые приемы
3. Включить призыв к действию
4. Соблюдать структуру: заголовок - основной текст - заключение
5. Длина: 3-6 коротких предложений
6. Ответ должен содержать только текст рекламы без дополнительных комментариев

Пример хорошего текста:
Запустите свой бизнес в космос с {{advertiser_name}}! Кампания "{{ad_title}}" предлагает 
уникальные решения для цифрового продвижения. Присоединяйтесь к лидерам рынка - получите 
персональную консультацию сегодня!
```

Demonstration:

![ad_image generation](./assets/gifs/ad_text-generation.gif)

### Moderation

Moderation implemented via report system. Client goes to `/report` ([see OpenAPI docs](#openapi-docs)) and submits a report, then llm ([YandexGPT-lite](https://yandex.cloud/en/services/yandexgpt)) in task mode (does stuff on the background with Celery) checks for potential violation and sets the `flagged_by_llm` to True or False and this just a little help to moderators to make more accurate decisions. Btw, moderators can do anything they think they should do, for example make some changes, censor some content or even delete campaign.
Also admin user (whoose creditionals specified lower) can add new staff members and even create a specified group for them (this is built-in django capabilities).
Report has four states: Sent, Under review, Took action and Skipped. Admin panel has filtration by states and by flagged by llm status.

Admin panel when deployed with docker compose (by default): [localhost:8080/admin/](http://localhost:8080/admin/)

Reports list when deployed with docker compose (requires authentication): [localhost:8080/admin/campaign/campaignreport/](http://localhost:8080/admin/campaign/campaignreport/)

Default username: `admin`

Default password: `admin`

Prompt used for moderation:

```text
Ты — строгий AI-модератор контента. Анализируй текст ПО ВСЕМ указанным критериям.
Если ЛЮБОЙ из критериев нарушен — верни true. Только если ВСЕ критерии соблюдены — верни false.

Критерии нарушений (true):
1. Нецензурная лексика: мат, эвфемизмы, оскорбительные выражения
2. Угрозы: прямые/косвенные угрозы жизни, шантаж, буллинг
3. Дискриминация: расизм, сексизм, ксенофобия, гомофобия
```

Btw, if llm returns `В интернете есть много сайтов с информацией на эту тему. [Посмотрите, что нашлось в поиске](https://ya.ru)` it also means that text is unacceptable)

Demonstration:

![moderation](./assets/gifs/moderation.gif)

### Grafana dashboard

When deployed with default docker compose: [localhost:13243](http://localhost:13243/)

Default login: `admin`

Default password: `proooooood`

Analytics dashboard when deployed with default docker compose: [localhost:13243/d/adnova-statistics/statistics](http://localhost:13243/d/adnova-statisticss/statistics). You can enter advertiser id and get detailed advertiser statistics and also detailed statistics for each advertiser's campaign.

Demonstration:

![grafana](./assets/gifs/grafana.gif)

### OpenAPI docs

When deployed with default docker compose: [localhost:8080/docs](http://localhost:8080/docs)

### Healthcheck endpoint

When deployed with default docker compose: [localhost:8080/health](http://localhost:8080/health)

Lets developers easily understand and identify problem and users check services health.

![Healthcheck endpoint](./assets/images/healthcheck.png)

### PgAdmin

When deployed with default docker compose: [localhost:13242](http://localhost:13242)

Default email: `admin@mail.com`

Default password: `password`

Default password for existing postgres server: `postgres`

Not enough of basic django admin? Here is pgadmin, which is the most powerfull instrument to manage and administrate your postgres instance. (btw, text is not gpt-generated as it could be seen at first glance).

![PgAdmin](./assets/images/pgadmin.png)

## Testing

You can find out about project tests [here](./tests/README.md).

## Code quality

All Python code linted and formatted with [Ruff](https://astral.sh/ruff) and i tried my best to keep code and architecture clean and simple :)
