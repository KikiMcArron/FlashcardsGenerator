from abc import ABC
from dataclasses import dataclass, field

from utils import _encrypt


@dataclass
class Credentials(ABC):
    service_name: str = field(init=False)


@dataclass
class OpenAICredentials(Credentials):
    api_key: str
    gpt_model: str
    encrypted_api_key: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.service_name = 'OpenAI'
        self.encrypt_api_key = _encrypt(self.api_key)
        self.api_key = self.encrypt_api_key
