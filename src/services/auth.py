import pickle
from typing import Optional

import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.settings.settings import settings


class Auth:
    """
    User authentication
    """
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verification password

        :param plain_password: The password to check
        :type plain_password: str
        :param hashed_password: The password in system
        :type hashed_password: str
        :return: True | False
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Get the password hash

        :param password: The password
        :type password: str
        :return: The password hash
        :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Create a new access token

        :param data: for generating token
        :type data: dict
        :param expires_delta: Optional[float]; default = None
        :type expires_delta: float | None
        :return: access token
        :rtype: str
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        Create a new refresh token

        :param data: for generating token
        :type data: dict
        :param expires_delta: Optional[float]; default = None
        :type expires_delta: float | None
        :return: access token
        :rtype: str
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'refresh_token'})
        encoded_refresh_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str) -> str:
        """
        Decoding refresh token

        :param refresh_token: refresh token
        :type refresh_token: str
        :return: user email
        :rtype: str
        """
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Get current user

        :param token: user token
        :type token: str
        :param db: database connection
        :type db: Session
        :return: User
        :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.r.get(f"user:{email}")

        if user is None:
            user = await repository_users.get_user_by_email(email, db)

            if user is None:
                raise credentials_exception

            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        return user

    def create_email_token(self, data: dict) -> str:
        """
        Create a new email token

        :param data: information about user
        :type data: dict
        :return: user token
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return token

    async def get_email_from_token(self, token: str) -> str:
        """
        Get email from token

        :param token: user token
        :type token: str
        :return: user token
        :rtype: str
        """
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            email = payload['sub']
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Invalid token for email verification')


auth_services = Auth()
