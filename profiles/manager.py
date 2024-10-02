import re
from typing import Dict, Optional

from custom_exceptions import InvalidPassword, InvalidUsername, UsernameAlreadyExists, ValidationError
from profiles.user_profile import User


class PasswordValidator:
    def __init__(self, min_length: int = 6, max_length: Optional[int] = None, numbers: bool = True,
                 special: bool = True,
                 upper_lower: bool = True):
        self.min_length = min_length
        self.max_length = max_length
        self.numbers = numbers
        self.special = special
        self.upper_lower = upper_lower

    def _is_valid_size(self, password: str) -> bool:
        if self.max_length is not None:
            if not self.min_length <= len(password) <= self.max_length:
                raise ValidationError(f'Password length have to be between {self.min_length} and {self.max_length} '
                                      f'characters')
        elif self.min_length >= len(password):
            raise ValidationError(f'Password length should be at least {self.min_length} characters')
        return True

    def _contains_numbers(self, password: str) -> bool:
        if self.numbers and not re.search('[0-9]', password):
            raise ValidationError('Password must contain at least one number')
        return True

    def _contains_special_characters(self, password: str) -> bool:
        if self.special and not re.search(r'[^a-zA-Z0-9\s]', password):
            raise ValidationError('Password must contain at least one special character')
        return True

    def _contains_upper_and_lower(self, password: str) -> bool:
        if self.upper_lower:
            if not (re.search('[a-z]', password) and re.search('[A-Z]', password)):
                raise ValidationError('Password must contain at least one lowercase and one uppercase letter')
        return True

    @staticmethod
    def _contains_no_whitespaces(password: str) -> bool:
        if re.search(r'\s', password):
            raise ValidationError('Password cannot contain whitespaces')
        return True

    def is_valid(self, password: str) -> bool:
        self._is_valid_size(password)
        self._contains_numbers(password)
        self._contains_special_characters(password)
        self._contains_upper_and_lower(password)
        self._contains_no_whitespaces(password)
        return True


class UserManager:
    def __init__(self) -> None:
        self.users: Dict[str, User] = {}

    def add_user(self, username: str, password: str) -> None:
        if username in self.users:
            raise UsernameAlreadyExists(f'Username {username} already exists')

        self.users[username] = User(username, password)

    def remove_user(self, username: str) -> None:
        if username not in self.users:
            raise InvalidUsername(f'User {username} does not exist')
        del self.users[username]

    def login_user(self, username: str, password: str) -> None:
        try:
            user = self.users[username]
        except KeyError:
            raise InvalidUsername(username)

        if not user.check_password(password):
            raise InvalidPassword(username, user)

        self.logout_all_users()

        user.is_logged_in = True

    def logout_all_users(self) -> None:
        for user in self.users.values():
            user.is_logged_in = False
