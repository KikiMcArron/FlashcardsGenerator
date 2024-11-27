import ast

from controller.actions.base_action import Action
from flashcards.deck import Card, Deck
from flashcards.editor import DataclassEditor
from flashcards.generator import CardsGenerator, OpenAIClient
from profiles.credentials import OpenAICredentials
from settings import PROMPT
from ui.menu_items import StageState
from ui.ui_manager import ContextManager


class GenerateCards(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.log('Generating cards...')
        if not self.context_manager.current_note:
            self.error('No note selected to generate cards from.')
            return

        if not self.context_manager.current_ai or not isinstance(self.context_manager.current_ai, OpenAICredentials):
            self.error('No valid AI credentials found for generating cards.')
            return

        try:
            api_key = self.context_manager.current_ai.get_api_key()
            model = self.context_manager.current_ai.gpt_model
            client = OpenAIClient(api_key=api_key)
            cards_generator = CardsGenerator(client)

            # Generate flashcards
            content = self.context_manager.current_note
            cards_content = cards_generator.generate_flashcards(model, PROMPT, content)
            if not cards_content:
                self.error('Failed to generate flashcards from the content.')
                return

            # You may need to implement parsing logic for cards_content into Card objects
            # Assuming cards_content is parsed into front-back card pairs here
            cards = [Card.from_dict(c) for c in ast.literal_eval(cards_content)]
            self.context_manager.temp_deck = self._save_cards_to_deck(cards)
            self.context_manager.current_stage = StageState.CARDS_GENERATED
            self.info('Flashcards generated successfully!')

        except Exception as e:
            self.error(f'Generating flashcards failed: \n{e}')

    @staticmethod
    def _save_cards_to_deck(cards):
        deck = Deck()
        deck.load_cards(cards)
        return deck


class WorkWithCards(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.cards_editor: DataclassEditor = DataclassEditor(display_fields=['front', 'back'])

    def execute(self):
        self.log('Work with generated cards...')
        if not self.context_manager.temp_deck:
            self.error('No cards to work with...')
        self.context_manager.final_deck = Deck()
        self.process_input()
        self.info('There are no more cards to work through. ')

    def process_input(self):
        for card in self.context_manager.temp_deck.cards[:]:
            while True:
                print('What you want to do with this card?')
                print('---')
                print(card)
                print('---')
                print('1. Approve card.')
                print('2. Reject card.')
                print('3. Edit card.')
                user_input = input('>>>>> ')
                if user_input == '1':
                    self.context_manager.final_deck.load_cards([card])
                    break
                elif user_input == '2':
                    print('Card rejected.')
                    break
                elif user_input == '3':
                    edited_card = self.cards_editor.edit_dataclass(card)
                    self.context_manager.final_deck.load_cards([Card(front=edited_card.front, back=edited_card.back)])
                    break
                else:
                    print(f'Option {user_input} is not available.')
                    input('Press Enter to continue...')
                    continue
            self.context_manager.temp_deck.remove_card(card)
