"""Unit tests for Authorization, RBAC, AuthenticatedUser Context, and Tenant Boundaries."""

from __future__ import annotations

import unittest
from core.authorization_service import (
    AuthenticatedUser,
    ROLE_ADMIN,
    ROLE_TEACHER,
    ROLE_VIEWER,
    is_admin,
    is_teacher,
    is_viewer,
    can_manage_users,
    can_manage_organizations,
    can_modify_students,
    can_record_attendance,
    can_create_interventions,
    can_generate_reports,
    can_view_analytics,
    has_school_access,
    has_org_access,
    get_authenticated_user_context,
)
from core.database import initialize_database
from core import user_service, tenant_service


class TestAuthorizationService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def setUp(self):
        self.def_org = tenant_service.get_default_organization()
        self.def_school = tenant_service.get_default_school()
        self.org_id = self.def_org["organization_id"]
        self.school_id = self.def_school["school_id"]

        self.admin_user = AuthenticatedUser(
            user_id=101,
            username="admin_user",
            full_name="Administrator Test",
            role=ROLE_ADMIN,
            organization_id=self.org_id,
            school_id=self.school_id,
            is_active=True,
        )

        self.teacher_user = AuthenticatedUser(
            user_id=102,
            username="teacher_user",
            full_name="Teacher Test",
            role=ROLE_TEACHER,
            organization_id=self.org_id,
            school_id=self.school_id,
            is_active=True,
        )

        self.viewer_user = AuthenticatedUser(
            user_id=103,
            username="viewer_user",
            full_name="Auditor Viewer",
            role=ROLE_VIEWER,
            organization_id=self.org_id,
            school_id=self.school_id,
            is_active=True,
        )

        self.inactive_user = AuthenticatedUser(
            user_id=104,
            username="inactive_user",
            full_name="Inactive Person",
            role=ROLE_TEACHER,
            organization_id=self.org_id,
            school_id=self.school_id,
            is_active=False,
        )

    def test_authenticated_user_dataclass_conversions(self):
        """Verify dictionary serialization and deserialization."""
        d = self.teacher_user.to_dict()
        self.assertEqual(d["username"], "teacher_user")
        self.assertEqual(d["role"], ROLE_TEACHER)
        self.assertEqual(d["school_id"], self.school_id)
        self.assertTrue(d["is_active"])

        restored = AuthenticatedUser.from_dict(d)
        self.assertEqual(restored.user_id, 102)
        self.assertEqual(restored.role, ROLE_TEACHER)
        self.assertTrue(restored.is_active)

    def test_role_type_predicates(self):
        """Verify role type checkers."""
        self.assertTrue(is_admin(self.admin_user))
        self.assertFalse(is_admin(self.teacher_user))
        self.assertFalse(is_admin(self.viewer_user))

        self.assertTrue(is_teacher(self.teacher_user))
        self.assertFalse(is_teacher(self.admin_user))

        self.assertTrue(is_viewer(self.viewer_user))
        self.assertFalse(is_viewer(self.teacher_user))

        # Inactive user predicates must all be False
        self.assertFalse(is_admin(self.inactive_user))
        self.assertFalse(is_teacher(self.inactive_user))
        self.assertFalse(is_viewer(self.inactive_user))

    def test_administrative_permissions(self):
        """Verify user and organization management is restricted strictly to Admins."""
        self.assertTrue(can_manage_users(self.admin_user))
        self.assertFalse(can_manage_users(self.teacher_user))
        self.assertFalse(can_manage_users(self.viewer_user))

        self.assertTrue(can_manage_organizations(self.admin_user))
        self.assertFalse(can_manage_organizations(self.teacher_user))
        self.assertFalse(can_manage_organizations(self.viewer_user))

    def test_operational_permissions(self):
        """Verify student modification, attendance recording, and intervention creation."""
        # Admin and Teacher can modify students, record attendance, create interventions
        self.assertTrue(can_modify_students(self.admin_user))
        self.assertTrue(can_modify_students(self.teacher_user))
        self.assertFalse(can_modify_students(self.viewer_user))
        self.assertFalse(can_modify_students(self.inactive_user))

        self.assertTrue(can_record_attendance(self.admin_user))
        self.assertTrue(can_record_attendance(self.teacher_user))
        self.assertFalse(can_record_attendance(self.viewer_user))

        self.assertTrue(can_create_interventions(self.admin_user))
        self.assertTrue(can_create_interventions(self.teacher_user))
        self.assertFalse(can_create_interventions(self.viewer_user))

    def test_read_and_report_permissions(self):
        """Verify active users across all roles can view analytics and generate reports."""
        for u in (self.admin_user, self.teacher_user, self.viewer_user):
            self.assertTrue(can_view_analytics(u))
            self.assertTrue(can_generate_reports(u))

        self.assertFalse(can_view_analytics(self.inactive_user))
        self.assertFalse(can_generate_reports(self.inactive_user))

    def test_tenant_boundary_scoping(self):
        """Verify school and organization access scope rules."""
        other_school_id = 9999

        # Teacher is strictly scoped to assigned school
        self.assertTrue(has_school_access(self.teacher_user, self.school_id))
        self.assertFalse(has_school_access(self.teacher_user, other_school_id))

        # Viewer is strictly scoped to assigned school
        self.assertTrue(has_school_access(self.viewer_user, self.school_id))
        self.assertFalse(has_school_access(self.viewer_user, other_school_id))

        # Inactive user is rejected
        self.assertFalse(has_school_access(self.inactive_user, self.school_id))

        # Organization check
        self.assertTrue(has_org_access(self.teacher_user, self.org_id))
        self.assertFalse(has_org_access(self.teacher_user, 9999))

    def test_server_side_user_context_revalidation(self):
        """Verify server reloads fresh state from DB and does not trust arbitrary claims."""
        # Create a test teacher account in DB
        test_uname = "auth_test_teacher"
        user_service.create_user(
            username=test_uname,
            full_name="Auth Test Teacher",
            password_t="teacher_pass_123",
            role=ROLE_TEACHER,
            status="Active",
            organization_id=self.org_id,
            school_id=self.school_id,
        )

        all_u = user_service.list_users()
        created_user = next((u for u in all_u if u["username"] == test_uname), None)
        self.assertIsNotNone(created_user)
        uid = created_user["user_id"]

        # Server-side revalidation
        ctx = get_authenticated_user_context(uid)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx.user_id, uid)
        self.assertEqual(ctx.role, ROLE_TEACHER)
        self.assertEqual(ctx.school_id, self.school_id)
        self.assertTrue(ctx.is_active)

        # Deactivate user in DB
        user_service.update_user(
            user_id=uid,
            username=test_uname,
            full_name="Auth Test Teacher",
            role=ROLE_TEACHER,
            status="Inactive",
            is_active=False
        )

        # Now context revalidation should return None (inactive)
        deactivated_ctx = get_authenticated_user_context(uid)
        self.assertNull_or_None = self.assertIsNone(deactivated_ctx)


if __name__ == "__main__":
    unittest.main()
