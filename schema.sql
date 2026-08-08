-- Schema for PMLA-SCWE
CREATE DATABASE IF NOT EXISTS pmla_scwe;
USE pmla_scwe;

-- Admin login
CREATE TABLE IF NOT EXISTS Admin_Login (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login DATETIME
);

-- Students
CREATE TABLE IF NOT EXISTS Students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    class_section VARCHAR(20) NOT NULL,
    dob DATE,
    gender ENUM('M','F','O') DEFAULT 'O',
    email VARCHAR(100),
    phone VARCHAR(20),
    enrollment_date DATE
);

-- Learning objectives / topics
CREATE TABLE IF NOT EXISTS Learning_Objectives (
    objective_id INT PRIMARY KEY AUTO_INCREMENT,
    topic_name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Diagnostic logs / assessments
CREATE TABLE IF NOT EXISTS Diagnostic_Logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    objective_id INT,
    score_obtained FLOAT NOT NULL,
    max_score FLOAT DEFAULT 100,
    test_date DATE,
    time_taken_minutes INT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (objective_id) REFERENCES Learning_Objectives(objective_id) ON DELETE SET NULL
);

-- Cyber audit
CREATE TABLE IF NOT EXISTS Cyber_Audit (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    password_strength INT DEFAULT 0,
    screen_time_hours FLOAT DEFAULT 0,
    netiquette_score INT DEFAULT 0,
    privacy_awareness INT DEFAULT 0,
    e_waste_awareness INT DEFAULT 0,
    wellness_score FLOAT DEFAULT 0,
    audit_date DATE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);

-- Weekly progress
CREATE TABLE IF NOT EXISTS Weekly_Progress (
    week_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    week_start DATE NOT NULL,
    score FLOAT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);

-- Achievements / badges
CREATE TABLE IF NOT EXISTS Achievements (
    achievement_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    badge_name VARCHAR(100) NOT NULL,
    date_awarded DATE,
    remarks VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);

-- Attendance
CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('P','A') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);

-- Activity log
CREATE TABLE IF NOT EXISTS Activity_Log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    activity VARCHAR(255) NOT NULL,
    activity_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Reports metadata
CREATE TABLE IF NOT EXISTS Reports_Metadata (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    report_type VARCHAR(50) NOT NULL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE SET NULL
);
