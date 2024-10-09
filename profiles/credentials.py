from abc import ABC, abstractmethod
from typing import Dict

from security import EncryptionStrategy


class Credentials(ABC):
    def __init__(self, service_name: str):
        self.service_name = service_name

    @abstractmethod
    def as_dict(self) -> Dict[str, str]:
        pass


class OpenAICredentials(Credentials):
    def __init__(self, api_key: str, gpt_model: str, encryption_strategy: EncryptionStrategy):
        super().__init__(service_name='OpenAI')
        self.encryption_strategy = encryption_strategy
        self.encrypted_api_key = self.encryption_strategy.encrypt(api_key)
        self.gpt_model = gpt_model

    def as_dict(self):
        return {
            'service_name': self.service_name,
            'encrypted_api_key': self.encrypted_api_key,
            'gpt_model': self.gpt_model
        }