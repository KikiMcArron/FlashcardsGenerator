import os.path
from abc import ABC, abstractmethod
from typing import Dict
import json

from profiles.user_profile import User


class UserStorageInterface(ABC):
    @abstractmethod
    def save_users_data(self, users: Dict[str, User]) -> None:
        pass

    @abstractmethod
    def load_users(self) -> Dict[str, str]:
        pass


class JSONUserStorage(UserStorageInterface):
    def __init__(self, file_path):
        self.file_path = file_path

    def save_users_data(self, users: Dict[str, User]) -> None:
        dir_path = os.path.dirname(self.file_path)
        self.create_directory_if_not_exists(dir_path)
        data_dict = {username: user.as_dict() for username, user in users.items()}
        with open(self.file_path, 'w') as file:
            json.dump(data_dict, file, indent=4)

    def load_users(self) -> Dict[str, str]:
        try:
            with open(self.file_path, 'r') as file:
                users_dict = json.load(file)
                return users_dict
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f'Load users data error. Data file {self.file_path} is corrupted.')
            return {}

    @staticmethod
    def create_directory_if_not_exists(dir_path: str) -> None:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
