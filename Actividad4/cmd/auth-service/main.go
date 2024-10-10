package main

import (
    "bytes"
    "encoding/json"
    "log"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/streadway/amqp"
)

type Log struct {
    Application string    `json:"application"`
    LogType     string    `json:"log_type"`
    Module      string    `json:"module"`
    Timestamp   time.Time `json:"timestamp"`
    Summary     string    `json:"summary"`
    Description string    `json:"description"`
}

func createLog(l Log) {
    l.Timestamp = time.Now()
    jsonValue, err := json.Marshal(l)
    if err != nil {
        log.Println("Failed to marshal log:", err)
        return
    }
    _, err = http.Post("http://log-service:8080/logs", "application/json", bytes.NewBuffer(jsonValue))
    if err != nil {
        log.Println("Failed to create log:", err)
    }
}

func publishMessage(message string) {
    conn, err := amqp.Dial("amqp://guest:guest@rabbitmq:5672/")
    if err != nil {
        log.Fatalf("Failed to connect to RabbitMQ: %s", err)
    }
    defer conn.Close()

    ch, err := conn.Channel()
    if err != nil {
        log.Fatalf("Failed to open a channel: %s", err)
    }
    defer ch.Close()

    q, err := ch.QueueDeclare(
        "auth_logs",
        false,
        false,
        false,
        false,
        nil,
    )
    if err != nil {
        log.Fatalf("Failed to declare a queue: %s", err)
    }

    err = ch.Publish(
        "",
        q.Name,
        false,
        false,
        amqp.Publishing{
            ContentType: "text/plain",
            Body:        []byte(message),
        },
    )
    if err != nil {
        log.Fatalf("Failed to publish a message: %s", err)
    }
}

func main() {
    r := gin.Default()

    r.POST("/register", func(c *gin.Context) {
        // Registro de usuario
        log := Log{
            Application: "AuthService",
            LogType:     "INFO",
            Module:      "UserRegistration",
            Summary:     "User registered",
            Description: "A new user has been registered.",
        }
        createLog(log)
        publishMessage("User registered")
        c.JSON(http.StatusOK, gin.H{"message": "User registered"})
    })

    r.POST("/login", func(c *gin.Context) {
        // Login de usuario
        log := Log{
            Application: "AuthService",
            LogType:     "INFO",
            Module:      "UserLogin",
            Summary:     "User login",
            Description: "A user has logged in.",
        }
        createLog(log)
        publishMessage("User login")
        c.JSON(http.StatusOK, gin.H{"message": "User logged in"})
    })

    r.POST("/recover", func(c *gin.Context) {
        // Recuperación de credenciales
        log := Log{
            Application: "AuthService",
            LogType:     "INFO",
            Module:      "PasswordRecovery",
            Summary:     "Password recovery",
            Description: "A user has requested password recovery.",
        }
        createLog(log)
        publishMessage("Password recovery requested")
        c.JSON(http.StatusOK, gin.H{"message": "Password recovery requested"})
    })

    r.Run(":8081")
}