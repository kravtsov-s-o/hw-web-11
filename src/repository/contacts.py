from datetime import date, timedelta
from operator import and_
from typing import List

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase, ContactResponse


async def get_contacts(skip: int, limit: int, user: User, db: Session, search_first_name: str = None,
                       search_last_name: str = None, search_email: str = None) -> List[Contact]:
    """
    Return contacts list

    :param skip: Skip count lines
    :type skip: int
    :param limit: Limit lines by page
    :type limit: int
    :param user: authorization user
    :type user: User
    :param db: database connection
    :type db: Session
    :param search_first_name: Search by first name
    :type search_first_name: str
    :param search_last_name: Search by last name
    :type search_last_name: str
    :param search_email: Search by email name
    :type search_email: str
    :return: List of contacts
    :rtype: list[Contact]
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)

    if search_first_name:
        query = query.filter(Contact.first_name.ilike(f"%{search_first_name}%"))
    if search_last_name:
        query = query.filter(Contact.last_name.ilike(f"%{search_last_name}%"))
    if search_email:
        query = query.filter(Contact.email.ilike(f"%{search_email}%"))

    return query.offset(skip).limit(limit).all()


async def get_contacts_birthday_within_7_days(user: User, db: Session) -> List[Contact]:
    """
    Get contacts with birthday during next 7 days

    :param user: authorization user
    :type user: User
    :param db: database connection
    :type db: Session
    :return: List of contacts
    :rtype: list[Contact]
    """
    end_date = date.today() + timedelta(days=7)

    query = db.query(Contact).filter(Contact.user_id == user.id)

    return query.filter(
        and_(
            Contact.birthday >= date.today(),
            Contact.birthday <= end_date
        )
    ).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Get contact by id

    :param contact_id: contact id
    :type contact_id: int
    :param user: authorization user
    :type user: User
    :param db: database connection
    :type db: Session
    :return: contact
    :rtype: Contact
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactBase, user: User, db: Session) -> Contact:
    """
    Create new contact

    :param body: information for new contact
    :type body: ContactBase
    :param user: authorization user
    :type user: User
    :param db: database connection
    :type db: Session
    :return: contact
    :rtype: Contact
    """
    contact = Contact(first_name=body.first_name, last_name=body.last_name, email=body.email, phone=body.phone,
                      birthday=body.birthday, notes=body.notes, user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Delete new contact

    :param contact_id: information for new contact
    :type contact_id: int
    :param user: authorization user
    :type user: User
    :param db: database connection
    :type db: Session
    :return: contact
    :rtype: Contact
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
        return contact


async def update_contact(contact_id: int, user: User, body: ContactBase, db: Session) -> Contact:
    """
    Delete new contact

    :param contact_id: information for new contact
    :type contact_id: int
    :param user: authorization user
    :type user: User
    :param body: information for new contact
    :type body: ContactBase
    :param db: database connection
    :type db: Session
    :return: contact
    :rtype: Contact
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.notes = body.notes
        db.commit()
        return contact
