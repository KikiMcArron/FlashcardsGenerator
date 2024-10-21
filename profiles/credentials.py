from abc import ABC, abstractmethod
from typing import Dict

from profiles.security import SensitiveDataManager


class Credentials(ABC):
    def __init__(self, service_name: str):
        self.service_name = service_name

    @abstractmethod
    def as_dict(self) -> Dict[str, str]:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, str]):
        pass


class OpenAICredentials(Credentials):
    SENSITIVE_DATA_NAME = 'api_key'
    SENSITIVE_VARIABLE_NAME = 'OPENAI_API_KEY'

    def __init__(self, gpt_model: str, service_name='OpenAI'):
        super().__init__(service_name=service_name)
        self.gpt_model = gpt_model
        self.sensitive_data_manager = SensitiveDataManager()

    def as_dict(self):
        return {
            'service_name': self.service_name,
            'gpt_model': self.gpt_model
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Credentials:
        return cls(
            service_name='OpenAI',
            gpt_model=data['gpt_model']
        )

    def set_api_key(self, api_key: str) -> None:
        self.sensitive_data_manager.set_sensitive_data(
            self.service_name,
            self.SENSITIVE_DATA_NAME,
            api_key
        )

    def get_api_key(self) -> str:
        api_key = self.sensitive_data_manager.get_sensitive_data(self.service_name, self.SENSITIVE_DATA_NAME)
        if not api_key:
            raise ValueError(f'API Key not found in keyring for the service "{self.service_name}"')
        return api_key

    def load_api_key_to_env(self) -> None:
        self.sensitive_data_manager.load_sensitive_data_to_env(
            self.service_name,
            self.SENSITIVE_DATA_NAME,
            self.SENSITIVE_VARIABLE_NAME
        )
