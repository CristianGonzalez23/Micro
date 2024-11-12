package main

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

func UpdateProfile(c *gin.Context) {
    var input User
    if err := c.ShouldBindJSON(&input); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    email := c.Param("email")
    var user User
    if err := DB.Where("email = ?", email).First(&user).Error; err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found!"})
        return
    }

    DB.Model(&user).Updates(input)

    c.JSON(http.StatusOK, gin.H{"data": user})
}