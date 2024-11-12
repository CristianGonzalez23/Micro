package main

import (
    "gorm.io/driver/mysql"
    "gorm.io/gorm"
)

var DB *gorm.DB

func ConnectDatabase() {
    dsn := "root:rootpassword@tcp(mysql_db:3306)/mydatabase?charset=utf8mb4&parseTime=True&loc=Local"
    database, err := gorm.Open(mysql.Open(dsn), &gorm.Config{})

    if err != nil {
        panic("Failed to connect to database!")
    }

    database.AutoMigrate(&User{})

    DB = database
}