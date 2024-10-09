import bcrypt
from abc import ABC, abstractmethod


class EncryptionStrategy(ABC):
    @abstractmethod
    def encrypt(self, plain_text: str) -> str:
        pass

    @abstractmethod
    def check_encrypted(self, plain_text: str, encrypted_text: str) -> bool:
        pass


class BcryptEncryption(EncryptionStrategy):
    def encrypt(self, plain_text: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_text.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def check_encrypted(self, plain_text: str, encrypted_text: str) -> bool:
        return bcrypt.checkpw(plain_text.encode('utf-8'), encrypted_text.encode('utf-8'))
