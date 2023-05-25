package routes

import (
	"github.com/rekib0023/auth/controllers"

	"github.com/gin-gonic/gin"
)

func AuthRoutes(incomingRoutes *gin.Engine) {
	incomingRoutes.POST("/api/signup", controllers.Signup())
	incomingRoutes.POST("/api/login", controllers.Login())
	incomingRoutes.GET("/api/refresh-token", controllers.RefreshToken())
	incomingRoutes.POST("/api/verify", controllers.Verify())
}
