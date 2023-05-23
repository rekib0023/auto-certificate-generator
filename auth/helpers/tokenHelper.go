package helpers

import (
	"errors"
	"fmt"
	"github.com/rekib0023/auth/models"
	"time"

	"github.com/dgrijalva/jwt-go"
)

type Claims struct {
	UserID uint   `json:"user_id"`
	Email  string `json:"email"`
	jwt.StandardClaims
}

func GenerateToken(user *models.User, tokenType string) (string, error) {
	var expirationTime int64
	var subject string

	if tokenType == "access" {
		expirationTime = time.Now().Add(time.Hour * 1).Unix() // expire in 1 hour
	} else if tokenType == "refresh" {
		expirationTime = time.Now().Add(time.Hour * 24 * 7).Unix() // expire in 7 days
		subject = "refresh"
	}

	claims := &Claims{
		UserID: user.ID,
		Email:  user.Email,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime,
			Issuer:    "myapp",
			Subject:   subject,
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	accessToken, err := token.SignedString([]byte(AppConfig.SECRET_KEY))

	if err != nil {
		return "", err
	}

	return accessToken, nil
}

func ValidateToken(tokenString string, tokenType string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("invalid token signing method")
		}
		return []byte(AppConfig.SECRET_KEY), nil
	})
	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, errors.New("invalid token")
	}

	if tokenType == "refresh" && claims.Subject != "refresh" {
		return nil, errors.New("invalid token")
	}

	return claims, nil
}
