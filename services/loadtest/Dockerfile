ARG GOARCH=amd64

# Stage 1: Build go binary
FROM docker.io/golang:1.24-alpine AS build

WORKDIR /build

COPY . .

RUN go mod download

ARG GOARCH

RUN CGO_ENABLED=0 GOARCH=$GOARCH go build -o loadtest


# Stage 2: Run go binary
FROM docker.io/alpine:3.22

WORKDIR /app

COPY --from=build /build/loadtest .

COPY . .

EXPOSE 5001

CMD [ "./loadtest", "--port", "5001" ]
