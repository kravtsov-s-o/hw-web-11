import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = User(email=email)
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=email, db=self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        user_model = UserModel(email="test@example.com", username="test_username", password="test_passw", avatar=None)
        result_user = User(username=user_model.username, email=user_model.email, password=user_model.password, avatar=None)
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        result = await create_user(body=user_model, db=self.session)
        self.assertEqual(result.username, result_user.username)
        self.assertEqual(result.email, result_user.email)
        self.assertEqual(result.password, result_user.password)

    async def test_update_token(self):
        user = User(email="test@example.com")
        token = "test_token"
        await update_token(user=user, token=token, db=self.session)
        self.assertEqual(user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(email="test@example.com")
        self.session.query().filter().first.return_value = user
        await confirmed_email(email=user.email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User(email="test@example.com")
        url = "https://example.com/avatar.jpg"
        self.session.query().filter().first.return_value = user
        result = await update_avatar(email=user.email, url=url, db=self.session)
        self.assertEqual(result, user)
        self.assertEqual(user.avatar, url)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
