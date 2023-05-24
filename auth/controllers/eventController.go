package controllers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Events() gin.HandlerFunc {
	return func(c *gin.Context) {
		var events map[string]interface{}

		if err := c.Bind(&events); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		log.Printf("Received events: %+v", events)
		c.JSON(http.StatusOK, gin.H{"message": "OK"})
	}
}
