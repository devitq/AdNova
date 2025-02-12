# AdNova Backend

## Prerequisites

Ensure you have the following installed on your system:

- [Python](https://www.python.org/) (>=3.10,<3.12)
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/) (for containerized setup)

## Basic setup

### Installation

#### Clone the project

```bash
git clone https://gitlab.prodcontest.ru/2025-final-projects-back/devitq.git
```

#### Go to the project directory

```bash
cd devitq/solution/services/backend
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

##### In dev mode

Apply migrations:

```bash
uv run python manage.py migrate
```

Start project:

```bash
uv run python manage.py runserver
```

##### In prod mode

Apply migrations:

```bash
uv run python manage.py migrate
```

Start project:

```bash
uv run gunicorn config.wsgi
```

## Containerized setup

### Clone the project

```bash
git clone https://gitlab.prodcontest.ru/2025-final-projects-back/devitq.git
```

### Go to the project directory

```bash
cd devitq/solution/services/backend
```

### Build docker image

```bash
docker build -t adnova-backend .
```

### Customize environment

Customize environment with `docker run` command (or bind .env file to container), for all environment vars and default values see [.env.template](./.env.template).

### Run docker image

```bash
docker run -p 8080:8080 --name adnova-backend adnova-backend
```

Backend will be available on localhost:8080.
