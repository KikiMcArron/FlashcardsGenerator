import os
import re
from abc import ABC, abstractmethod
from typing import Optional

import bcrypt
import keyring
from dotenv import load_dotenv

from custom_exceptions import ValidationError

load_dotenv()


class SensitiveDataManager:
    def load_sensitive_data_to_env(self, service_name: str, data_name: str, env_variable_name: str) -> None:
        data_value = self.get_sensitive_data(service_name, data_name)
        if not data_value:
            raise ValueError(f'Data "{data_name}" not found for service "{service_name}" in keyring')
        os.environ[env_variable_name] = data_value

    @staticmethod
    def set_sensitive_data(service_name: str, data_name: str, sensitive_data: str) -> None:
        keyring.set_password(service_name, data_name, sensitive_data)

    @staticmethod
    def get_sensitive_data(service_name: str, data_name: str) -> Optional[str]:
        return keyring.get_password(service_name, data_name)

    @staticmethod
    def get_env_variable(env_variable_name: str) -> str:
        value = os.getenv(env_variable_name)
        if not value:
            raise ValueError(f'"{env_variable_name}" is not set in the environment variables')
        return value


class EncryptionStrategy(ABC):
    @abstractmethod
    def encrypt(self, plain_text: str):
        pass

    @abstractmethod
    def check_encrypted(self, plain_text: str, encrypted_text: str):
        pass


class Bcrypt(EncryptionStrategy):
    def encrypt(self, plain_text: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_text.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def check_encrypted(self, plain_text: str, encrypted_text: str) -> bool:
        return bcrypt.checkpw(plain_text.encode('utf-8'), encrypted_text.encode('utf-8'))


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
