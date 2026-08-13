"""Configuration module for PMLA-SCWE."""

import os

APP_NAME = "PMLA-SCWE"
APP_VERSION = "2.0.0"

# Centralized database settings (checks environment variables first, then defaults)
DATABASE_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "12345678"),
    "database": os.environ.get("DB_NAME", "pmla_scwe"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}

MENU_TITLE = f"{APP_NAME} - Predictive Learning Analytics System"
