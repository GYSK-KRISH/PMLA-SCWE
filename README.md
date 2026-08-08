# PMLA-SCWE

Predictive Micro-Learning Analytics and Student Cyber-Wellbeing Engine.

PMLA-SCWE is a school analytics project package built for CBSE-style project work. It combines a MySQL-backed data model, a modular Python application, and supporting documentation for students, teachers, and evaluators.

If you want the full step-by-step version that explains how to run the project and how to present it in viva, open [RUN_AND_EXPLAIN.md](RUN_AND_EXPLAIN.md).

## What This Project Does

The project currently supports:

- student management
- login and authentication
- attendance tracking
- assessment entry and history
- basic analytics scaffolding
- schema creation and sample data seeding
- SQLite fallback when MySQL is not available

The long-term package also includes reporting, graphs, export utilities, and teacher-facing analytics views.

## Project Structure

- `PMLA_SCWE/` - Python package containing the application code
- `schema.sql` - MySQL schema for the project database
- `requirements.txt` - Python dependencies
- `documentation/` - project notes, connection instructions, and report material

## Requirements

- Python 3.15 or compatible Python 3.x installation
- MySQL Server if you want to use the MySQL connection path
- MySQL Workbench for schema setup and manual inspection
- Python packages listed in `requirements.txt`

### Python dependencies

The project uses:

- pandas
- matplotlib
- mysql-connector-python

## Database Overview

The database name used by the project is `pmla_scwe`.

Main tables include:

- `Admin_Login`
- `Students`
- `Learning_Objectives`
- `Diagnostic_Logs`
- `Cyber_Audit`
- `Weekly_Progress`
- `Achievements`
- `Attendance`
- `Activity_Log`
- `Reports_Metadata`

## MySQL Workbench Setup

Use these values when creating the connection in MySQL Workbench:

- Connection Name: `PMLA-SCWE Project Package`
- Hostname: `127.0.0.1` or `localhost`
- Port: `3306`
- Username: `root`
- Password: your local MySQL root password
- Default Schema: `pmla_scwe`

Important notes:

- Do not put `:3306` inside the Hostname field.
- If Workbench says the database is unknown, leave Default Schema blank for the first connection test.
- Run `schema.sql` first to create the database and tables.

## Setup Instructions

### 1. Clone or open the workspace

Open the project folder in VS Code or your preferred editor.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

If your Python installation blocks direct package changes, install into the project virtual environment instead.

### 5. Create the database schema

Open `schema.sql` in MySQL Workbench or run it from the SQL editor. The script creates the `pmla_scwe` database and all tables.

If you want to reset the database before rerunning the schema:

```sql
DROP DATABASE IF EXISTS pmla_scwe;
CREATE DATABASE pmla_scwe;
USE pmla_scwe;
```

### 6. Seed sample data

To load 100 sample students and related rows, run:

```powershell
python -m PMLA_SCWE.seed_data
```

This seeds:

- 100 students
- 100 diagnostic log rows
- 100 attendance rows
- 100 cyber audit rows
- 100 weekly progress rows
- report metadata rows
- activity log rows
- sample achievements

## Running the App

Start the menu application with:

```powershell
python -m PMLA_SCWE.main
```

When the app starts, it shows the main menu:

- Login
- Add Student
- List Students
- Attendance
- Assessment
- Exit

## Default App Login

The application creates a default admin account when no admin exists yet.

- Username: `admin`
- Password: `admin123`

## Main Menu Features

### Login

Logs into the application using the admin credentials stored in the database.

### Add Student

Adds a student record with:

- first name
- last name
- class or section
- date of birth
- gender
- email
- phone

### List Students

Displays the students currently stored in the database.

### Attendance

Provides options to:

- mark attendance
- calculate attendance percentage

### Assessment

Provides options to:

- add a diagnostic assessment
- view assessment history

## SQLite Fallback

If MySQL is not available, the application falls back to a local SQLite database file named `pmla_scwe_fallback.db`.

This lets you run and test the app even when the MySQL connector or MySQL server is unavailable.

## Sample Data Helper

The file `PMLA_SCWE/seed_data.py` loads bulk sample data into the current database.

You can rerun it safely. It will fill missing sample rows and keep the app data usable for demonstrations.

## Documentation Folder

The `documentation/` folder contains extra notes, including MySQL Workbench connection instructions and project documentation content.

## Troubleshooting

### MySQL connection fails

- Check that MySQL Server is running.
- Confirm the host is `127.0.0.1`.
- Confirm the port is `3306`.
- Confirm the root password is correct.

### Unknown database error

If Workbench says `Unknown database 'pmla_scwe'`, connect first without setting a default schema, then run `schema.sql`.

### Login does not work

- Make sure the database contains an admin row.
- Use the default login `admin / admin123` if no admin has been created yet.

### App starts but MySQL is unavailable

The SQLite fallback should still allow the app to run. Check the generated file `pmla_scwe_fallback.db` in the project root.

## Current Status

The project is now functional with:

- schema creation
- MySQL Workbench setup
- database fallback support
- working login
- student CRUD basics
- attendance and assessment features
- sample data seeding

Next development areas are analytics, graphing, reporting, and export workflows.
