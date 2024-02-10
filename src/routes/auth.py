from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_services
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Registration user

    :param body: User model
    :type body: UserModel
    :param background_tasks: BackgroundTask
    :type background_tasks: BackgroundTask
    :param request: Form Request
    :type request: Request
    :param db: Session Database
    :type db: Session
    :return: dict with keys user (UserModel) and detail (message)
    :rtype: dict
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_services.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {'user': new_user, 'detail': 'User successful created. Check your email for confirmation.'}


@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    """
    User authentication
    ! Attention - Field Username, but you need enter email !

    :param body: user information
    :type body: OAuth2PasswordRequestForm
    :param db: connection to database
    :type db: Session
    :return: dictionary with keys access_token, refresh_token and token_type
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_services.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # generate JWT token
    access_token = await auth_services.create_access_token(data={'sub': user.email})
    refresh_token = await auth_services.create_refresh_token(data={'sub': user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> dict:
    """
    Refreshes the access token using a valid refresh token.

    :param credentials: HTTP Authorization credentials containing the refresh token.
    :type credentials: HTTPAuthorizationCredentials
    :param db: Database session.
    :type db: Session
    :return: New access and refresh tokens along with the token type.
    :rtype: dict
    """
    token = credentials.credentials
    email = await auth_services.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_services.create_access_token(data={'sub': email})
    refresh_token = await auth_services.create_refresh_token(data={'sub': email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)) -> dict:
    """
    Confirms the user's email based on the provided confirmation token.

    :param token: Confirmation token.
    :type token: str
    :param db: Database session.
    :type db: Session
    :return: Message indicating the result of the email confirmation.
    :rtype: dict
    """
    email = await auth_services.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'You email is already confirmed'}
    await repository_users.confirmed_email(email, db)
    return {'message': 'Email confirmed'}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)) -> dict:
    """
    Sends a confirmation email or notifies the user if the email is already confirmed.

    :param body: Request body containing the email.
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending emails.
    :type background_tasks: BackgroundTasks
    :param request: Request object.
    :type request: Request
    :param db: Database session.
    :type db: Session
    :return: Message instructing the user to check their email for confirmation.
    :rtype: dict
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)

    return {'message': 'Check your email for confirmed.'}
