from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Get user by email

    :param email: User email
    :type email: str
    :param db: database connection
    :type db: Session
    :return: User
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user

    :param body: information for new contact
    :type body: UserModel
    :param db: database connection
    :type db: Session
    :return: User
    :rtype: User
    """
    new_user = User(**body.dict(), avatar=None)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update user token

    :param user: User
    :type user: User
    :param token: user token
    :type token: str | None
    :param db: database connection
    :type db: Session
    :return: None
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm user email

    :param email: user email
    :type email: str
    :param db: database connection
    :type db: Session
    :return: None
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    Update user avatar

    :param email: user email
    :type email: str
    :param url: new url for avatar image
    :type url: str
    :param db: database connection
    :type db: Session
    :return: None
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
