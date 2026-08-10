# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-08-10

### Added
- **Database Abstraction Layer**: Implemented robust support for MySQL with automatic fallback to SQLite (`pmla_scwe_fallback.db`) if MySQL is unavailable, ensuring the application remains functional out-of-the-box.
- **Diagnostics System**: Created `diagnose_setup.py` to inspect system environment, Python dependencies, database accessibility, and SQL schema verification.
- **Comprehensive Guides**: Added detailed documentation for project execution and presentation in [RUN_AND_EXPLAIN.md](RUN_AND_EXPLAIN.md) and [DESKTOP_SETUP.md](DESKTOP_SETUP.md).

### Changed
- Refactored `PMLA_SCWE/database.py` to seamlessly switch between MySQL connectivity and SQLite fallback databases.
- Updated default credentials configuration in `.env.example`.
- Bypassed hard database connection requirements during setup/initial runs.
