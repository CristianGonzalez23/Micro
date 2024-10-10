package main

import (
    "github.com/gin-gonic/gin"
    "gorm.io/driver/mysql"
    "gorm.io/gorm"
    "log-service/internal/app"
)

func main() {
    dsn := "root:example@tcp(db:3306)/logs?charset=utf8mb4&parseTime=True&loc=Local"
    db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})
    if err != nil {
        panic("failed to connect database")
    }

    app.AutoMigrate(db)

    r := gin.Default()
    app.SetupRoutes(r, db)
    r.Run(":8080")
}