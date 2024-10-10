FROM golang:1.17-alpine

WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY . ./

RUN apk add --no-cache gcc musl-dev
RUN go build -o /log-service cmd/log-service/main.go

EXPOSE 8080

CMD ["/log-service"]