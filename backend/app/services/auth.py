
"""Authentication business logic for AnimeWall."""

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import APIError
from app.models.user import User
from app.services.security import hash_password, verify_password


async def register_user(
    session: AsyncSession,
    *,
    username: str,
    email: str,
    password: str,
) -> User:
    """Create a new standard user account."""

    normalized_username = username.strip().lower()
    normalized_email = email.strip().lower()

    try:
        async with session.begin():
            # Check whether username or email already exists.
            statement = select(User.id).where(
                or_(
                    User.username == normalized_username,
                    User.email == normalized_email,
                )
            )

            existing_user = await session.scalar(statement)

            if existing_user is not None:
                raise APIError(
                    status_code=409,
                    code="ACCOUNT_ALREADY_EXISTS",
                    message="Username or email is already in use.",
                )

            # Never store the original password.
            user = User(
    		username=normalized_username,
    		email=normalized_email,
    		password_hash=hash_password(password),
    		role="user",
    		token_version=0,
		)

            session.add(user)
            await session.flush()

    except IntegrityError:
        # Handles duplicate registration attempts occurring simultaneously.
        raise APIError(
            status_code=409,
            code="ACCOUNT_ALREADY_EXISTS",
            message="Username or email is already in use.",
        ) from None

    return user

async def authenticate_user(
    session: AsyncSession,
    *,
    email: str,
    password: str,
) -> User:
    """Authenticate a user using email and password."""

    normalized_email = email.strip().lower()

    statement = select(User).where(
        User.email == normalized_email
    )

    user = await session.scalar(statement)

    # Use the same public error for unknown email and wrong password.
    if user is None:
        raise APIError(
            status_code=401,
            code="INVALID_CREDENTIALS",
            message="Email or password is incorrect.",
        )

    password_is_valid = verify_password(
        password,
        user.password_hash,
    )

    if not password_is_valid or not user.is_active:
        raise APIError(
            status_code=401,
            code="INVALID_CREDENTIALS",
            message="Email or password is incorrect.",
        )

    return user

