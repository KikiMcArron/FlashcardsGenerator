import os
import subprocess
import sys
import time

from data import *


class Application:
    def __init__(self):
        self.current_module = None
        self.current_stage = None
        self.profiles = self.load_profiles()
        self.determine_current_stage()
        self.menu = Menu(self.current_module, self.current_stage)
        self.menu_items_dict = module_menus[self.current_module]
        self.input_to_action_key = {v: k for k, v in self.menu_items_dict.items()}
        self.action_dispatcher = self.create_action_dispatcher()

    def main(self):
        self.clear_screen()
        while True:
            self.menu = Menu(self.current_module, self.current_stage)
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

    def menu_needs_update(self):
        return self.menu.current_module != self.current_module or self.menu.current_stage != self.current_stage

    def load_profiles(self):
        return False

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
        user_action_key = next((k for k, v in self.input_to_action_key.items() if k.startswith(user_input)), None)
        action_key = self.input_to_action_key.get(user_action_key)
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
        menu_items_dict = module_menus[current_module]
        self.items = [menu_items_dict[item_id] for item_id in stages[current_stage]]

    def display_menu(self):
        for item in self.items:
            print(item)


class Action:
    def __init__(self, app_inst):
        self.app_inst = app_inst

    def execute(self):
        raise NotImplementedError("Subclasses should implement this!")

    def log(self, message):
        print(f'[LOG] {message}')


class AddNewProfile(Action):
    def execute(self):
        self.log('Adding a new profile...')
        # Logic for adding a new profile
        print('New profile added.')
        time.sleep(3)
        self.app_inst.clear_screen()
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
