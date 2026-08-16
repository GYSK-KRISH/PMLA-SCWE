"""Unit tests for Tenant Service (Organizations and Schools management)."""

from __future__ import annotations

import unittest
from core.database import initialize_database, execute_non_query
from core import tenant_service


class TestTenantService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    def test_default_organization_and_school_provisioning(self):
        """Verify dynamic provisioning and retrieval of default legacy tenant boundaries."""
        org = tenant_service.get_default_organization()
        self.assertIsNotNone(org)
        self.assertEqual(org["code"], "DEFAULT_ORG")
        self.assertEqual(org["name"], "PMLA-SCWE Default Organization")
        self.assertTrue(org["organization_id"] > 0)

        school = tenant_service.get_default_school()
        self.assertIsNotNone(school)
        self.assertEqual(school["code"], "DEFAULT_SCHOOL")
        self.assertEqual(school["name"], "Default School")
        self.assertEqual(school["organization_id"], org["organization_id"])
        self.assertTrue(school["school_id"] > 0)

    def test_organization_crud(self):
        """Verify organization creation, retrieval, listing, and updates."""
        # Create custom test org
        org_code = "TEST_ORG_ALPHA"
        org_name = "Alpha Educational Trust"
        org_id = tenant_service.create_organization(org_name, org_code, is_active=True)
        self.assertIsNotNone(org_id)

        # Retrieve by ID and code
        fetched_by_id = tenant_service.get_organization(org_id)
        self.assertIsNotNone(fetched_by_id)
        self.assertEqual(fetched_by_id["name"], org_name)
        self.assertEqual(fetched_by_id["code"], org_code)

        fetched_by_code = tenant_service.get_organization_by_code(org_code)
        self.assertIsNotNone(fetched_by_code)
        self.assertEqual(fetched_by_code["organization_id"], org_id)

        # Update
        self.assertTrue(tenant_service.update_organization(org_id, "Alpha Trust Updated", is_active=False))
        updated = tenant_service.get_organization(org_id)
        self.assertEqual(updated["name"], "Alpha Trust Updated")
        self.assertEqual(updated["is_active"], 0)

        # List organizations
        all_orgs = tenant_service.list_organizations()
        self.assertTrue(any(o["organization_id"] == org_id for o in all_orgs))

    def test_school_crud(self):
        """Verify school creation, retrieval, listing under organization, and updates."""
        org = tenant_service.get_default_organization()
        org_id = org["organization_id"]

        school_code = "NORTH_CAMPUS"
        school_name = "North Valley High School"
        school_id = tenant_service.create_school(org_id, school_name, school_code, is_active=True)
        self.assertIsNotNone(school_id)

        # Retrieve by ID and code
        fetched = tenant_service.get_school(school_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["name"], school_name)
        self.assertEqual(fetched["code"], school_code)
        self.assertEqual(fetched["organization_id"], org_id)

        fetched_code = tenant_service.get_school_by_code(school_code)
        self.assertIsNotNone(fetched_code)
        self.assertEqual(fetched_code["school_id"], school_id)

        # List schools for org
        org_schools = tenant_service.list_schools(organization_id=org_id)
        self.assertTrue(any(s["school_id"] == school_id for s in org_schools))

        # Update
        self.assertTrue(tenant_service.update_school(school_id, "North Valley Academy", is_active=True))
        updated = tenant_service.get_school(school_id)
        self.assertEqual(updated["name"], "North Valley Academy")


if __name__ == "__main__":
    unittest.main()
