import stdiomask  # type: ignore

from controller.actions.base_action import Action
from profiles.credentials import OpenAICredentials
from profiles.manager import UserManager
from settings import OPENAI_MODELS
from ui.menu_items import StageState
from ui.ui_manager import ContextManager
from utils import clear_screen
from custom_exceptions import DuplicateServiceError


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
        try:
            self.context_manager.current_profile.add_credentials(openai_credentials)
            if not self.context_manager.current_ai:
                self.context_manager.current_ai = openai_credentials
                self.log(f'Current AI updated to {openai_credentials.service_name}')
            self.user_manager.save_users()
            self.context_manager.current_stage = StageState.NO_NOTE_SELECTED
            self.info('OpenAI configured successfully!')
        except DuplicateServiceError:
            print('OpenAI credential for this profile is already configured.')
            input(f'Press enter to continue...')

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
