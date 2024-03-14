from tools import save_to_file
from data import SETTINGS_FILE
from openai import OpenAI
from datetime import datetime
import json


class CardsGenerator:
    def __init__(self, api_key) -> None:
        self.client = OpenAI(api_key=api_key)

    def generate_flashcards(self, model, content) -> str:
        """Generate flashcards based on the prompt and return them as a JSON array."""
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
                max_tokens=1000, temperature=0.5, top_p=1.0, frequency_penalty=0.0)
            return response.choices[0].message.content
        except Exception as e:
            print(f'Error generating flashcards: {e}')
            return None


class Card:
    """Class representing a single flashcard."""

    def __init__(self, card_id, front, back) -> None:
        self.card_id = card_id
        self.front = front
        self.back = back

    def __str__(self) -> str:
        return (f'Card ID: {self.card_id}\n'
                f'Front: {self.front}\n'
                f'Back: {self.back}')


class CardsManager:
    def __init__(self) -> None:
        self.cards = []

    def add_cards(self, json_cards) -> None:
        """Add a list of Card objects to the manager."""
        cards = self.convert_json_to_cards(json_cards)
        self.cards.extend(cards)

    @staticmethod
    def convert_json_to_cards(json_string) -> list[Card]:
        """Convert a JSON array of flashcards to a list of Card objects."""
        try:
            cards_data = json.loads(json_string)
            return [Card(card['card_id'], card['front'], card['back']) for card in cards_data]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error converting flashcards: {e}")
            return []

    def save_flashcards(self) -> None:
        """Save all managed flashcards to a timestamped file and update settings."""
        date_time = datetime.now().strftime('%Y-%m-%d_%H-%M')
        file_name = f'flashcards_{date_time}.json'
        file_path = f'flashcards/tmp/{file_name}'
        cards_data = [{'card_id': card.card_id, 'front': card.front, 'back': card.back} for card in self.cards]
        cards_json = json.dumps(cards_data, indent=4)
        save_to_file(cards_json, file_path)
        self.update_settings_with_current_flashcards(file_name)

    @staticmethod
    def update_settings_with_current_flashcards(file_name) -> None:
        """Update SETTINGS_FILE with the current flashcards file."""
        try:
            with open(SETTINGS_FILE, 'r') as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}
        settings['current_tmp_flashcards'] = file_name
        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file, indent=4)
