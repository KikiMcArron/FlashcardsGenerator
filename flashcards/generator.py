from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from openai import OpenAI

from logger import logger, queries_logger


class AIClient(ABC):
    """Abstract base class for AI clients."""

    @abstractmethod
    def generate_completion(self, model: str, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Generate a completion based on the provided model and messages.

        :param model: The AI model to use for generating the completion.
        :param messages: A list of message dictionaries to use as input for the AI model.
        """
        pass


class OpenAIClient(AIClient):
    """OpenAI API client."""

    def __init__(self, api_key: str) -> None:
        """
        Initialize the OpenAI client with the provided API key.

        :param api_key: The API key to use for authenticating with the OpenAI API.
        """
        self.client = OpenAI(api_key=api_key)

    def generate_completion(self, model: str, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Generate a completion based on the provided model and messages.

        :param model: The AI model to use for generating the completion.
        :param messages: A list of message dictionaries to use as input for the AI model.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
        )
        return response.choices[0].message.content

    def __str__(self) -> str:
        return f'OpenAI client (API Key: {self.client.api_key[:3]}...{self.client.api_key[-4:]})'


class CardsGenerator:
    """Class responsible for generating flashcards using an AI client."""

    def __init__(self, api_client: AIClient) -> None:
        """
        Initialize the CardsGenerator with the provided AI client.

        :param api_client: An instance of AIClient to use for generating flashcards.
        """
        self.api_client = api_client
        logger.info(f'CardsGenerator initialized with: {self.api_client}.')

    def generate_flashcards(self, model: str, prompt: str, content: str) -> Optional[str]:
        """
        Generate flashcards based on the provided model, prompt, and content.

        :param model: The AI model to use for generating the flashcards.
        :param prompt: The prompt to guise the AI in generating the flashcards.
        :param content: The content to be converted into flashcards.
        """
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\n{content}"},
            ]
            response = self.api_client.generate_completion(model, messages)
            queries_logger.debug(f'Model: {model}\nContent: {content[:100] + '...'}\nResponse: {response}\n\n')
            return response
        except Exception as e:
            logger.error(f'Generating flashcards failed: \n{e}')
            raise
