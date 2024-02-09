import os
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
        self.determine_current_stage()
        self.menu = Menu(self.current_module, self.current_stage)
        self.action_dispatcher = {
            'new_profile': AddNewProfile(self, self.profile_manager),
            'select_profile': SelectProfile(self, self.profile_manager),
            'edit_profile': EditProfile(self, self.profile_manager),
            # 'select_source': '',
            # 'source_notion': '',
            # 'source_pdf': '',
            # 'source_txt': '',
            # 'generate_cards': '',
            # 'profile_menu': '',
            'exit': ExitProgram(self, self.profile_manager)
        }

    def main(self):
        Tools.clear_screen()
        while True:
            self.profile_manager.display_profile_info()
            print('What you want to do?')
            self.menu.update(self.current_module, self.current_stage)
            self.menu.display_menu()
            user_input = input('>>>> ')
            self.handle_user_input(user_input)

    def determine_current_stage(self):
        if not self.profile_manager.profiles:
            self.set_current_stage('profile', 'initiation')
        elif not self.current_profile:
            self.set_current_stage('profile', 'no_profile_selected')

    def set_current_stage(self, module, stage):
        self.current_module = module
        self.current_stage = stage

    def change_stage(self, new_stage):
        if new_stage in stages:
            self.current_stage = new_stage
            self.menu = Menu(self.current_module, self.current_stage)
        else:
            print(f'Invalid stage: {new_stage}.')

    def handle_user_input(self, user_input):
        input_to_action_key = self.input_to_action_key()
        user_action_key = next((k for k, v in input_to_action_key.items() if k.startswith(user_input)), None)
        action_key = input_to_action_key.get(user_action_key)
        if action_key:
            action = self.action_dispatcher.get(action_key)
            action.execute()
        else:
            print(f'Option {user_input} is not available.')
            time.sleep(4)
            Tools.clear_screen()

    def input_to_action_key(self):
        menu_items_dict = module_menus[self.current_module]
        return {v: k for k, v in menu_items_dict.items()}


class Tools:
    clear_command = 'cls' if os.name == 'nt' else 'clear'

    @staticmethod
    def clear_screen():
        os.system(Tools.clear_command)


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
        directory = os.path.dirname(file_path)
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(self.as_dict(), file, indent=4)


class ProfileManager:
    def __init__(self, profiles_dir='profiles'):
        self.profiles_dir = profiles_dir
        self.profiles = self.load_profiles()
        self.profile = self.determine_current_profile()

    def load_profiles(self):
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)
            return []
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
                        # else:
                        #     # TODO: Do I need this message? Maybe not displaying invalid profiles is enough
                        #     print(f'Invalid profile data in file "{file_path}".', flush=True)
                        #     time.sleep(3)
                    except json.JSONDecodeError:
                        print(f'Error decoding JSON from file "{file_path}".')
        return profiles

    def select_profile(self):
        for index, profile in enumerate(self.profiles):
            print(f'{index + 1}. {profile}')
        while True:
            choice = input(f'Select profile (1-{len(self.profiles)}) >>>> ')
            if choice.isdigit() and int(choice) in range(1, len(self.profiles) + 1):
                self.profile = self.profiles[int(choice) - 1]
                self.validate_profile_data(self.profile)
                return self.profile
            else:
                print(f'Invalid choice. Please enter a number between 1 and {len(self.profiles)}.')

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
            Tools.clear_screen()
            print(f'Invalid or no OpenAI API Key selected in profile "{profile_name}"')
            profile.openai_api_key = self.get_openai_api_key_from_user()
            data_changed = True
            print(f'The OpenAI Key in profile "{profile_name}" has been updated')
        if gpt_model == '' or gpt_model not in openai_models:
            Tools.clear_screen()
            print(f'Invalid or no GPT model selected for profile "{profile_name}"')
            profile.gpt_model = self.select_model()
            data_changed = True
        if data_changed:
            profile.save_to_file(f'profiles/{profile.profile_name}.json')
            print(f'Profile "{profile.profile_name}" updated and saved.')

    def add_new_profile(self):
        while True:
            profile_name = input('Enter your new profile name: ')
            if self.is_unique_profile_name(profile_name):
                break
            else:
                print(f'Profile {profile_name} already exist')
        openai_api_key = self.get_openai_api_key_from_user()
        gpt_model = self.select_model()
        new_profile = Profile(profile_name, openai_api_key, gpt_model)
        new_profile.save_to_file(f'profiles/{profile_name}.json')

    def edit_profile(self):
        # TODO: After selecting a profile and then editing it, the data displayed in the profile information remains unchanged.
        selected_profile = self.select_profile()
        profile_dict = selected_profile.as_dict()
        original_profile_name = selected_profile.profile_name
        Tools.clear_screen()

        options = {
            '1': ('profile_name', 'Enter new profile name: '),
            '2': ('openai_api_key', self.get_openai_api_key_from_user),
            '3': ('gpt_model', self.select_model)
        }

        while True:
            Tools.clear_screen()
            self.display_edit_menu(profile_dict)
            choice = input('Select >>>>  ')

            if choice in options:
                field, handler = options[choice]
                if callable(handler):
                    profile_dict[field] = handler()
                else:
                    profile_dict[field] = input(handler)
                if field == 'profile_name' and not self.is_unique_profile_name(profile_dict[field]):
                    print(f'Profile {profile_dict[field]} already exists. Please choose a different name.')
                    continue
            elif choice == '9':
                break
            else:
                print('Invalid choice. Please select 1-3 to edit selected element or 9 to finish editing.')

        self.update_profile(original_profile_name, profile_dict)

    @staticmethod
    def display_edit_menu(profile_dict):
        print('What you want to edit: ')
        for index, (key, _) in enumerate(profile_dict.items(), start=1):
            print(f'{index}. {key.replace("_", " ").upper()}')
        print('9. Finish editing')

    def is_unique_profile_name(self, profile_name):
        return not any(profile.profile_name == profile_name for profile in self.profiles)

    def update_profile(self, original_profile_name, profile_dict):
        new_profile = Profile(**profile_dict)
        new_profile.save_to_file(os.path.join('profiles', f'{new_profile.profile_name}.json'))
        if original_profile_name != new_profile.profile_name:
            old_file_path = os.path.join('profiles', f'{original_profile_name}.json')
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        self.profiles = self.load_profiles()

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
        while True:
            print('Select GPT model:')
            for index, model in enumerate(openai_models):
                print(f'{index}. {model}')
            choice = input(f'(0-{len(openai_models) - 1}) >>>> ')
            if choice.isdigit() and int(choice) in range(len(openai_models)):
                return openai_models[int(choice)]
            else:
                print(f'Invalid choice. Please enter a number between 0 and {len(openai_models) - 1}.')

    def save_current_profile(self):
        pass

    def determine_current_profile(self):
        return None

    def display_profile_info(self):
        if not self.profile:
            print(f'>>>>> Current profile: NO PROFILE SELECTED <<<<<')
        else:
            print(f'>>>>> Current profile: {self.profile}] <<<<<')


class Action:
    def __init__(self, app_inst):
        self.app_inst = app_inst

    def execute(self):
        raise NotImplementedError("Subclasses should implement this!")

    def log(self, message):
        print(f'[LOG] {message}')


class AddNewProfile(Action):
    def __init__(self, app_inst, profile_manager):
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        Tools.clear_screen()
        self.log('Adding a new profile...')

        self.profile_manager.add_new_profile()

        print('New profile added.')
        time.sleep(3)
        Tools.clear_screen()
        profiles = self.profile_manager.load_profiles()
        if profiles and not self.profile_manager.profile:
            self.app_inst.change_stage('no_profile_selected')


class SelectProfile(Action):
    def __init__(self, app_inst, profile_manager):
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        Tools.clear_screen()
        self.log('Profile selection...')

        profile = self.profile_manager.select_profile()

        print(f'Profile: {profile} selected.')
        time.sleep(3)
        Tools.clear_screen()
        self.app_inst.change_stage('profile_selected')


class EditProfile(Action):
    def __init__(self, app_inst, profile_manager):
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        Tools.clear_screen()
        self.log('Profile editing...')
        print('Which profile you want to edit?')
        self.profile_manager.edit_profile()
        print('Profile edited.')
        time.sleep(7)
        Tools.clear_screen()


class ExitProgram(Action):
    def __init__(self, app_inst, profile_manager):
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        Tools.clear_screen()
        while True:
            answer = input('Are you sure you want to close this application? (Y/N) ')
            if answer.upper() == 'Y':
                Tools.clear_screen()
                sys.exit()
            if answer.upper() == 'N':
                Tools.clear_screen()
                break
            else:
                print('Invalid answer, select "Y" or "N".')
                time.sleep(3)
                Tools.clear_screen()
                pass


if __name__ == "__main__":
    app = Application()
    app.main()
