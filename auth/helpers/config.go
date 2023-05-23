package helpers

import (
	"log"
	"os"
	"strconv"

	"github.com/joho/godotenv"
)

var AppConfig struct {
	PORT        string
	DB_HOST     string
	DB_PORT     int
	DB_USER     string
	DB_PASSWORD string
	DB_NAME     string
	SECRET_KEY  string
}

func LoadConfig(filename string) {
	err := godotenv.Load(filename)
	if err != nil {
		log.Fatal("Error loading .env file:", err)
		return
	}
	port := os.Getenv("PORT")

	if port == "" {
		port = "8000"
	}

	db_port, _ := strconv.Atoi(os.Getenv("DB_PORT"))

	AppConfig.PORT = port
	AppConfig.DB_HOST = os.Getenv("DB_HOST")
	AppConfig.DB_PORT = db_port
	AppConfig.DB_USER = os.Getenv("POSTGRES_USER")
	AppConfig.DB_PASSWORD = os.Getenv("POSTGRES_PASSWORD")
	AppConfig.DB_NAME = os.Getenv("POSTGRES_DB")
	AppConfig.SECRET_KEY = os.Getenv("SECRET_KEY")

}
