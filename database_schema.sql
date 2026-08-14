-- MySQL Database Schema for Writing Feedback Portal
-- This schema corresponds to the Django models in the application

-- Create database
CREATE DATABASE IF NOT EXISTS writing_feedback CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE writing_feedback;

-- Django's built-in tables for authentication system
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(128) NOT NULL,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    last_login DATETIME,
    date_joined DATETIME NOT NULL,
    INDEX auth_user_username_idx (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL UNIQUE,
    UNIQUE KEY auth_permission_content_type_id_codename_key (content_type_id, codename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_group_permissions_group_id_permission_id_key (group_id, permission_id),
    FOREIGN KEY (group_id) REFERENCES auth_group(id),
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY auth_user_groups_user_id_group_id_key (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (group_id) REFERENCES auth_group(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_user_user_permissions_user_id_permission_id_key (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Django's content type table
CREATE TABLE IF NOT EXISTS django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model_key (app_label, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Django's session table
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME NOT NULL,
    INDEX django_session_expire_date_idx (expire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Django's migration table
CREATE TABLE IF NOT EXISTS django_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL,
    UNIQUE KEY django_migrations_app_name_key (app, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Custom UserProfile table
CREATE TABLE IF NOT EXISTS main_userprofile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT main_userprofile_role_check CHECK (role IN ('student', 'teacher', 'institution'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- EssaySubmission table
CREATE TABLE IF NOT EXISTS main_essaysubmission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    pdf_file VARCHAR(100),
    score INT NOT NULL DEFAULT 0,
    feedback TEXT,
    created_at DATETIME NOT NULL,
    student_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    INDEX main_essaysubmission_student_id_idx (student_id),
    INDEX main_essaysubmission_created_at_idx (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default content types for Django's built-in models
INSERT INTO django_content_type (app_label, model) VALUES
('auth', 'permission'),
('auth', 'group'),
('auth', 'user'),
('contenttypes', 'contenttype'),
('sessions', 'session')
ON DUPLICATE KEY UPDATE model=VALUES(model);

-- Insert default permissions (simplified set)
INSERT INTO auth_permission (name, content_type_id, codename) VALUES
('Can add permission', 1, 'add_permission'),
('Can change permission', 1, 'change_permission'),
('Can delete permission', 1, 'delete_permission'),
('Can view permission', 1, 'view_permission'),
('Can add group', 2, 'add_group'),
('Can change group', 2, 'change_group'),
('Can delete group', 2, 'delete_group'),
('Can view group', 2, 'view_group'),
('Can add user', 3, 'add_user'),
('Can change user', 3, 'change_user'),
('Can delete user', 3, 'delete_user'),
('Can view user', 3, 'view_user')
ON DUPLICATE KEY UPDATE name=VALUES(name);
