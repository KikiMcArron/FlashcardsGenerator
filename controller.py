import sys
import ast

import stdiomask  # type: ignore

from custom_exceptions import DuplicateProfileError, InvalidPassword, ValidationError
from flashcards.deck import Card, Deck
from flashcards.generator import CardsGenerator, OpenAIClient
from notes.reader import TxtReader
from profiles.credentials import OpenAICredentials
from profiles.manager import AuthenticationManager, UserManager
from profiles.repository import JSONStorage
from profiles.security import Bcrypt, PasswordValidator
from profiles.user_profile import Profile
from settings import FILE_TYPES, OPENAI_MODELS, STORAGE_DIR, USERS_FILE, PROMPT
from ui.gui import FileSelector
from ui.menu_items import MenuState, StageState
from ui.ui_manager import ContextManager, MenuManager
from utils import clear_screen


class Application:
    def __init__(self):
        self.context_manager = ContextManager()
        self.menu_manager = MenuManager(self.context_manager)
        self.encryption_strategy = Bcrypt()
        self.storage = JSONStorage(f'{STORAGE_DIR}/{USERS_FILE}')
        self.user_manager = UserManager(self.encryption_strategy, self.storage)
        self.auth_manager = AuthenticationManager(self.user_manager)
        self.file_selector = FileSelector(FILE_TYPES)
        # TODO: Do I need this action_dispatcher. Maybe I can execute menu actions via class method
        self.action_dispatcher = {
            'login': LogIn(self.context_manager, self.auth_manager),
            'logout': LogOut(self.context_manager, self.auth_manager),
            'new_user': NewUser(self.user_manager),
            'remove_user': RemoveUser(self.auth_manager),
            'profile_menu': ProfileMenu(self.context_manager),
            'new_profile': NewProfile(self.context_manager, self.user_manager),
            'select_profile': SelectProfile(self.context_manager),
            'ai_menu': AIMenu(self.context_manager),
            'source_menu': SourceMenu(self.context_manager),
            'setup_open_ai': SetupOpenAI(self.context_manager, self.user_manager),
            # 'edit_profile': EditProfile(self, self.profile_manager),
            'source_file': NoteFromFile(self.context_manager, self.file_selector),
            'generate_cards': GenerateCards(self.context_manager),
            # 'work_with_cards': WorkWithCards()
            'main_menu': MainMenu(self.context_manager),
            'exit': Exit(self.auth_manager)
        }

    def main(self):
        clear_screen()
        while True:
            print('################ DEBUG #######################')
            print(f'Current menu: {self.context_manager.current_menu},\n'
                  f'Current stage: {self.context_manager.current_stage}\n'
                  f'Current user: {self.context_manager.current_user}\n'
                  f'Current AI: {self.context_manager.current_ai}')
            print('####################################################################\n')
            print('Select your action:')
            self.menu_manager.display_menu()
            user_input = input('>>>>> ')
            action_key = self.menu_manager.process_input(user_input)
            clear_screen()
            if not action_key:
                continue
            self._execute_action(action_key)
            clear_screen()

    def _execute_action(self, action_key):
        action = self.action_dispatcher.get(action_key)
        action.execute()


class Action:
    def execute(self):
        raise NotImplementedError('Subclasses should implement this!')

    @staticmethod
    def log(message):
        print(f'[LOG] {message}')

    @staticmethod
    def error(message):
        print(f'[ERROR] {message}')
        input('Press enter to continue...')

    @staticmethod
    def info(message):
        print(f'[INFO] {message}')
        input('Press enter to continue...')


class LogIn(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self) -> None:
        user_manager = self.auth_manager.user_manager
        if not user_manager.users:
            self.error('No users! Please create new user first.')
            return
        self.log('Logging in...')
        user_name = input('Username: ')
        if not user_manager.user_exists(user_name):
            self.error(f'User "{user_name}" doesn\'t exists, try again with a different user name or create new user.')
            return
        password = stdiomask.getpass(prompt='Password: ')
        try:
            self.auth_manager.login_user(user_name, password)
        except InvalidPassword:
            self.error('Invalid password.')
            return
        user = user_manager.users[user_name]
        self.context_manager.current_user = user
        self.context_manager.current_menu = MenuState.MAIN_MENU
        profile = self.context_manager.current_user.get_profile('main')
        self.context_manager.current_profile = profile
        default_ai = profile.default_ai
        if default_ai:
            self.context_manager.current_ai = profile.get_credentials(default_ai)
            self.context_manager.current_stage = StageState.NO_NOTE_SELECTED
        else:
            self.context_manager.current_stage = StageState.NO_AI
        self.info(f'User {user_name} logged in successfully!')


class LogOut(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self) -> None:
        self.log('Logging out...')
        self.auth_manager.logout_users()
        self.context_manager.current_menu = MenuState.LOG_MENU
        self.context_manager.current_user = None
        self.info('Logged out successfully!')


class NewUser(Action):
    def __init__(self, user_manager: UserManager) -> None:
        self.password_validator = PasswordValidator()
        self.user_manager = user_manager

    def execute(self) -> None:
        self.log('Adding new user...')
        user_name = input('Please provide new username: ')
        if not user_name:
            self.error('User name can\'t be empty.')
            return
        if self.user_manager.user_exists(user_name):
            self.error(f'User {user_name} already exists, try again with a different name or login for existing user.')
            return
        while True:
            # TODO: Add double check password functionality
            password = stdiomask.getpass(prompt='Please provide your password: ')
            try:
                self.password_validator.is_valid(password)
                self.user_manager.add_user(user_name, password)
                self.info('User added successfully!')
                return
            except ValidationError as e:
                self.error(f'Password validation failed: {e}\nPlease try again with a different password.')
                clear_screen()


class RemoveUser(Action):
    def __init__(self, auth_manager: AuthenticationManager) -> None:
        self.auth_manager = auth_manager

    def execute(self) -> None:
        user_manager = self.auth_manager.user_manager
        if not user_manager.users:
            self.error('No users! Please create new user first.')
            return
        self.log('Removing user...')
        user_name = input('Please provide username to remove: ')
        if not user_manager.user_exists(user_name):
            self.error(f'User "{user_name}" doesn\'t exists.')
            return
        password = stdiomask.getpass(prompt=f'Please provide password for user "{user_name}": ')
        if not self.auth_manager.password_match(user_manager.users[user_name], password):
            self.error('Invalid password.')
            return
        # TODO: Add confirmation of user deletion.
        user_manager.remove_user(user_name)
        self.info(f'User "{user_name}" removed successful.')


class ProfileMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.PROFILE_MENU


class NewProfile(Action):
    def __init__(self, context_manager: ContextManager, user_manager: UserManager) -> None:
        self.context_manager = context_manager
        self.user_manager = user_manager

    def execute(self):
        self.log('Adding new profile...')
        current_user = self.context_manager.current_user
        profile_name = input('Provide New Profile name: ')
        if not profile_name:
            self.error('Profile name can\'t be empty.')
            return
        try:
            current_user.add_profile(Profile(profile_name))
            self.user_manager.save_users()
            if self.context_manager.current_profile:
                self.context_manager.current_stage = 'profile_selected'
            else:
                self.context_manager.current_stage = 'no_profile_selected'
            self.info(f'Profile "{profile_name}" created successful.')
            return
        except DuplicateProfileError:
            self.error(f'Profile "{profile_name}" already exist.\nTry other profile name or use exist profile.''')
            return


class SelectProfile(Action):
    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager

    def execute(self):
        self.log('Profile selection...')
        profile_name = input('Please provide profile name: ')
        if not self.context_manager.current_user.profile_exists(profile_name):
            self.error(
                f'Profile "{profile_name}" does\'t exists, try again with a different profile name or create new.')
            return
        self.context_manager.current_profile = self.context_manager.current_user.get_profile(profile_name)
        self.context_manager.current_stage = StageState.NO_AI
        self.info(f'Profile "{profile_name}" selected.')
        return


class AIMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.AI_MENU


class SetupOpenAI(Action):
    def __init__(self, context_manager: ContextManager, user_manager: UserManager):
        self.context_manager = context_manager
        self.user_manager = user_manager

    def execute(self):
        self.log('OpenAI model configuration...')
        gpt_model = self.select_model()
        openai_credentials = OpenAICredentials(gpt_model)
        api_key = self.get_openai_api_key_from_user()
        openai_credentials.set_api_key(api_key)
        self.context_manager.current_profile.add_credentials(openai_credentials)
        self.context_manager.current_profile.set_as_default_ai(openai_credentials.service_name)
        self.user_manager.save_users()
        self.context_manager.current_stage = StageState.NO_NOTE_SELECTED
        self.info('OpenAI configured successfully!')

    def get_openai_api_key_from_user(self) -> str:
        """ Get OpenAI API key from the user. """
        while True:
            clear_screen()
            openai_api_key = stdiomask.getpass(prompt='Enter your OpenAI API key: ')
            if (len(openai_api_key) == 51
                    and openai_api_key[:3] == 'sk-'
                    and openai_api_key[3:].isalnum()):
                return openai_api_key
            else:
                self.error('Invalid API Key format. It should start with "sk-" and have 48 alphanumeric characters.')

    def select_model(self) -> str:
        """ Select GPT model from the list of available models."""
        while True:
            clear_screen()
            print('Select GPT model:')
            for index, model in enumerate(OPENAI_MODELS, start=1):
                print(f'{index}. {model}')
            choice = input(f'(1-{len(OPENAI_MODELS)}) >>>> ')
            if choice.isdigit() and int(choice) in range(1, len(OPENAI_MODELS) + 1):
                return OPENAI_MODELS[int(choice) - 1]
            else:
                self.error(f'Invalid choice. Please enter a number between 1 and {len(OPENAI_MODELS)}.')


class SourceMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.SOURCE_MENU


class NoteFromFile(Action):
    def __init__(self, context_manager: ContextManager, file_selector: FileSelector):
        self.context_manager = context_manager
        self.file_selector = file_selector

    def execute(self):
        self.log('Load note from TXT file...')
        file_path = self.file_selector.select_file()
        if file_path:
            txt_reader = TxtReader()
            content = txt_reader.read_source(file_path)
            self.context_manager.current_note = content
            self.context_manager.current_stage = StageState.NO_CARDS_GENERATED
            self.context_manager.current_menu = MenuState.MAIN_MENU
            self.info('Note loaded successfully!')


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


class MainMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.MAIN_MENU


class Exit(Action):
    def __init__(self, auth_manager: AuthenticationManager) -> None:
        self.auth_manager = auth_manager

    def execute(self) -> None:
        while True:
            answer = input('Are you sure you want quit? (Y/N) ').strip().upper()
            if answer == 'Y':
                self.auth_manager.logout_users()
                sys.exit()
            if answer == 'N':
                break
            else:
                self.error('Invalid answer, select "Y" or "N".')
                clear_screen()


app = Application()
app.main()
