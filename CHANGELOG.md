# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-08-13

### Added
- **Root-level Seeder (`seed_data.py`)**: Created a fresh database seeder utility directly at the project root. It leverages the modular `core.database` library to wipe existing tables, reset auto-increment counters, and seed 100 mock students with multi-day attendance, diagnostics, weekly progress, wellness audits, badges, activity logs, and reports metadata.
- **Enhanced Setup Diagnostics (`diagnose_setup.py`)**: Extended diagnostics to check all 12 current database tables (verifying presence and mapping individually) and formatted output into a structured 5-stage setup verification summary.

### Changed
- **Database Schema Alignment**: Aligned the root `schema.sql` to match `database/schema.sql` (source of truth), ensuring both `Users` and `Notifications` tables are included.
- **Requirements Update (`requirements.txt`)**: Cleaned and organized dependencies, separating them by category with comments.
- **Command Standardization**: Standardized commands to use root-level direct scripts (e.g. `python seed_data.py`, `python main.py`) instead of python modules (`-m PMLA_SCWE`).
- **Guides Alignment**: Refactored `README.md`, `all step.md`, `RUN_AND_EXPLAIN.md`, and `DESKTOP_SETUP.md` to match the current modular codebase directory layout.

### Removed
- **Legacy backup directory (`PMLA_SCWE_legacy_backup/`)**: Safely deleted the old backup folders since all logic is now fully modularized under `core/`, `desktop/`, and `web/`.

---

## [2.0.0] - 2026-08-10

### Added
- **Database Abstraction Layer**: Implemented support for MySQL with automatic fallback to SQLite (`pmla_scwe_fallback.db`).
- **Diagnostics System**: Created initial `diagnose_setup.py` script.
- **Comprehensive Guides**: Added detailed documentation for project execution and presentation.
