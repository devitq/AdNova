# AdNova Telegram Bot

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
cd AdNova/services/telegram_bot
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

```bash
uv run python main.py
```

## Containerized setup

### Clone the project

### Go to the project directory

```bash
cd AdNova/services/telegram_bot
```

### Build docker image

```bash
docker build -t adnova-telegram_bot .
```

### Customize environment

Customize environment with `docker run` command (or bind .env file to container), for all environment vars and default values see [.env.template](./.env.template).

### Run docker image

```bash
docker run --name adnova-telegram_bot adnova-telegram_bot
```
