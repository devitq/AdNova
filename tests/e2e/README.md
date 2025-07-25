# E2E tests for AdNova

## Prerequisites

Ensure you have the following installed on your system:

- [Python](https://www.python.org/) (>=3.10,<3.14)
- [uv](https://docs.astral.sh/uv/) (latest version recommended)
- [Docker](https://www.docker.com/) (latest version recommended)
- [Docker compose](https://docs.docker.com/compose/) (latest version recommended)

## Warning

Please note that containers will use ports from 13240 to 13248, so there is must be no listeners on this ports range.

## Setup

### Clone the project

### Go to the project directory

```bash
cd AdNova/tests/e2e
```

### Install dependencies

```bash
uv sync --no-dev
```

### Customize environment (optional)

```bash
cp .env.template .env
```

And setup env vars according to your needs.

### Run tests

```bash
uv run pytest .
```

### Results

You will see something like `n passed in Ns`
