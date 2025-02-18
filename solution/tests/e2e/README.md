# E2E tests for AdNova

## Prerequisites

Ensure you have the following installed on your system:

- [Python](https://www.python.org/) (>=3.10,<3.12)
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/)
- [Docker compose](https://docs.docker.com/compose/)

## Warning

Plese note that containers will use ports 13241 to 13246 and 8080, so there is must be no listeners on this ports range.

## Install dependencies

```bash
uv sync --no-dev
```

### Customize environment

Customize environment with `docker run` command (or bind .env file to container), for all environment vars and default values see [.env.template](./.env.template).

## Run tests

```bash
uv run pytest .
```
