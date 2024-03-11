import os

import pytest
import requests
from dotenv import load_dotenv

from src.handlers.authentication import AuthAndTokenHandler


class TestAUTH:
    @classmethod
    def setup_class(cls):
        load_dotenv()
        cls.auth = AuthAndTokenHandler()

    def test_login_user_success(self):
        session = requests.Session()
        login_status, updated_session = self.auth.login_user(session)
        assert login_status is True
        assert updated_session is session

    def test_login_user_failure(self):
        session = requests.Session()
        os.environ['EMAIL'] = "WrongEmail"
        os.environ['PASSWORD'] = "WrongPassword"
        login_status, updated_session = self.auth.login_user(session)
        assert login_status is False
        assert updated_session is session
