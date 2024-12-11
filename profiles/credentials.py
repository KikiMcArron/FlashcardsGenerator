from abc import ABC, abstractmethod
from typing import Dict, Optional

from profiles.security import SensitiveDataManager


class Credentials(ABC):
    def __init__(self, credentials_type: str, service_name: str):
        self.credentials_type = credentials_type
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

    def __init__(self, gpt_model: str, credentials_type='AI', service_name='OpenAI'):
        super().__init__(credentials_type=credentials_type, service_name=service_name)
        self.gpt_model = gpt_model
        self.sensitive_data_manager = SensitiveDataManager()

    def as_dict(self):
        return {
            'credentials_type': self.credentials_type,
            'service_name': self.service_name,
            'gpt_model': self.gpt_model,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Credentials:
        return cls(
            credentials_type=data['credentials_type'],
            service_name=data['service_name'],
            gpt_model=data['gpt_model'],
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


class CredentialsFactory:
    registered_classes: Dict = {}

    @classmethod
    def register_credentials(cls, service_name: str, credentials_cls) -> None:
        cls.registered_classes[service_name] = credentials_cls

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Optional[Credentials]:
        service_name = data.get('service_name')
        if not service_name:
            return None
        credentials_cls = cls.registered_classes.get(service_name)
        if credentials_cls is None:
            return None
        return credentials_cls.from_dict(data)


CredentialsFactory.register_credentials('OpenAI', OpenAICredentials)
