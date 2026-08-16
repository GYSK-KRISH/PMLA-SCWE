# PMLA-SCWE: Strategic Development Roadmap
## Release Milestones, Current Checkpoint & Future Planning

---

## 1. Roadmap Overview & Status Matrix

```text
┌──────────────────────────────┬───────────────────┬───────────────────────────────────────────────────────────┐
│ Milestone / Phase            │ Status            │ Primary Capabilities & Focus                              │
├──────────────────────────────┼───────────────────┼───────────────────────────────────────────────────────────┤
│ Version 1.0 – 1.2            │ COMPLETED         │ Core CRUD, Dual DB, Student 360°, LHS formulation.        │
│ Version 1.3 – 1.4            │ COMPLETED         │ OLS Linear Regression, Explainable Risk Engine, Copilot.  │
│ Version 1.5 – 1.6            │ COMPLETED         │ Closed-loop interventions, delta analytics, vector PDFs.  │
│ Version 1.7 – 1.8            │ COMPLETED         │ Command Center, smart notifications, CBSE freeze.         │
│ Version 2.0 Phase 1          │ COMPLETED         │ Multi-School Tenancy & RBAC Foundation (78 Tests Passing).│
├──────────────────────────────┼───────────────────┼───────────────────────────────────────────────────────────┤
│ Version 2.0 Phase 2A         │ NEXT TO RESUME    │ Desktop AuthenticatedUser Context & Desktop RBAC UI.      │
│ Version 2.0 Phase 2B         │ PLANNED           │ Teacher-Class Allocation & Class-Level Scoping.           │
│ Version 2.0 Phase 3          │ PLANNED           │ Organization & School Administration GUI.                 │
│ Version 2.1                  │ PLANNED           │ Real-Time Voice Synthesis & Speech Dialogue Engine.       │
│ Version 2.2                  │ PLANNED           │ Proactive Insight & Early Risk Automation Engine.         │
└──────────────────────────────┴───────────────────┴───────────────────────────────────────────────────────────┘
```

---

## 2. Completed Milestones Summary

### Version 2.0 Phase 1 (Completed & Verified)
- **Multi-School Tenancy Schema**: Created `Organizations` (root tenant), `Schools` (operational tenant), and `Schema_Migrations` tables.
- **Tenant-Aware Users & Students**: Added `school_id` to `Students`, and `organization_id`, `school_id`, and `is_active` to `Users`.
- **RBAC Security Engine**: Centralized `AuthenticatedUser` dataclass, server-side revalidation, and capability checking in `core/authorization_service.py`.
- **Modern Password Hashing**: Standardized on PBKDF2-HMAC-SHA256 with transparent fallback for legacy hashes.
- **Migration & Backup Infrastructure**: Created `core/migration_service.py` with pre-migration SQLite snapshots and zero data loss assertions.
- **Verified Test Baseline**: 78 Unit Tests passing (100% OK) + 5/5 Smoke Test checkpoints passing.

---

## 3. Next Immediate Development Milestone

```text
================================================================================
                    IMMEDIATE RESUME POINT: VERSION 2.0 PHASE 2A
================================================================================
```

### **Version 2.0 Phase 2A — Desktop AuthenticatedUser Context & Desktop RBAC Integration**

**Target Objective**:
Connect the authenticated user session to the PySide6 desktop interface, propagating user identity and tenant context into the main window and enforcing role-aware UI navigation.

**Actionable Task Breakdown**:
1. **Desktop Login Integration (`desktop/login.py`)**:
   - Update `LoginFrame` to return the complete authenticated user dictionary upon successful verification.
   - Construct a validated `AuthenticatedUser` context object.
2. **Context Propagation (`desktop/app.py`)**:
   - Store `current_user: AuthenticatedUser` on the main application window.
   - Pass user context into child view panels (`DashboardFrame`, `StudentsFrame`, `InterventionsFrame`, `ReportsFrame`, etc.).
3. **Role-Aware Sidebar Navigation**:
   - Dynamically filter sidebar navigation items based on role:
     - **Admin**: All views visible (Dashboard, Students, Attendance, Assessments, Wellness, Analytics, Interventions, Reports, AI Copilot, User Management).
     - **Teacher**: School operational views visible; User Management hidden.
     - **Viewer**: Read-only views visible; User Management hidden.
4. **UI Operational Enforcement**:
   - For **Viewer** role, disable/hide *Add Student*, *Mark Attendance*, *Log Test*, and *Create Intervention* buttons to enforce read-only access.
   - Display role badge in desktop header (`Admin`, `Teacher`, `Viewer`).
5. **Phase 2A Verification**:
   - Add automated UI/context tests in `tests/test_desktop_rbac.py`.
   - Perform live manual verification with Admin, Teacher, and Viewer accounts.

---

## 4. Subsequent Planned Milestones

### Version 2.0 Phase 2B: Teacher-Class Allocation & Class Scoping
- Create `Teacher_Class_Assignments` junction table.
- Allow teachers to be assigned to specific class sections (e.g. `XII-A`, `XI-B`).
- Scope student lists, attendance sheets, and intervention pipelines to assigned classes.

### Version 2.0 Phase 3: Super-Admin Tenant Administration GUI
- Dedicated Desktop and Web management views for creating and configuring Organizations and Schools.
- Cross-tenant usage analytics and institutional subscription monitoring.

### Version 2.1: Advanced Real-Time Voice Synthesis
- Full integration of real-time conversational audio tutor with pyttsx3 speech synthesis.
- Voice-driven hands-free student intelligence queries.

### Version 2.2: Proactive Automated Insight Engine
- Automated background worker scanning student trajectories weekly.
- Proactive generation of early warning alerts before quarterly exams.
