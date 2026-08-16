# PMLA-SCWE: Authentication & Role-Based Access Control (RBAC)
## Security Specification & Authorization Architecture — Version 2.0 (Phase 1)

---

## 1. Overview & Security Philosophy

PMLA-SCWE Version 2.0 establishes a centralized, multi-layered security model:
1. **Cryptographic Password Protection**: PBKDF2-HMAC-SHA256 with 100,000 iterations and per-user salt.
2. **Backward-Compatible Authentication**: Transparent verification of legacy SHA-256 and MD5 password hashes.
3. **Immutable Identity Context**: Encapsulation of session state in an `AuthenticatedUser` dataclass.
4. **Server-Side Identity Revalidation**: Authoritative database re-verification prior to state-modifying operations to prevent client-side session tampering.
5. **Tenant Boundary Enforcement**: Strict scoping of faculty and student records to assigned school and organization boundaries.

---

## 2. Password Security Architecture

### 2.1 PBKDF2-HMAC-SHA256 Standard
All newly created and updated user passwords in `core/auth_service.py` are hashed using PBKDF2:

```text
Format: pbkdf2:sha256:100000$<salt_hex>$<hash_hex>
Parameters:
  • Algorithm: SHA-256
  • Salt: 16 cryptographically random bytes (os.urandom)
  • Iterations: 100,000
```

### 2.2 Transparent Legacy Hash Verification
When `verify_password(entered_pass, stored_hash)` executes:
1. **PBKDF2 Detection**: If `stored_hash` starts with `pbkdf2:sha256:`, it verifies against the salt and hash using `hashlib.pbkdf2_hmac` in constant time (`hmac.compare_digest`).
2. **SHA-256 Fallback**: If `stored_hash` is a 64-character hex string, it compares against `hashlib.sha256(password.encode()).hexdigest()`.
3. **MD5 / Plaintext Fallback**: If legacy plaintext or MD5 was stored in development prototypes, it performs a fallback check.

---

## 3. The `AuthenticatedUser` Context

Defined in `core/authorization_service.py`, `AuthenticatedUser` represents the validated identity and tenant scope of an active user:

```python
@dataclass(slots=True)
class AuthenticatedUser:
    user_id: int
    username: str
    full_name: str
    role: str                       # 'Admin', 'Teacher', or 'Viewer'
    organization_id: int | None = None
    school_id: int | None = None
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthenticatedUser:
        """Construct context from dictionary or DB row."""
        ...
```

---

## 4. Server-Side Identity Revalidation

Client-side tokens or serialized session objects can be tampered with in memory. To prevent privilege escalation or deleted/deactivated user access, the core service layer re-verifies user state via:

```python
def get_authenticated_user_context(user_id: int) -> AuthenticatedUser | None:
    """Reloads fresh database state for user_id. Returns None if inactive."""
    rows = execute_query(
        "SELECT user_id, username, full_name, role, status, is_active, "
        "organization_id, school_id FROM Users WHERE user_id = %s",
        (user_id,)
    )
    if not rows:
        return None
    user = AuthenticatedUser.from_db_row(dict(rows[0]))
    return user if user.is_active else None
```

---

## 5. Role Capability Matrix (Phase 1 Baseline)

```text
┌──────────────────────────────────────┬─────────────┬─────────────┬─────────────┐
│ Capability Function                  │ Admin       │ Teacher     │ Viewer      │
├──────────────────────────────────────┼─────────────┼─────────────┼─────────────┤
│ can_manage_users(user)               │ ALLOW       │ DENY        │ DENY        │
│ can_manage_organizations(user)       │ ALLOW       │ DENY        │ DENY        │
│ has_school_access(user, school_id)   │ ALL SCHOOLS │ Assigned    │ Assigned    │
│ has_org_access(user, org_id)         │ ALL ORGS    │ Assigned    │ Assigned    │
│ can_modify_students(user)            │ ALLOW       │ ALLOW       │ DENY (Read) │
│ can_record_attendance(user)          │ ALLOW       │ ALLOW       │ DENY (Read) │
│ can_create_interventions(user)       │ ALLOW       │ ALLOW       │ DENY (Read) │
│ can_view_analytics(user)             │ ALLOW       │ ALLOW       │ ALLOW       │
│ can_generate_reports(user)           │ ALLOW       │ ALLOW       │ ALLOW       │
└──────────────────────────────────────┴─────────────┴─────────────┴─────────────┘
```

### Role Definitions
1. **Admin (System Administrator)**:
   - Complete system access across all organizations and schools.
   - User account creation, role editing, and account deactivation.
   - Organization and school provisioning.
2. **Teacher (Faculty / Educator)**:
   - Full operational access within their assigned school.
   - Register and update student profiles, mark daily attendance, log diagnostic tests, and record cyber-wellness audits.
   - Create remedial interventions, snapshot baseline scores, and evaluate intervention recovery outcomes.
   - Access AI Teacher Copilot, view class predictive analytics, and export PDF reports.
3. **Viewer (Academic Auditor / Evaluator / Read-Only Guest)**:
   - Read-only access within their assigned school.
   - Can inspect student profiles, review attendance histories, view class analytics, and generate PDF/CSV reports.
   - Mutation operations (add student, mark attendance, edit records) are strictly rejected.

---

## 6. Tenant Boundary Scoping Rules

Faculty access to student records is constrained by school assignment:

```python
def has_school_access(user: AuthenticatedUser | dict[str, Any] | None, school_id: int | None) -> bool:
    """Verifies user has legitimate authorization to access the specified school."""
    u = _to_user_obj(user)
    if not u or not u.is_active:
        return False
    # Super-Admins have cross-school global visibility
    if u.role == ROLE_ADMIN:
        return True
    # Teachers and Viewers are strictly scoped to their assigned school
    return bool(u.school_id and u.school_id == school_id)
```

---

## 7. Version 2.0 Phase 2A UI Integration Roadmap

> [!IMPORTANT]
> **Phase 2A Implementation Boundary**:
> - **Completed in Phase 1**: All cryptographic hashing, `Users` tenant columns, `AuthenticatedUser` context, server-side revalidation, and RBAC matrix functions in `core/authorization_service.py`.
> - **Scheduled for Phase 2A**: Visual Desktop UI integration (connecting `desktop/login.py` to `AuthenticatedUser`, hiding Admin-only views for Teachers/Viewers in `desktop/app.py`, and disabling input fields for Viewers).
