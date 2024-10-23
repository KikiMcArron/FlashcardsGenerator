import os.path
from abc import ABC, abstractmethod
from typing import Dict
import json


class StorageInterface(ABC):
    @abstractmethod
    def save_data(self, users: Dict[str, dict]) -> None:
        pass

    @abstractmethod
    def load_data(self) -> Dict[str, dict]:
        pass


class JSONStorage(StorageInterface):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_data(self, users: Dict[str, dict]) -> None:
        dir_path = os.path.dirname(self.file_path)
        self.create_directory_if_not_exists(dir_path)
        with open(self.file_path, 'w') as file:
            json.dump(users, file, indent=4)

    def load_data(self) -> Dict[str, dict]:
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
