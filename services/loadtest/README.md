# AdNova Loadtest

## Prerequisites

Ensure you have the following installed on your system:

- [Go](https://go.dev/) (1.24 recommended)
- [Docker](https://www.docker.com/) (for containerized setup, latest version recommended)

## Basic setup

### Installation

#### Clone the project

#### Go to the project directory

```bash
cd AdNova/services/loadtest
```

#### Customize environment

```bash
cp .env.template .env
```

And setup env vars according to your needs.

#### Install dependencies

```bash
go mod download
```

#### Running

```bash
go run main.go
```

## Containerized setup

### Clone the project

### Go to the project directory

```bash
cd AdNova/services/loadtest
```

### Build docker image

```bash
docker build -t adnova-loadtest .
```

### Customize environment

Customize environment with `docker run` command, for all environment vars and default values see [.env.template](./.env.template).

### Run docker image

```bash
docker run -p 5001:5001 --name adnova-loadtest adnova-loadtest
```

Loadtest will be available on [127.0.0.1:5001](http://127.0.0.1:5001).
