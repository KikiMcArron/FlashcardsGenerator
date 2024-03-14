from tools import save_to_file
from data import SETTINGS_FILE
from openai import OpenAI
from datetime import datetime
import json


class CardsGenerator:
    """Class responsible for handling communication with the OpenAI via API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def generate_flashcards(self, model, content) -> dict or None:
        """Generate flashcards based on the prompt."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': f'Generate flashcards for the given text, based on content and '
                                                f'information from text. Please format the flashcards as a simple '
                                                f'JSON array with keys: "card_id", "front", "back", without Markdown '
                                                f'or code block formatting. The text is:\n\n{content}'
                     }
                ],
                max_tokens=1000,
                temperature=0.5,
                top_p=1.0,
                frequency_penalty=0.0)
            return response.choices[0].message.content
        except Exception as e:
            print(f'Error occurred while generating flashcards: {e}')
            return None

    def save_flashcards(self, flashcards):
        """Save the flashcards to a file."""
        date_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
        file_name = f'flashcards_{date_time}.json'
        file_path = f'flashcards/tmp/{file_name}'
        save_to_file(flashcards, file_path)
        self.save_current_flashcards(file_name)

    @staticmethod
    def save_current_flashcards(tmp_file_name):
        """Save the flashcards to a file."""
        try:
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings['current_tmp_flashcards'] = tmp_file_name

        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file, indent=4)


class Card:
    """Class representing a single flashcard."""

    def __init__(self, card_id, front, back):
        self.card_id = card_id
        self.front = front
        self.back = back

    def __str__(self):
        return (f'Card ID: {self.card_id}\n'
                f'Front: {self.front}\n'
                f'Back: {self.back}')


class CardManager:
    """Class responsible for managing flashcards."""

    def __init__(self):
        self.cards = []

    def load_card(self, card):
        """Load a card."""
        pass
