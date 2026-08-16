"""Database backup and recovery service for PMLA-SCWE.

Supports atomic SQLite snapshot backups, backup cataloging, restore operations,
and MySQL dump command generation for enterprise deployments.
"""

from __future__ import annotations

import datetime
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from core.config import DATABASE_CONFIG

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_SQLITE_PATH = _PROJECT_ROOT / "pmla_scwe_fallback.db"
_DEFAULT_BACKUP_DIR = _PROJECT_ROOT / "database" / "backups"


def get_backup_dir(custom_dir: Path | str | None = None) -> Path:
    """Ensure and return the backup directory."""
    bdir = Path(custom_dir) if custom_dir else _DEFAULT_BACKUP_DIR
    bdir.mkdir(parents=True, exist_ok=True)
    return bdir


def backup_sqlite(
    db_path: Path | str | None = None,
    backup_dir: Path | str | None = None,
    tag: str = "snapshot"
) -> dict[str, Any]:
    """Creates a timestamped snapshot of the SQLite database file.

    Returns metadata dictionary with backup path, timestamp, size, and status.
    """
    source_path = Path(db_path) if db_path else _DEFAULT_SQLITE_PATH
    dest_dir = get_backup_dir(backup_dir)

    if not source_path.exists():
        return {
            "success": False,
            "error": f"Database file not found: {source_path}",
            "backup_path": None,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_tag = tag.replace(" ", "_").replace("/", "_")
    backup_filename = f"{source_path.stem}_{clean_tag}_{timestamp_str}.db"
    backup_file_path = dest_dir / backup_filename

    try:
        # Use sqlite3 online backup API if possible for transaction safety
        src_conn = sqlite3.connect(source_path)
        dest_conn = sqlite3.connect(backup_file_path)
        with dest_conn:
            src_conn.backup(dest_conn)
        dest_conn.close()
        src_conn.close()

        size_bytes = backup_file_path.stat().st_size
        return {
            "success": True,
            "backup_path": str(backup_file_path.resolve()),
            "filename": backup_filename,
            "timestamp": datetime.datetime.now().isoformat(),
            "size_bytes": size_bytes,
            "tag": tag,
        }
    except Exception as ex:
        # Fallback to file copy if online backup fails
        try:
            shutil.copy2(source_path, backup_file_path)
            size_bytes = backup_file_path.stat().st_size
            return {
                "success": True,
                "backup_path": str(backup_file_path.resolve()),
                "filename": backup_filename,
                "timestamp": datetime.datetime.now().isoformat(),
                "size_bytes": size_bytes,
                "tag": tag,
                "fallback_copy": True,
            }
        except Exception as copy_err:
            return {
                "success": False,
                "error": f"Backup failed: {ex} (Fallback error: {copy_err})",
                "backup_path": None,
                "timestamp": datetime.datetime.now().isoformat(),
            }


def restore_sqlite(
    backup_path: Path | str,
    target_db_path: Path | str | None = None
) -> bool:
    """Restores SQLite database from a specified backup file snapshot."""
    src = Path(backup_path)
    if not src.exists():
        raise FileNotFoundError(f"Backup file does not exist: {src}")

    target = Path(target_db_path) if target_db_path else _DEFAULT_SQLITE_PATH
    try:
        # Verify source is valid SQLite database
        test_conn = sqlite3.connect(src)
        test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        test_conn.close()

        shutil.copy2(src, target)
        return True
    except Exception:
        return False


def list_backups(backup_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """List all available backup snapshots in descending order of creation."""
    bdir = get_backup_dir(backup_dir)
    results = []
    for f in bdir.glob("*.db"):
        stat = f.stat()
        results.append({
            "filename": f.name,
            "path": str(f.resolve()),
            "size_bytes": stat.st_size,
            "created_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results


def generate_mysqldump_instructions(
    config: dict[str, Any] | None = None,
    output_file: str | None = None
) -> dict[str, str]:
    """Generates standard mysqldump command and restore instructions for MySQL setups."""
    cfg = config or DATABASE_CONFIG
    host = cfg.get("host", "localhost")
    user = cfg.get("user", "root")
    database = cfg.get("database", "pmla_scwe")
    port = cfg.get("port", 3306)

    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = output_file or f"backup_mysql_{database}_{timestamp_str}.sql"

    dump_cmd = (
        f"mysqldump -h {host} -P {port} -u {user} -p "
        f"--single-transaction --routines --triggers --databases {database} > {out_file}"
    )
    restore_cmd = f"mysql -h {host} -P {port} -u {user} -p {database} < {out_file}"

    return {
        "output_file": out_file,
        "dump_command": dump_cmd,
        "restore_command": restore_cmd,
        "database": database,
        "host": host,
        "port": str(port),
    }
