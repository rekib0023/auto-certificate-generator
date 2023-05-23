package helpers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

func SetCookie(c *gin.Context, name string, value string, expiration time.Time) {
	cookie := buildCookie(name, value, expiration.Second())
	http.SetCookie(c.Writer, cookie)
}

func ClearCookie(c *gin.Context, name string) {
	cookie := buildCookie(name, "", -1)

	http.SetCookie(c.Writer, cookie)
}

func buildCookie(name string, value string, expires int) *http.Cookie {

	cookie := &http.Cookie{
		Name:     name,
		Value:    value,
		Path:     "/",
		HttpOnly: true,
		MaxAge:   expires,
	}

	return cookie
}
