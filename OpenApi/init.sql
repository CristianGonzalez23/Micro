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
INSERT INTO usuarios (nombre, email, password, is_deleted, last_login) VALUES
('John Doe', 'john.doe@example.com', 'password1', FALSE, NOW()),
('Emily Smith', 'emily.smith@example.com', 'password2', FALSE, NOW()),
('Michael Johnson', 'michael.johnson@example.com', 'password3', FALSE, NOW()),
('Sophia Williams', 'sophia.williams@example.com', 'password4', FALSE, NOW()),
('David Brown', 'david.brown@example.com', 'password5', FALSE, NOW()),
('Olivia Jones', 'olivia.jones@random.com', 'pass123', FALSE, NOW()),
('William Miller', 'william.miller@random.com', 'qwerty01', FALSE, NOW()),
('Ashley Hernandez', 'ashley.hernandez@random.com', 'secret123', FALSE, NOW()),
('Charles Garcia', 'charles.garcia@random.com', '!@#$%^,', FALSE, NOW()),
('Jessica Moore', 'jessica.moore@random.com', 'welcome123', FALSE, NOW()),
('Christopher Taylor', 'christopher.taylor@random.com', 'dragonfire', FALSE, NOW()),
('Amanda Davis', 'amanda.davis@random.com', 'sunshine1', FALSE, NOW()),
('Daniel Martin', 'daniel.martin@random.com', 'player1', FALSE, NOW()),
('Sarah Allen', 'sarah.allen@random.com', 'hello123', FALSE, NOW()),
('Nicholas Rodriguez', 'nicholas.rodriguez@random.com', 'password007', FALSE, NOW());