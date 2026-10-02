from jose import jwt, JWTError
from datetime import datetime, timedelta
import bcrypt
from app.core.config import settings


# =========================================================
# PASSWORD HASHING
# =========================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""

    if not password or len(password) == 0:
        raise ValueError("Password cannot be empty")

    if len(password) > 72:
        import hashlib
        password = hashlib.sha256(
            password.encode()
        ).hexdigest()

    try:
        salt = bcrypt.gensalt(rounds=12)

        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            salt
        )

        return hashed.decode("utf-8")

    except Exception as e:
        raise ValueError(
            f"Error hashing password: {str(e)}"
        )


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    """Verify a plain password against a hashed password."""

    if not plain_password or not hashed_password:
        return False

    try:

        if len(plain_password) > 72:
            import hashlib

            plain_password = hashlib.sha256(
                plain_password.encode()
            ).hexdigest()

        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except Exception as e:

        print(
            f"Error verifying password: {str(e)}"
        )

        return False


# =========================================================
# ACCESS TOKEN
# =========================================================

def create_access_token(data: dict) -> str:

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

# =========================================================
# REFRESH TOKEN
# =========================================================

def create_refresh_token(data: dict) -> str:
    """Create a long-lived refresh token."""
    try:
        to_encode = data.copy()

        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    except Exception as e:
        raise ValueError(f"Error creating refresh token: {str(e)}")

    # =========================================================
# VERIFY REFRESH TOKEN
# =========================================================

def verify_refresh_token(token: str) -> dict:
    """Verify and decode a refresh token."""

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Make sure this is actually a refresh token
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        return payload

    except JWTError:
        raise

    except Exception as e:
        raise JWTError(
            f"Error verifying refresh token: {str(e)}"
        )