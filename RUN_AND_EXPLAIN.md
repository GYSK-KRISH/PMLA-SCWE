# PMLA-SCWE Run and Explain Guide

## 1. Project Meaning

PMLA-SCWE stands for Predictive Micro-Learning Analytics and Student Cyber-Wellbeing Engine.

This project is designed to show how student data can be stored, managed, and analyzed using:

- a database
- a Python application
- basic analytics logic
- attendance tracking
- assessment tracking
- cyber wellness tracking
- sample-data seeding

It is suitable for school project presentations because it combines database design, application logic, and reporting concepts in one package.

## 2. What the Project Contains

### Main parts

- `schema.sql` - creates the database and tables
- `PMLA_SCWE/` - Python application package
- `requirements.txt` - dependency list
- `README.md` - project overview and quick setup
- `documentation/` - extra notes and project material

### Important tables in the database

- `Admin_Login` - stores login accounts for the app
- `Students` - stores student details
- `Learning_Objectives` - stores topic names and learning goals
- `Diagnostic_Logs` - stores assessment/quiz results
- `Cyber_Audit` - stores wellness and cyber-safety scores
- `Weekly_Progress` - stores progress data over time
- `Achievements` - stores badges and rewards
- `Attendance` - stores presence/absence records
- `Activity_Log` - stores system actions
- `Reports_Metadata` - stores report file information

## 3. How the Project Works

The flow is simple:

1. The database schema is created.
2. Sample data is inserted.
3. The Python app connects to the database.
4. The user logs in.
5. The user manages students, attendance, and assessments.
6. The app can later be expanded for analytics, graphs, and reports.

## 4. How to Run the Project Step by Step

## Step 1: Open the workspace

Open the folder `D:\PMLA-SCWE` in VS Code.

## Step 2: Create a virtual environment

Run:

```powershell
python -m venv .venv
```

This creates a private Python environment for the project.

## Step 3: Activate the virtual environment

Run:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, all Python packages are installed only for this project.

## Step 4: Install dependencies

Run:

```powershell
pip install -r requirements.txt
```

The project uses:

- pandas
- matplotlib
- mysql-connector-python

## Step 5: Open MySQL Workbench

Create a new connection with:

- Connection name: `PMLA-SCWE Project Package`
- Hostname: `127.0.0.1`
- Port: `3306`
- Username: `root`
- Password: your MySQL root password
- Default schema: `pmla_scwe`

Important:

- Do not type `127.0.0.1:3306` in the hostname box.
- Put only `127.0.0.1` in hostname and `3306` in port.

## Step 6: Create the schema

Open `schema.sql` in Workbench and run it.

If the schema already exists, you may see a warning about the database already existing. That is normal.

If you want a clean reset before running again, execute:

```sql
DROP DATABASE IF EXISTS pmla_scwe;
CREATE DATABASE pmla_scwe;
USE pmla_scwe;
```

Then run `schema.sql` again.

## Step 7: Seed 100 sample records

Run:

```powershell
python -m PMLA_SCWE.seed_data
```

This adds sample records into the database.

### What the seeder inserts

- 100 students
- diagnostic log rows
- attendance rows
- cyber audit rows
- weekly progress rows
- achievements
- activity log rows
- report metadata rows

## Step 8: Start the application

Run:

```powershell
python -m PMLA_SCWE.main
```

The main menu appears.

## 5. Menu Explanation

### 1. Login

Use this to enter the application.

Default login when no admin exists:

- Username: `admin`
- Password: `admin123`

### 2. Add Student

This option stores student information such as:

- first name
- last name
- class section
- date of birth
- gender
- email
- phone

### 3. List Students

Shows all students currently stored in the database.

### 4. Attendance

This menu has two actions:

- Mark Attendance
- Attendance Percentage

It helps track whether a student was present or absent.

### 5. Assessment

This menu has two actions:

- Add Assessment
- Assessment History

It stores quiz or test scores for each student.

### 9. Exit

Closes the app.

## 6. What To Tell Teachers

If a teacher asks what the project does, explain it like this:

"This project stores student information in a database, allows login and data entry through a Python app, tracks attendance and assessment scores, and is built to be expanded with analytics and reports."

## 7. How To Explain the Database

### Why use a database?

Because student records need to be stored permanently and queried later.

### Why MySQL?

Because MySQL is a standard relational database and is easy to demonstrate in Workbench.

### Why multiple tables?

Because each type of data has a separate purpose:

- student table for personal details
- attendance table for presence tracking
- assessment table for test results
- cyber audit table for wellness tracking
- report table for saved files

## 8. How To Explain the Python App

The Python code acts as the front end for the database.

It:

- shows a menu
- takes user input
- validates data
- saves data to the database
- reads data back for display

## 9. How To Explain Sample Data

The seeder is useful because:

- it creates demo records quickly
- it helps in presentations
- it shows that the system works with realistic data
- it saves time during testing

## 10. SQLite Fallback

If MySQL does not work, the project still runs using SQLite.

This is useful because:

- the app can still be demonstrated
- you do not depend on MySQL every time
- the project is easier to run in limited environments

The fallback file is:

- `pmla_scwe_fallback.db`

## 11. Common Problems and Fixes

### Problem: MySQL connection fails

Check:

- MySQL server is running
- host is `127.0.0.1`
- port is `3306`
- password is correct

### Problem: Unknown database `pmla_scwe`

Fix:

- connect first without a default schema
- run `schema.sql`
- refresh schemas
- set default schema after the database exists

### Problem: Login fails

Fix:

- use the correct username and password
- if needed, use default admin credentials
- make sure the database has an admin record

### Problem: App does not start

Fix:

- activate the virtual environment
- install requirements
- make sure the Python files are not modified incorrectly

## 12. Short Viva Summary

If you need a short answer in an exam or viva, say:

"PMLA-SCWE is a Python and MySQL-based student analytics project that manages student records, attendance, assessments, and cyber wellness data. It uses a relational database, a menu-driven interface, and sample data seeding for demonstration."

## 13. Quick Commands

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m PMLA_SCWE.seed_data
python -m PMLA_SCWE.main
```

## 14. Final Note

If you want to present the project clearly, use this order:

1. project title
2. objective
3. database tables
4. Python menu flow
5. sample data
6. live demo
7. future scope

That sequence makes the project easier to explain to teachers.
