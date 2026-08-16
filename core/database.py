from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
import os
import re
import sqlite3

try:
    import mysql.connector
except Exception:  # pragma: no cover - optional dependency
    mysql = None
    _HAS_MYSQL = False
else:  # pragma: no cover - optional dependency
    _HAS_MYSQL = True

from .config import DATABASE_CONFIG


@dataclass(slots=True)
class DatabaseConnectionInfo:
    host: str
    user: str
    password: str
    database: str
    port: int


_SQLITE_DB_PATH = Path(__file__).resolve().parent.parent / "pmla_scwe_fallback.db"


def get_connection_info() -> DatabaseConnectionInfo:
    return DatabaseConnectionInfo(**DATABASE_CONFIG)


def _sqlite_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _mysql_connection(database: str | None = None):
    if not _HAS_MYSQL:
        raise RuntimeError("mysql-connector-python is not available in this environment")
    cfg = get_connection_info()
    connect_kwargs: dict[str, Any] = {
        "host": cfg.host,
        "user": cfg.user,
        "password": cfg.password,
        "port": cfg.port,
        "autocommit": False,
    }
    if database:
        connect_kwargs["database"] = database
    return mysql.connector.connect(**connect_kwargs)


def get_connection():
    """Return a live database connection.

    Uses MySQL when the connector is installed and server is reachable; otherwise falls back to SQLite.
    """
    if _HAS_MYSQL:
        cfg = get_connection_info()
        try:
            return _mysql_connection(cfg.database)
        except Exception:
            # Fall back to SQLite when MySQL is unavailable or unreachable.
            pass
    return _sqlite_connection()


def get_db_status() -> dict[str, Any]:
    """Return status details of the database connection for frontends."""
    mysql_available = _HAS_MYSQL
    mysql_reachable = False
    
    if mysql_available:
        try:
            conn = _mysql_connection(get_connection_info().database)
            conn.close()
            mysql_reachable = True
        except Exception:
            pass
            
    if mysql_reachable:
        return {
            "backend": "MySQL",
            "mode": "Primary",
            "available": True,
            "display": "Database: MySQL (Primary)"
        }
    else:
        sqlite_available = True
        try:
            conn = _sqlite_connection()
            conn.close()
        except Exception:
            sqlite_available = False
            
        return {
            "backend": "SQLite",
            "mode": "Fallback Mode",
            "available": sqlite_available,
            "display": "Database: SQLite (Fallback Mode)"
        }


def _normalize_sql_for_sqlite(query: str) -> str:
    q = query
    q = q.replace("%s", "?")
    q = re.sub(r"\bAUTO_INCREMENT\b", "AUTOINCREMENT", q, flags=re.IGNORECASE)
    q = re.sub(r"\bINT\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b", "INTEGER PRIMARY KEY AUTOINCREMENT", q, flags=re.IGNORECASE)
    q = re.sub(r"\bDATETIME\s+DEFAULT\s+CURRENT_TIMESTAMP\b", "TEXT DEFAULT CURRENT_TIMESTAMP", q, flags=re.IGNORECASE)
    q = re.sub(r"\bDATE\b", "TEXT", q)
    q = q.replace("ENUM('P','A')", "TEXT")
    q = q.replace("ENUM('M','F','O')", "TEXT")
    return q


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, sqlite3.Row):
        return dict(row)
    if isinstance(row, dict):
        return row
    if hasattr(row, "_asdict"):
        return row._asdict()
    return {f"col_{index}": value for index, value in enumerate(row)}


def execute_query(query: str, parameters: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    """Execute a SELECT-style query and return rows as dictionaries."""
    params = tuple(parameters or ())
    if _HAS_MYSQL:
        use_sqlite = False
        try:
            cfg = get_connection_info()
            conn = _mysql_connection(cfg.database)
        except Exception:
            use_sqlite = True

        if not use_sqlite:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            finally:
                cursor.close()
                conn.close()

    conn = _sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(_normalize_sql_for_sqlite(query), params)
        rows = cursor.fetchall()
        cursor.close()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def execute_non_query(query: str, parameters: Iterable[Any] | None = None) -> int:
    """Execute INSERT/UPDATE/DELETE and return affected rowcount."""
    params = tuple(parameters or ())
    if _HAS_MYSQL:
        use_sqlite = False
        try:
            cfg = get_connection_info()
            conn = _mysql_connection(cfg.database)
        except Exception:
            use_sqlite = True

        if not use_sqlite:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                affected = cursor.rowcount
                conn.commit()
                return affected
            finally:
                cursor.close()
                conn.close()

    conn = _sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(_normalize_sql_for_sqlite(query), params)
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        return affected
    finally:
        conn.close()


def execute_select(query: str, parameters: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    """Compatibility wrapper for legacy module structures."""
    return execute_query(query, parameters)


def execute_modify(query: str, parameters: Iterable[Any] | None = None) -> int:
    """Compatibility wrapper returning affected rowcount for INSERT/UPDATE/DELETE."""
    return execute_non_query(query, parameters)


def initialize_database(schema_path: str | None = None) -> bool:
    """Execute schema.sql or the fallback schema to create tables."""
    schema_path = schema_path or os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    schema_path = os.path.abspath(schema_path)
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    try:
        if _HAS_MYSQL:
            cfg = get_connection_info()
            conn = _mysql_connection()
            cursor = conn.cursor()
            with open(schema_path, "r", encoding="utf-8") as fh:
                sql = fh.read()
            for statement in sql.split(";"):
                statement = statement.strip()
                while statement.startswith("--") or statement.startswith("#"):
                    lines = statement.split("\n", 1)
                    statement = lines[1].strip() if len(lines) > 1 else ""
                if not statement:
                    continue
                try:
                    cursor.execute(statement)
                except Exception:
                    continue
            conn.commit()
            _run_migrations(conn)
            cursor.close()
            conn.close()
            return True
    except Exception:
        # Fall back to SQLite below.
        pass

    try:
        conn = _sqlite_connection()
        cursor = conn.cursor()
        cursor.executescript(_sqlite_schema())
        conn.commit()
        _run_migrations(conn)
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False


def _run_migrations(conn) -> None:
    """Safely adds newly introduced columns and tables to existing databases without data loss."""
    cols_to_add = [
        ("Notifications", "student_id", "INT", "INTEGER"),
        ("Notifications", "alert_type", "VARCHAR(50) DEFAULT 'SYSTEM'", "TEXT DEFAULT 'SYSTEM'"),
        ("Notifications", "source", "VARCHAR(50) DEFAULT 'Analytics Engine'", "TEXT DEFAULT 'Analytics Engine'"),
        ("Notifications", "dedup_key", "VARCHAR(150)", "TEXT"),
        ("Notifications", "action_status", "VARCHAR(30) DEFAULT 'OPEN'", "TEXT DEFAULT 'OPEN'"),
        # Version 2.0 Phase 1: Multi-School Tenancy & User Context
        ("Students", "school_id", "INT", "INTEGER"),
        ("Users", "organization_id", "INT", "INTEGER"),
        ("Users", "school_id", "INT", "INTEGER"),
        ("Users", "is_active", "INT DEFAULT 1", "INTEGER DEFAULT 1"),
        ("Users", "updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
    ]
    cursor = conn.cursor()
    is_sqlite = isinstance(conn, sqlite3.Connection) or ("sqlite" in str(type(conn)).lower())
    for tbl, col_name, mysql_def, sqlite_def in cols_to_add:
        try:
            col_def = sqlite_def if is_sqlite else mysql_def
            cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col_name} {col_def}")
            conn.commit()
        except Exception:
            # Column already exists or table structure up to date
            pass
    try:
        cursor.close()
    except Exception:
        pass


def initialize_database_from_file(sql_file_path: str) -> bool:
    """Initialize the database from custom schema file or the SQLite fallback schema."""
    if _HAS_MYSQL:
        try:
            conn = _mysql_connection()
            cursor = conn.cursor()
            with open(sql_file_path, "r", encoding="utf-8") as fh:
                sql = fh.read()
            for statement in sql.split(";"):
                statement = statement.strip()
                while statement.startswith("--") or statement.startswith("#"):
                    lines = statement.split("\n", 1)
                    statement = lines[1].strip() if len(lines) > 1 else ""
                if not statement:
                    continue
                try:
                    cursor.execute(statement)
                except Exception:
                    continue
            conn.commit()
            _run_migrations(conn)
            cursor.close()
            conn.close()
            return True
        except Exception:
            pass

    try:
        conn = _sqlite_connection()
        cursor = conn.cursor()
        cursor.executescript(_sqlite_schema())
        conn.commit()
        _run_migrations(conn)
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False



def log_activity(activity_text: str):
    """Logs a system action to the Activity_Log table."""
    import datetime
    now_str = datetime.datetime.now().strftime("%I:%M %p")
    time_str = f"Today • {now_str}"
    try:
        execute_non_query(
            "INSERT INTO Activity_Log (activity, activity_time) VALUES (%s, %s)",
            (activity_text, time_str)
        )
    except Exception:
        pass


def _sqlite_schema() -> str:
    return """
    CREATE TABLE IF NOT EXISTS Schema_Migrations (
      migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
      version TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
      checksum TEXT,
      status TEXT DEFAULT 'SUCCESS'
    );

    CREATE TABLE IF NOT EXISTS Organizations (
      organization_id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      code TEXT UNIQUE NOT NULL,
      is_active INTEGER DEFAULT 1,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Schools (
      school_id INTEGER PRIMARY KEY AUTOINCREMENT,
      organization_id INTEGER NOT NULL,
      name TEXT NOT NULL,
      code TEXT UNIQUE NOT NULL,
      is_active INTEGER DEFAULT 1,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Admin_Login (
      admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      last_login TEXT
    );
    CREATE TABLE IF NOT EXISTS Students (
      student_id INTEGER PRIMARY KEY AUTOINCREMENT,
      school_id INTEGER,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      class_section TEXT NOT NULL,
      dob TEXT,
      gender TEXT DEFAULT 'O',
      email TEXT,
      phone TEXT,
      enrollment_date TEXT,
      FOREIGN KEY (school_id) REFERENCES Schools(school_id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS Learning_Objectives (
      objective_id INTEGER PRIMARY KEY AUTOINCREMENT,
      topic_name TEXT NOT NULL,
      description TEXT
    );
    CREATE TABLE IF NOT EXISTS Diagnostic_Logs (
      log_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      objective_id INTEGER,
      score_obtained REAL NOT NULL,
      max_score REAL DEFAULT 100,
      test_date TEXT,
      time_taken_minutes INTEGER,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
      FOREIGN KEY (objective_id) REFERENCES Learning_Objectives(objective_id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS Cyber_Audit (
      audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      password_strength INTEGER DEFAULT 0,
      screen_time_hours REAL DEFAULT 0,
      daily_screen_time REAL DEFAULT 0,
      study_screen_time REAL DEFAULT 0,
      recreational_screen_time REAL DEFAULT 0,
      sleep_duration REAL DEFAULT 8,
      digital_distraction_level INTEGER DEFAULT 0,
      cyber_safety_awareness INTEGER DEFAULT 0,
      netiquette_score INTEGER DEFAULT 0,
      privacy_awareness INTEGER DEFAULT 0,
      e_waste_awareness INTEGER DEFAULT 0,
      wellness_score REAL DEFAULT 0,
      audit_date TEXT,
      remarks TEXT,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS Weekly_Progress (
      week_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      week_start TEXT NOT NULL,
      score REAL DEFAULT 0,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS Achievements (
      achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      badge_name TEXT NOT NULL,
      date_awarded TEXT,
      remarks TEXT,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS Attendance (
      attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      attendance_date TEXT NOT NULL,
      status TEXT NOT NULL,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS Activity_Log (
      log_id INTEGER PRIMARY KEY AUTOINCREMENT,
      activity TEXT NOT NULL,
      activity_time TEXT
    );
    CREATE TABLE IF NOT EXISTS Reports_Metadata (
      report_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER,
      report_type TEXT NOT NULL,
      generated_at TEXT,
      file_path TEXT,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS Users (
      user_id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      full_name TEXT NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT DEFAULT 'Teacher',
      status TEXT DEFAULT 'Active',
      is_active INTEGER DEFAULT 1,
      organization_id INTEGER,
      school_id INTEGER,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      last_login TEXT,
      FOREIGN KEY (organization_id) REFERENCES Organizations(organization_id) ON DELETE SET NULL,
      FOREIGN KEY (school_id) REFERENCES Schools(school_id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS Notifications (
      notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER,
      alert_type TEXT DEFAULT 'SYSTEM',
      priority TEXT DEFAULT 'INFO',
      title TEXT NOT NULL,
      message TEXT NOT NULL,
      is_read INTEGER DEFAULT 0,
      source TEXT DEFAULT 'Analytics Engine',
      dedup_key TEXT,
      action_status TEXT DEFAULT 'OPEN',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS Interventions (
      intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      risk_factor TEXT NOT NULL,
      action_type TEXT DEFAULT 'Remedial Practice',
      priority TEXT DEFAULT 'MEDIUM',
      status TEXT DEFAULT 'PENDING',
      assigned_date TEXT NOT NULL,
      target_date TEXT,
      completed_date TEXT,
      teacher_notes TEXT,
      pre_academic_score REAL,
      post_academic_score REAL,
      pre_attendance_rate REAL,
      post_attendance_rate REAL,
      pre_risk_score REAL,
      post_risk_score REAL,
      pre_lhs_score REAL,
      post_lhs_score REAL,
      effectiveness_score REAL,
      effectiveness_tier TEXT,
      FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
    );
    """

