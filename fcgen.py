import os
import subprocess
import sys
import time
import json
import stdiomask

from data import *


class Application:
    def __init__(self):
        self.current_module = None
        self.current_stage = None
        self.current_profile = None
        self.profile_manager = ProfileManager()
        self.profiles = self.profile_manager.load_profiles()
        self.determine_current_stage()
        self.menu = Menu(self.current_module, self.current_stage)
        self.action_dispatcher = self.create_action_dispatcher()

    def main(self):
        self.clear_screen()
        while True:
            print('What you want to do?')
            self.menu.update(self.current_module, self.current_stage)
            self.menu.display_menu()
            user_input = input('>>>> ')
            self.handle_user_input(user_input)

    def input_to_action_key(self):
        menu_items_dict = module_menus[self.current_module]
        return {v: k for k, v in menu_items_dict.items()}

    def create_action_dispatcher(self):
        return {
            'new_profile': AddNewProfile(self),
            'select_profile': SelectProfile(self),
            'edit_profile': EditProfile(self),
            # 'select_source': '',
            # 'source_notion': '',
            # 'source_pdf': '',
            # 'source_txt': '',
            # 'generate_cards': '',
            # 'profile_menu': '',
            'exit': ExitProgram(self)
        }

    def determine_current_stage(self):
        if not self.profiles:
            self.current_module = 'profile'
            self.current_stage = 'initiation'
        elif not self.current_profile:
            self.current_module = 'profile'
            self.current_stage = 'no_profile_selected'

    def change_stage(self, new_stage):
        if new_stage in stages:
            self.current_stage = new_stage
            self.menu = Menu(self.current_module, self.current_stage)
        else:
            print(f'Invalid stage: {new_stage}.')

    def handle_user_input(self, user_input):
        user_action_key = next((k for k, v in self.input_to_action_key().items() if k.startswith(user_input)), None)
        action_key = self.input_to_action_key().get(user_action_key)

        # TO FIX: The action is initialized even if it is not available in the current menu items

        if action_key:
            action = self.action_dispatcher.get(action_key)
            if action:
                action.execute()
            else:
                print('Invalid option selected.')
        else:
            print(f'No action key found for user input: {user_input}')

    @staticmethod
    def clear_screen():
        if os.name == 'nt':
            subprocess.call('cls', shell=True)
        else:
            subprocess.call('clear', shell=True)


class Menu:
    def __init__(self, current_module: str, current_stage: str):
        self.current_module = current_module
        self.current_stage = current_stage
        self.items = self.get_menu_items()

    def get_menu_items(self):
        menu_items_dict = module_menus[self.current_module]
        return [menu_items_dict[item_id] for item_id in stages[self.current_stage]]

    def display_menu(self):
        for item in self.items:
            print(item)

    def needs_update(self, new_module, new_stage):
        return new_module != self.current_module or new_stage != self.current_stage

    def update(self, new_module, new_stage):
        if self.needs_update(new_module, new_stage):
            self.current_module = new_module
            self.current_stage = new_stage
            self.items = self.get_menu_items()


class Profile:
    def __init__(self, profile_name=None, openai_api_key=None, gpt_model=None):
        self.profile_name = profile_name
        self.openai_api_key = openai_api_key
        self.gpt_model = gpt_model

    def __str__(self):
        return (f'{self.profile_name} (OpenAI API Key: sk-...{self.openai_api_key[-4:]}, GPT Model: '
                f'{self.gpt_model})')

    def as_dict(self):
        return {
            'profile_name': self.profile_name,
            'openai_api_key': self.openai_api_key,
            'gpt_model': self.gpt_model
        }

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.as_dict(), file, indent=4)

    def current_profile(self):
        return None


class ProfileManager:
    def __init__(self, profiles_dir='profiles'):
        self.profiles_dir = profiles_dir
        self.profiles = self.load_profiles()

    def load_profiles(self):
        profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.profiles_dir, filename)
                with open(file_path, 'r') as file:
                    try:
                        profile_data = json.load(file)
                        if self.validate_profile_files(profile_data):
                            profile = Profile(**profile_data)
                            profiles.append(profile)
                        else:
                            # TODO: Consider to add validation messages depends of data issue
                            print(f'Invalid profile data in file "{file_path}".')
                    except json.JSONDecodeError:
                        print(f'Error decoding JSON from file "{file_path}".')
        return profiles

    def select_profile(self):
        for index, profile in enumerate(self.profiles):
            print(f'{index}. {profile}')
        while True:
            choice = input(f'Select profile (0-{len(self.profiles) - 1}) >>>> ')
            if choice.isdigit() and int(choice) in range(len(self.profiles)):
                current_profile = self.profiles[int(choice)]
                self.validate_profile_data(current_profile)
                return current_profile
            else:
                print(f'Invalid choice. Please enter a number between 0 and {len(self.profiles) - 1}.')

    def save_current_profile(self):
        pass

    def determine_current_profile(self):
        pass

    @staticmethod
    def validate_profile_files(data):
        requires_fields = ['profile_name', 'openai_api_key', 'gpt_model']
        if not all(field in data for field in requires_fields):
            return False
        return True

    def validate_profile_data(self, profile):
        profile_name = profile.profile_name
        openai_api_key = profile.openai_api_key
        gpt_model = profile.gpt_model
        data_changed = False
        if not (len(openai_api_key) == 51 and openai_api_key.startswith('sk-') and openai_api_key[3:].isalnum()):
            print(f'Invalid or no OpenAI API Key selected in profile {profile_name}')
            openai_api_key = self.get_openai_api_key_from_user()
            data_changed = True
            print(f'The OpenAI Key in profile {profile_name} has been updated')
        if gpt_model == '' or gpt_model not in openai_models:
            print(f'Invalid or no GPT model selected for profile {profile_name}')
            gpt_model = self.select_model()
            data_changed = True
            print(f'The GPT model in profile {profile_name} has been updated')
        if data_changed:
            updated_profile = Profile(profile_name, openai_api_key, gpt_model)
            updated_profile.save_to_file(f'profiles/{profile_name}.json')

    def display_profile_info(self):
        print(f'[Current profile info:   ]')

    def add_new_profile(self):
        # TODO: Add verification whether a profile with the given name already exists
        profile_name = input('Enter your new profile name: ')
        openai_api_key = self.get_openai_api_key_from_user()
        gpt_model = self.select_model()
        new_profile = Profile(profile_name, openai_api_key, gpt_model)

        new_profile.save_to_file(f'profiles/{profile_name}.json')

    @staticmethod
    def get_openai_api_key_from_user():
        while True:
            openai_api_key = stdiomask.getpass(prompt='Enter your OpenAI API key: ')
            if (len(openai_api_key) == 51
                    and openai_api_key[:3] == 'sk-'
                    and openai_api_key[3:].isalnum()):
                return openai_api_key
            else:
                print('Invalid API Key format. It should start with "sk-" and have 48 alphanumeric characters.')

    @staticmethod
    def select_model():
        for index, model in enumerate(openai_models):
            print(f'{index}. {model}')
        while True:
            choice = input(f'Select GPT model (0-{len(openai_models) - 1}): ')
            if choice.isdigit() and int(choice) in range(len(openai_models)):
                return openai_models[int(choice)]
            else:
                print(f'Invalid choice. Please enter a number between 0 and {len(openai_models) - 1}.')


class Action:
    def __init__(self, app_inst):
        self.app_inst = app_inst

    def execute(self):
        raise NotImplementedError("Subclasses should implement this!")

    def log(self, message):
        print(f'[LOG] {message}')


class AddNewProfile(Action):
    def execute(self):
        self.app_inst.clear_screen()
        self.log('Adding a new profile...')

        ProfileManager().add_new_profile()

        print('New profile added.')
        time.sleep(3)

        # Updating application stage
        self.app_inst.clear_screen()
        profiles = ProfileManager().load_profiles()
        if profiles:
            self.app_inst.change_stage('no_profile_selected')


class SelectProfile(Action):
    def execute(self):
        self.app_inst.clear_screen()
        self.log('Profile selection...')

        profile = ProfileManager().select_profile()

        print(f'Profile: {profile} selected.')
        time.sleep(3)
        self.app_inst.clear_screen()
        self.app_inst.change_stage('profile_selected')


class EditProfile(Action):
    def execute(self):
        self.log('Profile editing...')
        # Logic for editing profile
        print('Profile edited.')
        time.sleep(3)
        self.app_inst.clear_screen()


class ExitProgram(Action):
    def execute(self):
        answer = input('Are you sure you want to close this application? ')
        if answer.upper() == 'Y':
            sys.exit()


if __name__ == "__main__":
    app = Application()
    app.main()
