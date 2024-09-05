from typing import Dict

from custom_exceptions import InvalidPassword, InvalidUsername, UsernameAlreadyExists
from profiles.user_profile import User


class UserManager:
    MIN_PASSWORD_LENGTH = 8

    def __init__(self) -> None:
        self.users: Dict[str, User] = {}

    def add_user(self, username: str, password: str) -> None:
        if username in self.users:
            raise UsernameAlreadyExists(f'Username {username} already exists')
        if not self.valid_password(password):
            raise ValueError('Password does not meet criteria')
        self.users[username] = User(username, password)

    def remove_user(self, username: str) -> None:
        if username not in self.users:
            raise InvalidUsername(f'User {username} does not exist')
        del self.users[username]

    def login(self, username: str, password: str) -> bool:
        try:
            user = self.users[username]
        except KeyError:
            raise InvalidUsername(username)

        if not user.check_password(password):
            raise InvalidPassword(username, user)

        user.is_logged_in = True
        return True

    def is_logged_in(self, username: str) -> bool:
        if username in self.users:
            return self.users[username].is_logged_in
        return False

    @classmethod
    def valid_password(cls, password: str) -> bool:
        return len(password) >= cls.MIN_PASSWORD_LENGTH
