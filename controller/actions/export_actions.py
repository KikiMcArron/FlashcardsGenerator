from controller.actions.base_action import Action
from ui.ui_manager import ContextManager
from utils import clear_screen
from flashcards.deck import Deck
from settings import STORAGE_DIR
from datetime import datetime


class Export2Txt(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.log('Exporting cards to .txt file...')

        temp_deck = self.context_manager.temp_deck
        final_deck = self.context_manager.final_deck

        if not final_deck or not final_deck.cards:
            if not temp_deck or not temp_deck.cards:
                self.info('There is nothing to export. Please generate cards first.')
                return
            self._handle_no_final_deck(temp_deck)
        elif final_deck.cards and temp_deck.cards:
            self._handle_export_options(temp_deck, final_deck)
        else:
            self._save_flashcards(final_deck, 'processed_cards')

    def _handle_no_final_deck(self, temp_deck: Deck):
        while True:
            self.info('You didn\'t processed any of generated cards.')
            user_input = input('Would you like to export generated cards without editing them? (Y/N) ').strip().upper()
            if user_input == 'Y':
                self._save_flashcards(temp_deck, 'unprocessed_cards')
                break
            elif user_input == 'N':
                break
            else:
                self.error('Invalid selection, please select "Y" or "N".')
                clear_screen()

    def _handle_export_options(self, temp_deck: Deck, final_deck: Deck):
        while True:
            self.info('You didn\'t processed all of generated cards.')
            print('What you want to do?')
            print('1. Export processed cards.')
            print('2. Export not processed cards.')
            print('3. Export all processed and not processed cards.')
            print('8. Back to main menu')
            user_input = input('>>>>> ').strip()

            if user_input == '1':
                self._save_flashcards(final_deck, 'processed_cards')
            elif user_input == '2':
                self._save_flashcards(temp_deck, 'unprocessed_cards')
            elif user_input == '3':
                self._save_flashcards(final_deck, 'processed_cards')
                self._save_flashcards(temp_deck, 'unprocessed_cards')
            elif user_input == '8':
                return
            else:
                self.error(f'Option {user_input} is not available.')
                clear_screen()
                continue
            break

    def _save_flashcards(self, deck: Deck, cards_name) -> None:
        date_time = datetime.now().strftime('%Y-%m-%d_%H:%M')
        file_name = f'{cards_name}_{date_time}.txt'
        file_path = f'{STORAGE_DIR}/{file_name}'
        with open(file_path, 'a') as file:
            for card in deck.cards:
                file.write(str(card) + '\n\n')
        self.info(f'Cards successful saved to {file_path}.')
