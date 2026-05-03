CREATE DATABASE IF NOT EXISTS taskdb;
USE taskdb;

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority ENUM('High', 'Medium', 'Low') DEFAULT 'Medium',
    status ENUM('Pending', 'In Progress', 'Done') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data so tests have something to work with
INSERT INTO tasks (title, description, priority, status) VALUES
('Submit Assignment 1', 'DevOps lab report submission', 'High', 'Done'),
('Study for Midterm', 'Cover Docker and Jenkins chapters', 'High', 'In Progress'),
('Read Flask Docs', 'Official Flask documentation review', 'Medium', 'Pending');
