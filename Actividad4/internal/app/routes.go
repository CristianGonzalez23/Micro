package app

import (
    "github.com/gin-gonic/gin"
    "gorm.io/gorm"
    "net/http"
    "strconv"
    "time"
)

func SetupRoutes(r *gin.Engine, db *gorm.DB) {
    r.POST("/logs", func(c *gin.Context) {
        var log Log
        if err := c.ShouldBindJSON(&log); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        log.Timestamp = time.Now()
        db.Create(&log)
        c.JSON(http.StatusCreated, log)
    })

    r.GET("/logs", func(c *gin.Context) {
        var logs []Log
        pageStr := c.DefaultQuery("page", "1")
        perPageStr := c.DefaultQuery("per_page", "10")

        page, err := strconv.Atoi(pageStr)
        if err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid page number"})
            return
        }

        perPage, err := strconv.Atoi(perPageStr)
        if err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid per_page number"})
            return
        }

        db.Order("timestamp desc").Offset((page - 1) * perPage).Limit(perPage).Find(&logs)
        c.JSON(http.StatusOK, logs)
    })

    r.GET("/logs/filter", func(c *gin.Context) {
        var logs []Log
        startDate := c.Query("start_date")
        endDate := c.Query("end_date")
        logType := c.Query("log_type")
        application := c.Query("application")

        query := db.Order("timestamp desc")
        if startDate != "" {
            query = query.Where("timestamp >= ?", startDate)
        }
        if endDate != "" {
            query = query.Where("timestamp <= ?", endDate)
        }
        if logType != "" {
            query = query.Where("log_type = ?", logType)
        }
        if application != "" {
            query = query.Where("application = ?", application)
        }
        query.Find(&logs)
        c.JSON(http.StatusOK, logs)
    })
}