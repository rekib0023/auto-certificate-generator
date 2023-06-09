package controllers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Event struct {
	Type string                 `json:"type"`
	Data map[string]interface{} `json:"data"`
}

func Events() gin.HandlerFunc {
	return func(c *gin.Context) {
		var events Event

		if err := c.Bind(&events); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}
		log.Printf("Received events: %+v", events)
		c.JSON(http.StatusOK, gin.H{"message": "OK"})
	}
}
