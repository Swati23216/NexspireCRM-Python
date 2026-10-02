from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.core.config import settings
from app.models.user import User
from app.models.role import Role


ROLE_NAME_CANONICAL_VALUES = [
    "Admin",
    "Manager",
    "Calling Executive",
    "Marketing Executive",
    "Sales Executive",
    "Support Executive",
    "HR",
    "Finance Executive",
    "Team Lead",
    "Business Development Executive",
    "Operations Executive",
    "Viewer",
]


def normalize_role_name(value):
    if value is None:
        return None

    text = " ".join(str(value).strip().split())
    if not text:
        return None

    lowered = text.lower()
    for canonical in ROLE_NAME_CANONICAL_VALUES:
        if lowered == canonical.lower():
            return canonical

    return text


def normalize_role_name_for_compare(value):
    normalized = normalize_role_name(value)
    return normalized.lower() if normalized else None


# =========================================================
# HTTP BEARER SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# GET CURRENT AUTHENTICATED USER
# =========================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate the JWT access token and return its payload.

    Only ACCESS tokens are accepted here.
    Refresh tokens cannot be used to access protected APIs.
    """

    token = credentials.credentials

    try:

        # -------------------------------------------------
        # Decode JWT
        # -------------------------------------------------

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # -------------------------------------------------
        # Check token type
        # -------------------------------------------------

        token_type = payload.get("type")

        if token_type != "access":

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # -------------------------------------------------
        # Get user information
        # -------------------------------------------------

        user_id = payload.get("user_id")
        email = payload.get("email")
        role_name = normalize_role_name(payload.get("role_name"))

        # -------------------------------------------------
        # Validate required fields
        # -------------------------------------------------

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: user_id missing"
            )

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: email missing"
            )

        if not role_name:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: role missing"
            )

        user = await User.find_one(
            User.user_id == user_id,
            User.deleted_at == None
        )
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive or no longer available"
            )

        role = await Role.find_one(
            Role.role_id == user.role_id,
            Role.deleted_at == None
        )
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role is no longer available"
            )

        normalized_role_name = normalize_role_name(role.role_name) or role.role_name
        from app.core.permissions import permissions_for_role

        return {
            **payload,
            "full_name": user.full_name,
            "mobile_no": user.mobile_no,
            "role_id": user.role_id,
            "role_name": normalized_role_name,
            "permissions": permissions_for_role(role),
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }

    except HTTPException:
        raise

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials"
        )


# =========================================================
# ROLE-BASED ACCESS CONTROL
# =========================================================

def require_role(allowed_roles: list[str]):

    async def role_checker(
        current_user=Depends(get_current_user)
    ):

        role = normalize_role_name_for_compare(current_user.get("role_name"))
        allowed = {
            normalize_role_name_for_compare(role_name)
            for role_name in allowed_roles
            if role_name is not None
        }

        if role not in allowed:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this role"
            )

        return current_user

    return role_checker


def require_permission(permission: str):
    async def permission_checker(
        current_user=Depends(get_current_user)
    ):
        if (
            normalize_role_name_for_compare(current_user.get("role_name")) != "admin"
            and permission not in current_user.get("permissions", [])
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this permission",
            )
        return current_user

    return permission_checker
