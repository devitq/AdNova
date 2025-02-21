# E2E tests for AdNova

## Prerequisites

Ensure you have the following installed on your system:

- [Python](https://www.python.org/) (>=3.10,<3.12)
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/)
- [Docker compose](https://docs.docker.com/compose/) (latest versions)

## Warning

Plese note that containers will use ports from 13241 to 13245 and 8080, so there is must be no listeners on this ports range.

## Clone the project

```bash
git clone https://gitlab.prodcontest.ru/2025-final-projects-back/devitq.git
```

## Go to the project directory

```bash
cd devitq/solution/tests/e2e
```

## Install dependencies

```bash
uv sync --no-dev
```

## Customize environment

```bash
cp .env.template .env
```

And setup env vars according to your needs.

## Run tests

```bash
uv run pytest .
```

## Results

You will see something like `n passed in Ns`
