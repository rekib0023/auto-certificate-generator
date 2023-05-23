package middleware

import (
	"github.com/rekib0023/auth/helpers"
	"net/http"

	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		jwt_token, err := c.Cookie("jwt")
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			return
		}

		claims, err := helpers.ValidateToken(jwt_token, "access")

		if err != nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}

		c.Set("userID", claims.UserID)
		c.Next()
	}
}
