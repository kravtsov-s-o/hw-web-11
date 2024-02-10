import unittest
from unittest.mock import MagicMock

from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactBase
from src.repository.contacts import (
    get_contacts,
    get_contacts_birthday_within_7_days,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_birthday_within_7_days(self):
        contacts = [MagicMock(birthday=date.today() + timedelta(days=3))]
        self.session.query().filter().filter().all.return_value = contacts
        result = await get_contacts_birthday_within_7_days(user=self.user, db=self.session)
        self.assertEqual(result, [contacts[0]])

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactBase(
            first_name='John',
            last_name='Doe',
            email="johm.dow@mail.loc",
            phone="0000000000",
            birthday=datetime.strptime('01.01.1990', '%d.%m.%Y').date())
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertTrue(hasattr(result, 'id'))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactBase(
            first_name='John',
            last_name='Doe',
            email="johm.dow@mail.loc",
            phone="0000000000",
            birthday=datetime.strptime('01.01.1990', '%d.%m.%Y').date())
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_contact_not_found(self):
        body = ContactBase(
            first_name='John',
            last_name='Doe',
            email="johm.dow@mail.loc",
            phone="0000000000",
            birthday=datetime.strptime('01.01.1990', '%d.%m.%Y').date())
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=3, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
