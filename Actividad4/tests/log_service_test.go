package tests

import (
    "bytes"
    "encoding/json"
    "log-service/internal/app"
    "net/http"
    "net/http/httptest"
    "testing"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
)

func setupRouter() *gin.Engine {
    r := gin.Default()
    dsn := "file::memory:?cache=shared"
    db, err := gorm.Open(sqlite.Open(dsn), &gorm.Config{})
    if err != nil {
        panic("failed to connect database")
    }
    app.AutoMigrate(db)
    app.SetupRoutes(r, db)
    return r
}

func TestCreateLog(t *testing.T) {
    router := setupRouter()

    log := app.Log{
        Application: "TestApp",
        LogType:     "INFO",
        Module:      "TestModule",
        Summary:     "Test Summary",
        Description: "Test Description",
    }
    jsonValue, _ := json.Marshal(log)
    req, _ := http.NewRequest("POST", "/logs", bytes.NewBuffer(jsonValue))
    req.Header.Set("Content-Type", "application/json")

    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusCreated, w.Code)
}

func TestGetLogs(t *testing.T) {
    router := setupRouter()

    // Create a log entry
    log := app.Log{
        Application: "TestApp",
        LogType:     "INFO",
        Module:      "TestModule",
        Summary:     "Test Summary",
        Description: "Test Description",
        Timestamp:   time.Now(),
    }
    jsonValue, _ := json.Marshal(log)
    req, _ := http.NewRequest("POST", "/logs", bytes.NewBuffer(jsonValue))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    // Get logs
    req, _ = http.NewRequest("GET", "/logs", nil)
    w = httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)
    var logs []app.Log
    err := json.Unmarshal(w.Body.Bytes(), &logs)
    assert.Nil(t, err)
    assert.NotEmpty(t, logs)
}

func TestFilterLogs(t *testing.T){}
	err = ch.Publish(
        "",
        q.Name,
        false,
        false,
        amqp.Publishing{
            ContentType: "text/plain",
            Body:        []byte(message),
        })
    if err != nil {
        log.Fatalf("Failed to publish a message: %s", err)
    }
    log.Printf(" [x] Sent %s", message)
}