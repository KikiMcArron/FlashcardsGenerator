from openai import OpenAI
from datetime import datetime
from tools import save_to_file
import json


class CardsGenerator:
    """Class responsible for handling communication with the OpenAI via API."""

    def __init__(self, api_key, settings_file='settings.json'):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.settings_file = settings_file

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
        date_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'flashcards_{date_time}.json'
        file_path = f'flashcards/tmp/{file_name}'
        save_to_file(flashcards, file_path)
        self.save_current_flashcards(file_name)

    def save_current_flashcards(self, tmp_file_name):
        """Save the flashcards to a file."""
        try:
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings['current_tmp_flashcards'] = tmp_file_name

        with open(self.settings_file, 'w') as file:
            json.dump(settings, file, indent=4)


class Card:
    """Class representing a single flashcard."""

    def __init__(self, front, back):
        self.front = front
        self.back = back

    def __str__(self):
        return f'Front: {self.front}\nBack: {self.back}'


class CardManager:
    """Class responsible for managing flashcards."""

    def __init__(self):
        self.cards = []

    def load_card(self, card):
        """Load a card."""
        pass
