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

    Uses MySQL when the connector is installed; otherwise falls back to SQLite.
    """
    if _HAS_MYSQL:
        cfg = get_connection_info()
        try:
            return _mysql_connection(cfg.database)
        except Exception:
            # Fall back to SQLite when MySQL is unavailable or unreachable.
            pass
    return _sqlite_connection()


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
        try:
            conn = _mysql_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return [dict(row) for row in rows]
        except Exception:
            pass

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
        try:
            conn = _mysql_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            affected = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            return affected
        except Exception:
            pass

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
    """Compatibility wrapper for older module names."""
    return execute_query(query, parameters)


def execute_modify(query: str, parameters: Iterable[Any] | None = None) -> int:
    """Compatibility wrapper returning affected rowcount for INSERT/UPDATE/DELETE."""
    return execute_non_query(query, parameters)


def initialize_database(schema_path: str | None = None) -> bool:
    """Execute schema.sql or the fallback schema to create tables."""
    schema_path = schema_path or os.path.join(os.path.dirname(__file__), "..", "schema.sql")
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
                if not statement or statement.startswith("--"):
                    continue
                try:
                    cursor.execute(statement)
                except Exception:
                    # Keep going so a single non-critical statement does not block setup.
                    continue
            conn.commit()
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
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False


def initialize_database_from_file(sql_file_path: str) -> bool:
    """Initialize the database from schema.sql or the SQLite fallback schema."""
    if _HAS_MYSQL:
        try:
            conn = _mysql_connection()
            cursor = conn.cursor()
            with open(sql_file_path, "r", encoding="utf-8") as fh:
                sql = fh.read()
            for statement in sql.split(";"):
                statement = statement.strip()
                if not statement or statement.startswith("--"):
                    continue
                try:
                    cursor.execute(statement)
                except Exception:
                    continue
            conn.commit()
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
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False


def _sqlite_schema() -> str:
    return """
    CREATE TABLE IF NOT EXISTS Admin_Login (
      admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      last_login TEXT
    );
    CREATE TABLE IF NOT EXISTS Students (
      student_id INTEGER PRIMARY KEY AUTOINCREMENT,
      first_name TEXT NOT NULL,
      last_name TEXT NOT NULL,
      class_section TEXT NOT NULL,
      dob TEXT,
      gender TEXT DEFAULT 'O',
      email TEXT,
      phone TEXT,
      enrollment_date TEXT
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
      FOREIGN KEY (student_id) REFERENCES Students(student_id),
      FOREIGN KEY (objective_id) REFERENCES Learning_Objectives(objective_id)
    );
    CREATE TABLE IF NOT EXISTS Cyber_Audit (
      audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      password_strength INTEGER DEFAULT 0,
      screen_time_hours REAL DEFAULT 0,
      netiquette_score INTEGER DEFAULT 0,
      privacy_awareness INTEGER DEFAULT 0,
      e_waste_awareness INTEGER DEFAULT 0,
      wellness_score REAL DEFAULT 0,
      audit_date TEXT,
      FOREIGN KEY (student_id) REFERENCES Students(student_id)
    );
    CREATE TABLE IF NOT EXISTS Weekly_Progress (
      week_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      week_start TEXT NOT NULL,
      score REAL DEFAULT 0,
      FOREIGN KEY (student_id) REFERENCES Students(student_id)
    );
    CREATE TABLE IF NOT EXISTS Achievements (
      achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      badge_name TEXT NOT NULL,
      date_awarded TEXT,
      remarks TEXT,
      FOREIGN KEY (student_id) REFERENCES Students(student_id)
    );
    CREATE TABLE IF NOT EXISTS Attendance (
      attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_id INTEGER NOT NULL,
      attendance_date TEXT NOT NULL,
      status TEXT NOT NULL,
      FOREIGN KEY (student_id) REFERENCES Students(student_id)
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
      file_path TEXT
    );
    """
