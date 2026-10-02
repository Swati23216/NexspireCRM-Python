#!/usr/bin/env python3
"""
Test authentication setup
"""
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

async def test_auth():
    try:
        from fastapi import HTTPException
        from app.core.security import hash_password, verify_password, create_access_token
        from app.core.dependencies import (
            normalize_role_name,
            normalize_role_name_for_compare,
            require_permission,
            require_role,
        )
        from app.core.permissions import permissions_for_role
        from app.schemas.auth_schema import RegisterRequest
        from app.routers.role_router import validate_permissions
        from app.routers.notification_router import _can_access_notification
        from app.routers.opportunity_router import (
            OPPORTUNITY_EDIT_ROLES,
            OPPORTUNITY_ROLES,
        )
        from app.routers.reports_router import REPORT_ROLES
        from app.routers.ticket_router import TICKET_ROLES
        from app.main import app, company_homepage
        from app.routers import (
            activity_router,
            auth_router,
            customer_router,
            dashboard_router,
            followup_router,
            lead_router,
            notification_router,
            opportunity_router,
            reports_router,
            search_router,
            ticket_router,
        )

        print("Security imports successful")

        root_route = next(
            route for route in app.routes
            if getattr(route, "path", None) == "/"
            and "GET" in getattr(route, "methods", set())
        )
        homepage_response = await company_homepage()
        assert root_route.endpoint is company_homepage
        assert Path(homepage_response.path).name == "company.html"

        frontend = Path(__file__).resolve().parent / "frontend"
        homepage_html = (frontend / "company.html").read_text(encoding="utf-8")
        login_script = (frontend / "js" / "auth.js").read_text(encoding="utf-8")
        company_script = (frontend / "js" / "company.js").read_text(encoding="utf-8")
        dashboard_html = (frontend / "index.html").read_text(encoding="utf-8")
        assert homepage_html.count('class="nav-cta login-link"') == 1
        assert 'class="nav-cta login-link" href="login.html"' in homepage_html
        assert 'aria-label="Sign in to Nexspire CRM"' in homepage_html
        assert "Team sign in" not in homepage_html
        assert 'window.location.href = "index.html#dashboard"' in login_script
        assert 'loginLink.href = "index.html#dashboard"' in company_script
        assert 'class="company-nav-link" href="/"' in dashboard_html

        # Test password hashing with a shorter password (bcrypt has 72 byte limit)
        test_password = "Password123"  # Shorter password
        hashed = hash_password(test_password)
        print(f"Password hashing works (hash length: {len(hashed)})")

        # Test password verification
        is_valid = verify_password(test_password, hashed)
        print(f"Password verification works: {is_valid}")

        # Test token creation
        token = create_access_token({"user_id": "test123", "email": "test@example.com"})
        print(f"Token creation works (token length: {len(token)})")

        # Regression check: roles should be normalized case-insensitively
        normalized = normalize_role_name("  admin  ")
        assert normalized == "Admin", f"Expected 'Admin', got {normalized!r}"
        assert normalize_role_name_for_compare("  Sales Executive ") == "sales executive"

        await require_role(OPPORTUNITY_ROLES)({"role_name": "Finance Executive"})
        await require_role(REPORT_ROLES)({"role_name": "Viewer"})
        await require_role(TICKET_ROLES)({"role_name": "Support Executive"})
        await require_permission("leads.create")({
            "role_name": "Sales Executive",
            "permissions": ["leads.create"],
        })
        try:
            await require_permission("leads.delete")({
                "role_name": "Sales Executive",
                "permissions": ["leads.create"],
            })
        except HTTPException as error:
            assert error.status_code == 403
        else:
            raise AssertionError("A role without leads.delete should be denied")
        await require_permission("leads.delete")({
            "role_name": "Admin",
            "permissions": [],
        })
        assert "leads.create" in permissions_for_role(
            SimpleNamespace(role_name="Sales Executive", permissions=None)
        )
        assert permissions_for_role(
            SimpleNamespace(role_name="Custom Reviewer", permissions=["customers.view"])
        ) == ["customers.view"]
        validate_permissions(["leads.view", "customers.create"])
        try:
            validate_permissions(["root.access"])
        except HTTPException as error:
            assert error.status_code == 400
        else:
            raise AssertionError("Unknown role permissions should be rejected")
        try:
            RegisterRequest(
                full_name="New User",
                email="new@example.com",
                mobile_no="123",
                password="short",
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Registration should require an 8-character password")
        try:
            await require_role(OPPORTUNITY_EDIT_ROLES)({"role_name": "Finance Executive"})
        except HTTPException as error:
            assert error.status_code == 403
        else:
            raise AssertionError("Finance Executive should not edit opportunities")
        try:
            await require_role(TICKET_ROLES)({"role_name": "Viewer"})
        except HTTPException as error:
            assert error.status_code == 403
        else:
            raise AssertionError("Viewer should not access ticket endpoints")

        notification = SimpleNamespace(user_id=12)
        assert _can_access_notification(
            notification,
            {"user_id": 12, "role_name": "HR"},
        )
        assert not _can_access_notification(
            notification,
            {"user_id": 13, "role_name": "HR"},
        )
        assert _can_access_notification(
            notification,
            {"user_id": 13, "role_name": "Admin"},
        )

        for router_module in (
            activity_router,
            customer_router,
            followup_router,
            notification_router,
            opportunity_router,
            reports_router,
            ticket_router,
        ):
            for route in router_module.router.routes:
                assert any(
                    dependency.call.__name__ in {"role_checker", "permission_checker"}
                    for dependency in route.dependant.dependencies
                ), f"{route.path} is missing role authorization"

        for router_module in (customer_router, followup_router):
            assert all(
                any(
                    dependency.call.__name__ == "permission_checker"
                    for dependency in route.dependant.dependencies
                )
                for route in router_module.router.routes
            ), f"{router_module.__name__} is missing permission authorization"

        for route in lead_router.router.routes:
            if route.path.endswith("/public-inquiries"):
                continue
            assert any(
                dependency.call.__name__ in {"permission_checker", "role_checker"}
                for dependency in route.dependant.dependencies
            ), f"{route.path} is missing lead authorization"
        assert any(
            route.path == "/auth/register" and "POST" in route.methods
            for route in auth_router.router.routes
        )
        for path in (
            "/dashboard/leads/status",
            "/dashboard/recent-leads",
            "/dashboard/upcoming-followups",
            "/dashboard/leads",
        ):
            route = next(
                item for item in dashboard_router.router.routes
                if item.path == path
            )
            assert any(
                dependency.call.__name__ == "permission_checker"
                for dependency in route.dependant.dependencies
            ), f"{path} is missing permission authorization"

        for route in search_router.router.routes:
            assert any(
                dependency.call.__name__ in {"get_current_user", "permission_checker"}
                for dependency in route.dependant.dependencies
            ), f"{route.path} is missing authentication"
        for path in ("/search/customers", "/search/leads"):
            route = next(item for item in search_router.router.routes if item.path == path)
            assert any(
                dependency.call.__name__ == "permission_checker"
                for dependency in route.dependant.dependencies
            ), f"{path} search is missing permission authorization"

        print("\nAll authentication components are working correctly!")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_auth())
    sys.exit(0 if success else 1)
