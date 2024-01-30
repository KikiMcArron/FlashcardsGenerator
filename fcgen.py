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
        self.profiles = ProfileManager().load_profiles()
        self.determine_current_stage()
        self.menu = Menu(self.current_module, self.current_stage)
        self.action_dispatcher = self.create_action_dispatcher()

    def input_to_action_key(self):
        menu_items_dict = module_menus[self.current_module]
        return {v: k for k, v in menu_items_dict.items()}

    def main(self):
        self.clear_screen()
        while True:
            if self.menu.needs_update(self.current_module, self.current_stage):
                self.menu.update(self.current_module, self.current_stage)
            self.menu.display_menu()
            user_input = input('What you want to do? ')
            self.handle_user_input(user_input)

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

    def change_stage(self, new_stage):
        if new_stage in stages:
            self.current_stage = new_stage
            self.menu = Menu(self.current_module, self.current_stage)
        else:
            print(f'Invalid stage: {new_stage}.')

    def handle_user_input(self, user_input):
        user_action_key = next((k for k, v in self.input_to_action_key().items() if k.startswith(user_input)), None)
        action_key = self.input_to_action_key().get(user_action_key)

        # TODO: The action is initialized even if it is not available in the current menu items

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


class ProfileManager:
    def __init__(self, profile_name=None, openai_api_key=None, gpt_model=None):
        self.profile_name = profile_name
        self.openai_api_key = openai_api_key
        self.gpt_model = gpt_model

    def load_profiles(self):
        return False

    def display_profile_info(self):
        print(f'[Current profile info:   ]')

    def get_openai_api_key_from_user(self):
        while True:
            self.openai_api_key = stdiomask.getpass(prompt="Enter your OpenAI API key: ")
            if (len(self.openai_api_key) == 51
                    and self.openai_api_key[:3] == 'sk-'
                    and self.openai_api_key[3:].isalnum()):
                return self.openai_api_key
            else:
                print("Invalid API Key format. It should start with 'sk-' and have 48 alphanumeric characters.")

    @staticmethod
    def select_model():
        for index, model in enumerate(openai_models):
            print(f'{index}: {model}')
        while True:
            choice = input(f"Select GPT model (0-{len(openai_models) - 1}): ")
            if choice.isdigit() and int(choice) in range(len(openai_models)):
                return openai_models[int(choice)]
            else:
                print(f"Invalid choice. Please enter a number between 0 and {len(openai_models) - 1}.")

    def as_dict(self):
        return {
            'profile_name': self.profile_name,
            'openai_api_key': self.openai_api_key,
            'gpt_model': self.gpt_model
        }

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.as_dict(), file, indent=4)


class Action:
    def __init__(self, app_inst):
        self.app_inst = app_inst

    def execute(self):
        raise NotImplementedError("Subclasses should implement this!")

    def log(self, message):
        print(f'[LOG] {message}')


class AddNewProfile(Action):
    def execute(self):
        Application.clear_screen()
        self.log('Adding a new profile...')

        # Obtaining profile data from user
        profile_name = input('Enter your new profile name: ')
        openai_api_key = ProfileManager().get_openai_api_key_from_user()
        gpt_model = ProfileManager.select_model()
        new_profile = ProfileManager(profile_name, openai_api_key, gpt_model)

        # Saving to file obtained profile data
        new_profile.save_to_file(f'profiles/{profile_name}.json')

        print('New profile added.')
        time.sleep(3)

        # Updating application stage
        self.app_inst.clear_screen()
        if self.app_inst.profiles:
            self.app_inst.change_stage('no_profile_selected')


class SelectProfile(Action):
    def execute(self):
        self.log('Profile selection...')
        # Logic for adding a new profile
        print('Profile selected.')
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
