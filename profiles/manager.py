from typing import Dict

from custom_exceptions import InvalidPassword, InvalidUsername, UserAlreadyExists
from profiles.security import EncryptionStrategy
from profiles.repository import StorageInterface
from profiles.user_profile import User


class UserManager:
    def __init__(self, encryption_strategy: EncryptionStrategy, storage: StorageInterface) -> None:
        self.users: Dict[str, User] = {}
        self.encryption_strategy = encryption_strategy
        self.storage = storage
        self.load_users()

    def load_users(self) -> None:
        users_data_dict = self.storage.load_data()
        for username, users_data_dict in users_data_dict.items():
            self.users[username] = User.from_dict(users_data_dict)

    def save_users(self) -> None:
        users_data_dict = {username: user.as_dict() for username, user in self.users.items()}
        self.storage.save_data(users_data_dict)

    def add_user(self, username: str, password: str) -> None:
        if self.user_exists(username):
            raise UserAlreadyExists(f'Username {username} already exists')

        encrypted_password = self.encryption_strategy.encrypt(password)
        new_user = User(username, encrypted_password)
        self.users[username] = new_user
        self.save_users()

    def remove_user(self, username: str) -> None:
        if not self.user_exists(username):
            raise InvalidUsername(f'User {username} does not exist')
        del self.users[username]
        self.save_users()

    def get_user(self, username: str) -> User:
        if not self.user_exists(username):
            raise InvalidUsername(f'User {username} does not exist.')
        return self.users[username]

    def user_exists(self, username: str) -> bool:
        return username in self.users


class AuthenticationManager:
    def __init__(self,  user_manager: UserManager) -> None:
        self.user_manager = user_manager

    def login_user(self, username: str, password: str) -> None:
        try:
            user = self.user_manager.users[username]
        except KeyError:
            raise InvalidUsername(username)

        if not self.password_match(user, password):
            raise InvalidPassword(username, user)

        self.logout_all_users()

        user.is_logged_in = True

    def logout_all_users(self) -> None:
        for user in self.user_manager.users.values():
            user.is_logged_in = False

    def password_match(self, user: User, password: str) -> bool:
        return self.user_manager.encryption_strategy.check_encrypted(password, user.encrypted_password)
