from fastapi import APIRouter, HTTPException, status, Depends
from jose import jwt, JWTError
from pymongo.errors import PyMongoError
import logging

from app.core.config import settings


from app.models.user import User
from app.models.role import Role

from app.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
)

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)

from app.core.dependencies import get_current_user
from app.core.permissions import DEFAULT_ROLE_PERMISSIONS


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


async def _ensure_registration_roles():
    standard_roles = [
        "Admin", "Manager", "Calling Executive", "Marketing Executive",
        "Sales Executive", "Support Executive", "HR", "Finance Executive",
        "Team Lead", "Business Development Executive", "Operations Executive",
        "Viewer",
    ]
    for role_id, role_name in enumerate(standard_roles, start=1):
        role = await Role.find_one(
            Role.role_name == role_name,
            Role.deleted_at == None,
        )
        if role:
            continue
        occupied = await Role.find_one(Role.role_id == role_id)
        if occupied:
            last_role = await Role.find_all().sort("-role_id").first_or_none()
            role_id = last_role.role_id + 1 if last_role else role_id
        await Role(
            role_id=role_id,
            role_name=role_name,
            permissions=list(
                DEFAULT_ROLE_PERMISSIONS.get(role_name.lower(), ("dashboard.view",))
            ),
        ).insert()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    full_name = data.full_name.strip()
    mobile_no = data.mobile_no.strip()
    if not full_name or not mobile_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Full name and mobile number are required",
        )
    email = str(data.email).lower()
    existing_user = await User.find_one(User.email == email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    await _ensure_registration_roles()
    existing_users = await User.find_all().count()
    role_name = "Admin" if existing_users == 0 else "Viewer"
    role = await Role.find_one(Role.role_name == role_name, Role.deleted_at == None)

    last_user = await User.find_all().sort("-user_id").first_or_none()
    user = User(
        user_id=last_user.user_id + 1 if last_user else 1,
        full_name=full_name,
        email=email,
        mobile_no=mobile_no,
        password_hash=hash_password(data.password),
        role_id=role.role_id,
        is_active=True,
    )
    await user.insert()
    return {
        "message": "Registration successful",
        "user_id": user.user_id,
        "role_name": role.role_name,
    }


# =========================================================
# GET CURRENT USER
# =========================================================

@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user)
):
    return current_user


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=LoginResponse
)
async def login(data: LoginRequest):

    try:

        logger.info(
            f"Login attempt for email: {data.email}"
        )

        # -------------------------------------------------
        # Find user by email
        # -------------------------------------------------

        user = await User.find_one(
            User.email == str(data.email).lower(),
            User.deleted_at == None
        )

        if not user:

            logger.warning(
                f"Login failed: User not found - {data.email}"
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # -------------------------------------------------
        # Verify password
        # -------------------------------------------------

        is_valid = verify_password(
            data.password,
            user.password_hash
        )

        if not is_valid:

            logger.warning(
                f"Login failed: Invalid password for user - {data.email}"
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # -------------------------------------------------
        # Check active user
        # -------------------------------------------------

        if not user.is_active:

            logger.warning(
                f"Login failed: User is inactive - {data.email}"
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # -------------------------------------------------
        # Get user's role
        # -------------------------------------------------

        role = None

        if user.role_id:

            role = await Role.find_one(
                Role.role_id == user.role_id
            )

        if not role:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role not found"
            )

        role_name = role.role_name

        # -------------------------------------------------
        # Create JWT tokens
        # -------------------------------------------------

        token_data = {
            "user_id": user.user_id,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": role_name
        }

        # Access token
        access_token = create_access_token(
            token_data
        )

        # Refresh token
        refresh_token = create_refresh_token({
         "user_id": user.user_id,
         "email": user.email,
         "role_id": user.role_id,
         "role_name": role_name
    })
            
        

        logger.info(
            f"Login successful for user: {data.email}"
        )

        # -------------------------------------------------
        # Return login response
        # -------------------------------------------------

        return LoginResponse(
         access_token=access_token,
         refresh_token=refresh_token,
         token_type="bearer",
         user_id=user.user_id,
         email=user.email,
         role_id=user.role_id,
         role_name=role_name
    )

    except HTTPException:
        raise

    except PyMongoError as e:
        logger.error(
            f"MongoDB error during login: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Please try again later."
        )

    except Exception as e:

        logger.error(
            f"Unexpected error during login: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest):

    try:
        payload = verify_refresh_token(data.refresh_token)

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = await User.find_one(
            User.user_id == user_id
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        role = await Role.find_one(
            Role.role_id == user.role_id
        )

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role not found"
            )

        token_data = {
            "user_id": user.user_id,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": role.role_name
        }

        new_access_token = create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    except Exception as e:
        logger.error(
            f"Token refresh error: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh access token"
        )