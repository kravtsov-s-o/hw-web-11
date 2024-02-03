from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactBase, ContactResponse
from src.repository import contacts as repository_contacts
from src.services.auth import auth_services

router = APIRouter(prefix='/contacts', tags=['contacts'])

TIMES = 10
SECONDS = 60

@router.get('/', response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def get_contacts(skip: int = 0, limit: int = 100, search_first_name: str = None, search_last_name: str = None,
                       search_email: str = None, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_services.get_current_user)
                       ):
    contacts = await repository_contacts.get_contacts(
        skip, limit, current_user, db, search_first_name, search_last_name, search_email
    )
    return contacts


@router.get('/birthday_within_7_days', response_model=List[ContactResponse],
            dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def get_contacts_birthday_within_7_days(db: Session = Depends(get_db),
                                              current_user: User = Depends(auth_services.get_current_user)):
    contacts = await repository_contacts.get_contacts_birthday_within_7_days(current_user, db)
    return contacts


@router.get('/{contact_id}', response_model=ContactResponse,
                                                    dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def get_contact(contact_id, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_services.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
                                                    dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def create_contact(body: ContactBase, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_services.get_current_user)):
    return await repository_contacts.create_contact(body, current_user, db)


@router.put('/{contact_id}', response_model=ContactResponse,
                                                    dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def update_contact(body: ContactBase, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_services.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete('/{contact_id}', response_model=ContactResponse,
                                                    dependencies=[Depends(RateLimiter(times=TIMES, seconds=SECONDS))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_services.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
