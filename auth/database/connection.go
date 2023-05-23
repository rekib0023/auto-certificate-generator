package database

import (
	"fmt"
	"log"

	"github.com/rekib0023/auth/helpers"
	"github.com/rekib0023/auth/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type DbInstance struct {
	Db *gorm.DB
}

var Database DbInstance

func Connect() {
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=disable", helpers.AppConfig.DB_HOST, helpers.AppConfig.DB_USER, helpers.AppConfig.DB_PASSWORD, helpers.AppConfig.DB_NAME, helpers.AppConfig.DB_PORT)
	fmt.Println(dsn)
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})

	if err != nil {
		panic("Could not connect to the database")
	}

	log.Println("Connected to the database successfully")

	db.Logger = logger.Default.LogMode(logger.Info)

	log.Println("Running Migrations")
	db.AutoMigrate(&models.User{})

	Database = DbInstance{Db: db}
}
