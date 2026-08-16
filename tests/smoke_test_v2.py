"""End-to-end smoke test for PMLA-SCWE Version 2.0 Phase 1."""

from __future__ import annotations

import os
import sys
import datetime

# Ensure project root is in sys.path
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core import (
    auth_service,
    student_service,
    attendance_service,
    dashboard_service,
    student_profile_service,
    authorization_service,
    tenant_service,
)


def run_smoke_test() -> bool:
    print("=" * 60)
    print(" PMLA-SCWE VERSION 2.0 PHASE 1 -- END-TO-END SMOKE TEST")
    print("=" * 60)

    # 1. Tenant and Admin Authentication
    print("\n[1/5] Testing Tenant Resolution & Admin Login...")
    def_org = tenant_service.get_default_organization()
    def_school = tenant_service.get_default_school()
    print(f"      Default Org: '{def_org['name']}' (ID: {def_org['organization_id']})")
    print(f"      Default School: '{def_school['name']}' (ID: {def_school['school_id']})")

    user = auth_service.login_user("admin", "admin123")
    if not user:
        print("      [FAIL] Admin login failed!")
        return False

    assert user["role"] == "Admin"
    assert user["organization_id"] == def_org["organization_id"]
    assert user["school_id"] == def_school["school_id"]
    print(f"      [PASS] Admin authenticated: @{user['username']} ({user['role']})")

    # 2. Student CRUD under tenant context
    print("\n[2/5] Testing Student Registration & Lookup...")
    test_student = {
        "first_name": "SmokeTest",
        "last_name": "Candidate",
        "class_section": "XII-A",
        "dob": "2008-01-01",
        "gender": "M",
        "email": "smoketest@candidate.edu",
        "phone": "9876543210",
        "school_id": user["school_id"],
    }
    if not student_service.add_student(test_student):
        print("      [FAIL] Failed to register test student!")
        return False

    results = student_service.search_students("SmokeTest")
    if not results:
        print("      [FAIL] Test student not found in search!")
        return False

    sid = results[0]["student_id"]
    print(f"      [PASS] Registered and retrieved student #{sid} with school_id={results[0]['school_id']}")

    # 3. Attendance Recording
    print("\n[3/5] Testing Attendance Logging...")
    today_str = datetime.date.today().isoformat()
    if not attendance_service.mark_attendance({
        "student_id": sid,
        "attendance_date": today_str,
        "status": "Present"
    }):
        print("      [FAIL] Failed to record attendance!")
        return False

    history = attendance_service.get_student_attendance(sid)
    print(f"      [PASS] Attendance history logged (Records: {len(history)})")

    # 4. Analytics & Dashboard Metrics
    print("\n[4/5] Testing Dashboard & Student 360 Analytics...")
    metrics = dashboard_service.get_dashboard_summary()
    total_stud = metrics.get("stats", {}).get("total_students", 0)
    print(f"      [PASS] Dashboard summary loaded (Total students: {total_stud})")

    profile = student_profile_service.get_student_360_profile(sid)
    if not profile:
        print("      [FAIL] Failed to load Student 360 profile!")
        return False
    print(f"      [PASS] Student 360 profile loaded for #{sid} (LHS: {profile.get('learning_health', {}).get('score')})")

    # Clean up test student
    student_service.delete_student(sid)
    print("      [PASS] Cleaned up temporary test student")

    # 5. RBAC & Tenant Access Scoping
    print("\n[5/5] Testing RBAC Roles & School Scoping...")
    admin_ctx = authorization_service.AuthenticatedUser.from_dict(user)
    teacher_ctx = authorization_service.AuthenticatedUser(
        user_id=2, username="t1", full_name="Teacher One", role="Teacher",
        organization_id=user["organization_id"], school_id=user["school_id"], is_active=True
    )
    viewer_ctx = authorization_service.AuthenticatedUser(
        user_id=3, username="v1", full_name="Viewer One", role="Viewer",
        organization_id=user["organization_id"], school_id=user["school_id"], is_active=True
    )

    # Permission checks
    assert authorization_service.can_manage_users(admin_ctx) is True
    assert authorization_service.can_manage_users(teacher_ctx) is False
    assert authorization_service.can_modify_students(teacher_ctx) is True
    assert authorization_service.can_modify_students(viewer_ctx) is False
    assert authorization_service.can_record_attendance(viewer_ctx) is False
    assert authorization_service.can_view_analytics(viewer_ctx) is True
    assert authorization_service.can_generate_reports(viewer_ctx) is True

    # Boundary checks
    assert authorization_service.has_school_access(teacher_ctx, user["school_id"]) is True
    assert authorization_service.has_school_access(teacher_ctx, 9999) is False
    assert authorization_service.has_school_access(viewer_ctx, user["school_id"]) is True
    assert authorization_service.has_school_access(viewer_ctx, 9999) is False
    print("      [PASS] Admin, Teacher (school-scoped), and Viewer (read-only) RBAC verified")

    print("\n" + "=" * 60)
    print(" [SUCCESS] ALL 5 SMOKE TEST CHECKPOINTS PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import sys
    success = run_smoke_test()
    sys.exit(0 if success else 1)
