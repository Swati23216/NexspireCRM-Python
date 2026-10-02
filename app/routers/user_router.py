from fastapi import APIRouter, HTTPException, status, Depends
import logging
from datetime import datetime, timezone

from app.schemas.user_schema import UserCreate
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password
from app.core.dependencies import require_role

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user=Depends(
        require_role(["Admin"])
    )
):

    try:
        logger.info(f"Creating user: {user.email}")

        existing_user = await User.find_one(
            User.email == user.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        role = await Role.find_one(
            Role.role_id == user.role_id,
            Role.deleted_at == None,
        )
        if not role:
            raise HTTPException(status_code=400, detail="User role not found")

        hashed_password = hash_password(user.password)

        # Generate next integer user_id
        last_user = await User.find_all().sort("-user_id").first_or_none()

        if last_user:
           new_user_id = last_user.user_id + 1
        else:
           new_user_id = 1

        new_user = User(
        user_id=new_user_id,
        full_name=user.full_name,
        email=user.email,
        mobile_no=user.mobile_no,
        password_hash=hashed_password,
        role_id=user.role_id,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
)

        await new_user.insert()

        

        return {
            "message": "User created successfully",
            "user_id": new_user.user_id,
            "email": user.email
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Error creating user: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/")
async def get_users(
    current_user=Depends(
        require_role(["Admin"])
    )
):

    try:
        users = await User.find(User.deleted_at == None).to_list()
        roles = await Role.find(Role.deleted_at == None).to_list()
        role_names = {role.role_id: role.role_name for role in roles}

        return [
            {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "mobile_no": user.mobile_no,
                "role_id": user.role_id,
                "role_name": role_names.get(user.role_id),
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "deleted_at": user.deleted_at
            }
            for user in users
        ]

    except Exception as e:
        logger.error(
            f"Error fetching users: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching users"
        )

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user=Depends(
        require_role(["Admin"])
    )
):
    try:
        user = await User.find_one(
        User.user_id == user_id
    )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        role = await Role.find_one(
            Role.role_id == user.role_id,
            Role.deleted_at == None,
        ) if user.role_id else None

        return {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "mobile_no": user.mobile_no,
            "role_id": user.role_id,
            "role_name": role.role_name if role else None,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "deleted_at": user.deleted_at
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Error fetching user: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user"
        )

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserCreate,
    current_user=Depends(
        require_role(["Admin"])
    )
):
    try:
        user = await User.find_one(User.user_id == user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if another user already has this email
        existing_user = await User.find_one(
            User.email == user_data.email
        )

        role = await Role.find_one(
            Role.role_id == user_data.role_id,
            Role.deleted_at == None,
        )
        if not role:
            raise HTTPException(status_code=400, detail="User role not found")

        if existing_user and existing_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already belongs to another user"
            )

        # Update user details
        user.full_name = user_data.full_name
        user.email = user_data.email
        user.mobile_no = user_data.mobile_no
        user.role_id = user_data.role_id
        user.updated_at = datetime.now(timezone.utc)

        # Update password only if a new password is provided
        if user_data.password:
            user.password_hash = hash_password(
                user_data.password
            )

        await user.save()

        return {
            "message": "User updated successfully",
            "user": {
                "user_id": user.user_id,
                "full_name": user.full_name,
                "email": user.email,
                "mobile_no": user.mobile_no,
                "role_id": user.role_id,
                "role_name": role.role_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "deleted_at": user.deleted_at
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Error updating user: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user=Depends(
        require_role(["Admin"])
    )
):
    try:
        user = await User.find_one(User.user_id == user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        user.updated_at = user.deleted_at
        await user.save()

        return {
            "message": "User deleted successfully",
            "user_id": user.user_id,
            "deleted_at": user.deleted_at,
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Error deleting user: {str(e)}",
            exc_info=True
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )