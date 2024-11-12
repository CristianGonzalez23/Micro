package main

import (
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    ConnectDatabase()

    r.PUT("/profile/:email", UpdateProfile)

    r.Run(":8086")
}