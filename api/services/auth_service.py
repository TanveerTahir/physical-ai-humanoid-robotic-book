"""
Authentication service for the Physical AI & Humanoid Robotics textbook platform.
This module handles user authentication, registration, and session management.
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..models.user import User, UserCreate, UserInDB
from ..database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.user import User as UserTable


class AuthService:
    """
    Authentication service class that handles user authentication, registration,
    and JWT token management.
    """

    def __init__(self):
        self.secret_key = os.getenv("BETTER_AUTH_SECRET", "default_secret_key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        # Password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Security scheme for API docs
        self.security = HTTPBearer()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain password.
        """
        return self.pwd_context.hash(password)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[UserInDB]:
        """
        Retrieve a user by email from the database.
        """
        result = await db.execute(select(UserTable).filter(UserTable.email == email))
        user = result.scalar_one_or_none()
        if user:
            return UserInDB(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
                preferences=user.preferences,
                learning_path=user.learning_path,
                personalization_profile=user.personalization_profile,
                hashed_password=user.hashed_password
            )
        return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create a JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate a user by email and password.
        """
        user = await self.get_user_by_email(db, email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def register_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """
        Register a new user.
        """
        # Check if user already exists
        existing_user = await self.get_user_by_email(db, user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        # Hash the password
        hashed_password = self.get_password_hash(user_create.password)

        # Create new user instance
        new_user = UserTable(
            id=uuid.uuid4(),
            email=user_create.email,
            name=user_create.name,
            hashed_password=hashed_password
        )

        # Add to database
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Return user without password
        return User(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            created_at=new_user.created_at,
            last_login_at=new_user.last_login_at,
            preferences=new_user.preferences,
            learning_path=new_user.learning_path,
            personalization_profile=new_user.personalization_profile
        )

    async def get_current_user(
        self,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: AsyncSession = Depends(get_db_session)
    ) -> User:
        """
        Get the current user from the token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token.credentials, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await self.get_user_by_email(db, email)
        if user is None:
            raise credentials_exception

        return User(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            preferences=user.preferences,
            learning_path=user.learning_path,
            personalization_profile=user.personalization_profile
        )


# Create a global authentication service instance
auth_service = AuthService()