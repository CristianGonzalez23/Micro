-- init.sql

-- Eliminar la base de datos si existe
DROP DATABASE IF EXISTS mydatabase;

-- Crear la base de datos
CREATE DATABASE mydatabase;

-- Usar la base de datos
USE mydatabase;

-- Crear la tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP
);