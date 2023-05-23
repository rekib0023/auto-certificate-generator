FROM golang:1.20-alpine

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . ./

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o /auth

EXPOSE 5001

ENTRYPOINT ["/auth"]
