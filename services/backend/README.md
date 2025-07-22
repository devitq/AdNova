# AdNova Backend

## Prerequisites

Ensure you have the following installed on your system:

- [Python](https://www.python.org/) (>=3.10,<3.14)
- [uv](https://docs.astral.sh/uv/) (latest version recommended)
- [Docker](https://www.docker.com/) (for containerized setup, latest version recommended)

## Basic setup

### Installation

#### Clone the project

#### Go to the project directory

```bash
cd AdNova/services/backend
```

#### Customize environment

```bash
cp .env.template .env
```

And setup env vars according to your needs.

#### Install dependencies

##### For dev environment

```bash
uv sync --all-extras
```

##### For prod environment

```bash
uv sync --no-dev
```

#### Running

##### Apply migrations

```bash
uv run python manage.py migrate
```

##### Start celery worker

```bash
celery -A config worker -l INFO
```

##### Start server

In dev mode:

```bash
uv run python manage.py runserver
```

In prod mode:

```bash
uv run gunicorn config.wsgi
```

## Containerized setup

### Clone the project

### Go to the project directory

```bash
cd AdNova/services/backend
```

### Build docker image

```bash
docker build -t adnova-backend .
```

### Customize environment

Customize environment with `docker run` command (or bind .env file to container), for all environment vars and default values see [.env.template](./.env.template).

### Run docker image

#### Backend

```bash
docker run -p 8080:8080 --name adnova-backend adnova-backend
```

#### Celery worker

```bash
docker run --name adnova-celery-worker adnova-backend celery -A config worker -l INFO
```

Backend will be available on [127.0.0.1:8080](http://127.0.0.1:8080).

## Testing

### Clone the project

### Go to the project directory

```bash
cd AdNova/services/backend
```

### Install dependencies

```bash
uv sync --all-extras
```

### Run tests

```bash
uv run coverage run --source="." manage.py test
```

### Check coverage

```bash
uv run coverage report
```
