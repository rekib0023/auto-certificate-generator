package controllers

import (
	"github.com/rekib0023/auth/database"
	"github.com/rekib0023/auth/models"
	"github.com/rekib0023/auth/serializers"
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetUsers() gin.HandlerFunc {
	return func(c *gin.Context) {
		var users []models.User

		if err := database.Database.Db.Find(&users); err.Error != nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "Error while querying database"})
			return
		}

		var responseUsers []serializers.UserSerializer

		for _, user := range users {
			responseUsers = append(responseUsers, UserResponse(user))
		}

		c.JSON(http.StatusOK, responseUsers)
	}
}

func GetUser() gin.HandlerFunc {
	return func(c *gin.Context) {
		userId := c.Param("userId")
		var user models.User

		database.Database.Db.Where("ID = ?", userId).First(&user)

		if user.ID == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No user found with the given ID"})
			return
		}

		responseUser := UserResponse(user)

		c.JSON(http.StatusOK, responseUser)
	}
}
