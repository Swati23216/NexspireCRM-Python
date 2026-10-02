from app.core.dependencies import normalize_role_name_for_compare


PERMISSION_LABELS = {
    "dashboard.view": "View dashboard",
    "leads.view": "View leads",
    "leads.create": "Create leads",
    "leads.update": "Update leads",
    "leads.delete": "Delete leads",
    "leads.convert": "Convert leads to customers",
    "customers.view": "View customers",
    "customers.create": "Create customers",
    "customers.update": "Update customers",
    "customers.delete": "Delete customers",
    "followups.view": "View follow-ups",
    "followups.create": "Create follow-ups",
    "followups.update": "Update follow-ups",
    "followups.delete": "Delete follow-ups",
}

ALL_PERMISSIONS = tuple(PERMISSION_LABELS)

DEFAULT_ROLE_PERMISSIONS = {
    "admin": ALL_PERMISSIONS,
    "manager": (
        "dashboard.view", "leads.view", "leads.create", "leads.update",
        "leads.convert", "customers.view", "customers.create",
        "customers.update", "followups.view", "followups.create",
        "followups.update",
    ),
    "sales executive": (
        "dashboard.view", "leads.view", "leads.create", "leads.update",
        "leads.convert", "customers.view", "customers.create",
        "customers.update", "followups.view", "followups.create",
        "followups.update",
    ),
    "calling executive": (
        "dashboard.view", "leads.view", "leads.create", "leads.update",
        "followups.view", "followups.create", "followups.update",
    ),
    "marketing executive": (
        "dashboard.view", "leads.view", "leads.create", "leads.update",
        "customers.view",
    ),
    "team lead": (
        "dashboard.view", "leads.view", "leads.create", "leads.update",
        "leads.convert", "customers.view", "customers.create",
        "customers.update", "followups.view", "followups.create",
        "followups.update",
    ),
    "business development executive": (
        "dashboard.view", "leads.view", "leads.create", "leads.update",
        "leads.convert", "customers.view", "followups.view",
        "followups.create", "followups.update",
    ),
    "support executive": ("dashboard.view", "customers.view"),
    "finance executive": ("dashboard.view", "customers.view"),
    "operations executive": ("dashboard.view", "customers.view"),
    "hr": ("dashboard.view",),
    "viewer": ("dashboard.view",),
}


def permissions_for_role(role):
    permissions = getattr(role, "permissions", None)
    if permissions is None:
        name = normalize_role_name_for_compare(getattr(role, "role_name", None))
        return list(DEFAULT_ROLE_PERMISSIONS.get(name, ("dashboard.view",)))
    return [permission for permission in permissions if permission in PERMISSION_LABELS]
