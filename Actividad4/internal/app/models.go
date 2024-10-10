package app

import (
    "gorm.io/gorm"
    "time"
)

type Log struct {
    ID          uint      `gorm:"primaryKey"`
    Application string    `json:"application"`
    LogType     string    `json:"log_type"`
    Module      string    `json:"module"`
    Timestamp   time.Time `json:"timestamp"`
    Summary     string    `json:"summary"`
    Description string    `json:"description"`
}

func AutoMigrate(db *gorm.DB) {
    db.AutoMigrate(&Log{})
}