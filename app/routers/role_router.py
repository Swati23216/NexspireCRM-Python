from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.role import Role
from app.models.user import User
from app.core.dependencies import require_role
from app.schemas.role_schema import RoleCreate
from app.core.permissions import (
    ALL_PERMISSIONS,
    DEFAULT_ROLE_PERMISSIONS,
    permissions_for_role,
)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.post("/seed")
async def seed_roles():

    roles = [
        (1, "Admin"),
        (2, "Manager"),
        (3, "Calling Executive"),
        (4, "Marketing Executive"),
        (5, "Sales Executive"),
        (6, "Support Executive"),
        (7, "HR"),
        (8, "Finance Executive"),
        (9, "Team Lead"),
        (10, "Business Development Executive"),
        (11, "Operations Executive"),
        (12, "Viewer")
    ]

    for role_id, role_name in roles:

        existing = await Role.find_one(
            Role.role_id == role_id
        )

        if not existing:
            await Role(
                role_id=role_id,
                role_name=role_name,
                permissions=list(
                    DEFAULT_ROLE_PERMISSIONS.get(
                        role_name.lower(),
                        ("dashboard.view",),
                    )
                ),
            ).insert()

    return {
        "message": "Roles created successfully"
    }


@router.get("/")
async def get_roles(current_user=Depends(require_role(["Admin"]))):
    roles = await Role.find(Role.deleted_at == None).to_list()
    for role in roles:
        role.permissions = permissions_for_role(role)
    return roles


def validate_permissions(permissions):
    unknown = set(permissions) - set(ALL_PERMISSIONS)
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown permissions: {', '.join(sorted(unknown))}",
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_role(data: RoleCreate, current_user=Depends(require_role(["Admin"]))):
    role_name = data.role_name.strip()
    if not role_name:
        raise HTTPException(status_code=400, detail="Role name is required")
    existing_roles = await Role.find(Role.deleted_at == None).to_list()
    if any(role.role_name.casefold() == role_name.casefold() for role in existing_roles):
        raise HTTPException(status_code=400, detail="Role already exists")
    permissions = (
        data.permissions
        if data.permissions is not None
        else list(DEFAULT_ROLE_PERMISSIONS.get(role_name.lower(), ("dashboard.view",)))
    )
    validate_permissions(permissions)
    last_role = await Role.find_all().sort("-role_id").first_or_none()
    now = datetime.now(timezone.utc)
    role = Role(
        role_id=(last_role.role_id + 1 if last_role else 1),
        role_name=role_name,
        permissions=permissions,
        created_at=now,
        updated_at=now,
    )
    await role.insert()
    return role


@router.put("/{role_id}")
async def update_role(role_id: int, data: RoleCreate, current_user=Depends(require_role(["Admin"]))):
    role = await Role.find_one(Role.role_id == role_id, Role.deleted_at == None)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role_name = data.role_name.strip()
    if not role_name:
        raise HTTPException(status_code=400, detail="Role name is required")
    if role.role_name.lower() == "admin" and role_name.lower() != "admin":
        raise HTTPException(status_code=400, detail="The Admin role cannot be renamed")
    existing_roles = await Role.find(Role.deleted_at == None).to_list()
    if any(
        existing.role_id != role_id
        and existing.role_name.casefold() == role_name.casefold()
        for existing in existing_roles
    ):
        raise HTTPException(status_code=400, detail="Role already exists")
    if data.permissions is not None:
        validate_permissions(data.permissions)
        role.permissions = data.permissions
    role.role_name = role_name
    role.updated_at = datetime.now(timezone.utc)
    await role.save()
    return role


@router.delete("/{role_id}")
async def delete_role(role_id: int, current_user=Depends(require_role(["Admin"]))):
    role = await Role.find_one(Role.role_id == role_id, Role.deleted_at == None)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.role_id == 1 or role.role_name.lower() == "admin":
        raise HTTPException(status_code=400, detail="The Admin role cannot be deleted")
    assigned_user = await User.find_one(
        User.role_id == role_id,
        User.deleted_at == None,
    )
    if assigned_user:
        raise HTTPException(
            status_code=400,
            detail="Reassign users before deleting this role",
        )
    role.deleted_at = datetime.now(timezone.utc)
    role.updated_at = role.deleted_at
    await role.save()
    return {"message": "Role deleted successfully", "role_id": role_id, "deleted_at": role.deleted_at}