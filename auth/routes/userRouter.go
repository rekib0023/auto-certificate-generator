package routes

import (
	"github.com/rekib0023/auth/controllers"

	"github.com/gin-gonic/gin"
)

func UserRoutes(incomingRoutes *gin.Engine) {
	incomingRoutes.GET("/api/users", controllers.GetUsers())
	incomingRoutes.GET("/api/users/:userId", controllers.GetUser())
}
