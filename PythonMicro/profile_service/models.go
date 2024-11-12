package main

type User struct {
	ID            uint   `gorm:"primaryKey"`
	Username      string `gorm:"unique;not null"`
	Email         string `gorm:"unique;not null"`
	PasswordHash  string `gorm:"not null"`
	CreatedAt     string
	UpdatedAt     string
	PersonalPage  string
	Nickname      string
	ContactPublic bool
	Address       string
	Biography     string
	Organization  string
	Country       string
	SocialLinks   string `gorm:"type:json"`
}
