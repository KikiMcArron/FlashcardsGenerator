from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from openai import OpenAI

from logger import logger, queries_logger


class AIClient(ABC):

    @abstractmethod
    def generate_completion(self, model: str, messages: List[Dict[str, str]]) -> Optional[str]:
        pass


class OpenAIClient(AIClient):

    def __init__(self, api_key: str) -> None:
        self.client = OpenAI(api_key=api_key)

    def generate_completion(self, model: str, messages: List[Dict[str, str]]) -> Optional[str]:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore
            max_tokens=1000,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
        )
        return response.choices[0].message.content

    def __str__(self) -> str:
        return f'OpenAI client (API Key: {self.client.api_key[:3]}...{self.client.api_key[-4:]})'


class CardsGenerator:
    def __init__(self, ai_client: AIClient) -> None:
        self.ai_client = ai_client
        logger.info(f'CardsGenerator initialized with: {self.ai_client}.')

    def generate_flashcards(self, model: str, prompt: str, content: str) -> Optional[str]:
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\n{content}"},
            ]
            response = self.ai_client.generate_completion(model, messages)
            queries_logger.debug(f'AI model: {model}\nContent: {content[:100] + '...'}\nResponse: {response}\n\n')
            return response
        except Exception as e:
            logger.error(f'Generating flashcards failed: \n{e}')
            raise
