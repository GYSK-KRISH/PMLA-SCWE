-- ============================================================================
-- PMLA-SCWE DATABASE DDL SCHEMA (ROOT COMPATIBILITY MIRROR)
-- File: schema.sql (Mirror of authoritative source: database/schema.sql)
-- Checkpoint: Version 2.0 Phase 1 (Multi-School Tenancy & RBAC Foundation)
-- Note: Authoritative schema definition is maintained in database/schema.sql.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS pmla_scwe;
USE pmla_scwe;

-- Schema Migrations Tracking Table
CREATE TABLE IF NOT EXISTS Schema_Migrations (
    migration_id INT PRIMARY KEY AUTO_INCREMENT,
    version VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64),
    status VARCHAR(20) DEFAULT 'SUCCESS'
);

-- Organizations Table (Multi-tenancy Root)
CREATE TABLE IF NOT EXISTS Organizations (
    organization_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Schools Table (Tenant Unit)
CREATE TABLE IF NOT EXISTS Schools (
    school_id INT PRIMARY KEY AUTO_INCREMENT,
    organization_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    is_active INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE CASCADE
);

-- Admin login (Legacy compatibility)
CREATE TABLE IF NOT EXISTS Admin_Login (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login DATETIME
);

-- Students
CREATE TABLE IF NOT EXISTS Students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    school_id INT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    class_section VARCHAR(20) NOT NULL,
    dob DATE,
    gender ENUM('M','F','O') DEFAULT 'O',
    email VARCHAR(100),
    phone VARCHAR(20),
    enrollment_date DATE,
    FOREIGN KEY (school_id) REFERENCES Schools(school_id) ON DELETE SET NULL
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
    daily_screen_time FLOAT DEFAULT 0,
    study_screen_time FLOAT DEFAULT 0,
    recreational_screen_time FLOAT DEFAULT 0,
    sleep_duration FLOAT DEFAULT 8,
    digital_distraction_level INT DEFAULT 0,
    cyber_safety_awareness INT DEFAULT 0,
    netiquette_score INT DEFAULT 0,
    privacy_awareness INT DEFAULT 0,
    e_waste_awareness INT DEFAULT 0,
    wellness_score FLOAT DEFAULT 0,
    audit_date DATE,
    remarks VARCHAR(255),
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

-- Multi-user Access Accounts & Tenant Context
CREATE TABLE IF NOT EXISTS Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'Teacher',
    status VARCHAR(20) DEFAULT 'Active',
    is_active INT DEFAULT 1,
    organization_id INT,
    school_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE SET NULL,
    FOREIGN KEY (school_id) REFERENCES Schools(school_id) ON DELETE SET NULL
);

-- System Notifications and Alerts Center (v1.6/v1.7)
CREATE TABLE IF NOT EXISTS Notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    alert_type VARCHAR(50) DEFAULT 'SYSTEM',
    priority VARCHAR(20) DEFAULT 'INFO',
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read INT DEFAULT 0,
    source VARCHAR(50) DEFAULT 'Analytics Engine',
    dedup_key VARCHAR(150),
    action_status VARCHAR(30) DEFAULT 'OPEN',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE SET NULL
);

-- Version 1.6: Teacher Interventions & Outcome Tracking
CREATE TABLE IF NOT EXISTS Interventions (
    intervention_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    risk_factor VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) DEFAULT 'Remedial Practice',
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'PENDING',
    assigned_date DATE NOT NULL,
    target_date DATE,
    completed_date DATE,
    teacher_notes TEXT,
    pre_academic_score FLOAT,
    post_academic_score FLOAT,
    pre_attendance_rate FLOAT,
    post_attendance_rate FLOAT,
    pre_risk_score FLOAT,
    post_risk_score FLOAT,
    pre_lhs_score FLOAT,
    post_lhs_score FLOAT,
    effectiveness_score FLOAT,
    effectiveness_tier VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
