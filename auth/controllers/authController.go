package controllers

import (
	"net/http"
	"time"

	"github.com/rekib0023/auth/database"
	"github.com/rekib0023/auth/helpers"
	"github.com/rekib0023/auth/models"
	"github.com/rekib0023/auth/serializers"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"golang.org/x/crypto/bcrypt"
)

func UserResponse(user models.User) serializers.UserSerializer {
	return serializers.UserSerializer{
		ID:        user.ID,
		FirstName: user.FirstName,
		LastName:  user.LastName,
		Email:     user.Email,
		CreatedAt: user.CreatedAt,
		UpdatedAt: user.UpdatedAt,
	}
}

var validate = validator.New()

func Signup() gin.HandlerFunc {
	return func(c *gin.Context) {
		var existing_user models.User
		var user models.User

		if err := c.Bind(&user); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		if err := validate.Struct(user); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		database.Database.Db.Find(&existing_user, "email = ?", user.Email)

		if existing_user.ID != 0 {
			c.JSON(http.StatusBadRequest, gin.H{"error": "User already exists with this email address"})
			return
		}

		password, _ := hashPassword(string(user.Password))

		user.Password = password

		database.Database.Db.Create(&user)

		accessToken, err := helpers.GenerateToken(&user, "access")

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		refreshToken, err := helpers.GenerateToken(&user, "refresh")

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		responseUser := UserResponse(user)

		helpers.SetCookie(c, "jwt", accessToken, time.Now().Add(time.Hour*1))
		helpers.SetCookie(c, "refresh_token", refreshToken, time.Now().Add(time.Hour*24*7))

		c.JSON(http.StatusCreated, responseUser)
	}
}

func Login() gin.HandlerFunc {
	return func(c *gin.Context) {
		var data map[string]string

		if err := c.Bind(&data); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		if data["email"] == "" || data["password"] == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Please provide email and password"})
			return
		}

		var user models.User

		database.Database.Db.Where("email = ?", data["email"]).First(&user)

		if user.ID == 0 {
			c.JSON(http.StatusNotFound, gin.H{"error": "No user found with this email"})
			return
		}

		if match := checkPasswordHash(data["password"], string(user.Password)); !match {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid Credentials"})
			return
		}

		accessToken, err := helpers.GenerateToken(&user, "access")

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}

		refreshToken, err := helpers.GenerateToken(&user, "refresh")

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}

		responseUser := UserResponse(user)

		helpers.SetCookie(c, "jwt", accessToken, time.Now().Add(time.Hour*1))
		helpers.SetCookie(c, "refresh_token", refreshToken, time.Now().Add(time.Hour*24*7))

		c.JSON(http.StatusOK, responseUser)
	}
}

func RefreshToken() gin.HandlerFunc {
	return func(c *gin.Context) {
		refreshToken, err := c.Cookie("refresh_token")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "missing refresh token"})
			return
		}

		claims, err := helpers.ValidateToken(refreshToken, "refresh")
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid refresh token"})
			return
		}

		var user models.User

		database.Database.Db.Where("ID = ?", claims.UserID).First(&user)

		accessToken, err := helpers.GenerateToken(&user, "access")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to generate access token"})
			return
		}
		helpers.SetCookie(c, "jwt", accessToken, time.Now().Add(time.Hour*1))

		c.JSON(http.StatusOK, gin.H{"message": "access token refreshed successfully"})

	}
}

func Logout() gin.HandlerFunc {
	return func(c *gin.Context) {
		helpers.ClearCookie(c, "jwt")
		helpers.ClearCookie(c, "refresh_token")

		c.JSON(http.StatusOK, gin.H{
			"message": "User logged out successfully",
		})
	}
}

func Verify() gin.HandlerFunc {
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

		c.JSON(http.StatusOK, gin.H{"message": "User verified", "user_id": claims.UserID})
	}
}

func hashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)
	return string(bytes), err
}

func checkPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}
