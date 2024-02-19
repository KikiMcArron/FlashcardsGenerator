import os
import sys
import json
import stdiomask

from data import *

clear_command = 'cls' if os.name == 'nt' else 'clear'


def clear_screen():
    """ Clear the screen. """
    os.system(clear_command)


class Application:
    """ Main class of the application. It is responsible for managing the flow of the application. """

    def __init__(self):
        """ Initialize the application. """
        self.current_module = None
        self.current_stage = None
        self.current_profile = None
        self.profile_manager = ProfileManager()
        self.stage_and_module_handler = StageAndModuleHandler(self)
        self.user_input_handler = UserInputHandler(self)
        self.stage_and_module_handler.determine_current_stage()
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
        """ Main loop for the application. """
        clear_screen()
        while True:
            self.profile_manager.display_profile_info()
            print('What you want to do?')
            self.menu.update(self.current_module, self.current_stage)
            self.menu.display_menu()
            user_input = input('>>>> ')
            self.user_input_handler.handle_user_input(user_input)


class StageAndModuleHandler:
    """ Class responsible for managing the current stage and module of the application. """

    def __init__(self, app_inst):
        """ Initialize the handler. """
        self.app_inst = app_inst

    def determine_current_stage(self):
        """ Determine the current stage of the application. """
        if not self.app_inst.profile_manager.profiles:
            self.set_current_stage('profile', 'initiation')
        elif not self.app_inst.current_profile:
            self.set_current_stage('profile', 'no_profile_selected')

    def set_current_stage(self, module, stage):
        """ Set the current stage of the application. """
        self.app_inst.current_module = module
        self.app_inst.current_stage = stage

    def change_stage(self, new_stage):
        """ Change the current stage of the application. """
        if new_stage in stages:
            self.app_inst.current_stage = new_stage
            self.app_inst.menu = Menu(self.app_inst.current_module, self.app_inst.current_stage)
        else:
            print(f'Invalid stage: {new_stage}.')
            input('Press Enter to continue...')
            clear_screen()


class UserInputHandler:
    """ Class responsible for handling user input. """

    def __init__(self, app_inst):
        """ Initialize the handler. """
        self.app_inst = app_inst

    def handle_user_input(self, user_input):
        """ Handle user input. """
        input_to_action_key = self.input_to_action_key()
        user_action_key = next((k for k, v in input_to_action_key.items() if k.startswith(user_input)), None)
        action_key = input_to_action_key.get(user_action_key)
        if action_key:
            action = self.app_inst.action_dispatcher.get(action_key)
            action.execute()
        else:
            print(f'Option {user_input} is not available.')
            input('Press Enter to continue...')
            clear_screen()

    def input_to_action_key(self):
        """ Convert user input to action key. """
        menu_items_dict = module_menus[self.app_inst.current_module]
        return {v: k for k, v in menu_items_dict.items()}


class Menu:
    """ Class responsible for managing the menu of the application. """

    def __init__(self, current_module: str, current_stage: str):
        """ Initialize the menu. """
        self.current_module = current_module
        self.current_stage = current_stage
        self.items = self.get_menu_items()

    def get_menu_items(self):
        """ Get menu items for the current stage and module. """
        menu_items_dict = module_menus[self.current_module]
        return [menu_items_dict[item_id] for item_id in stages[self.current_stage]]

    def display_menu(self):
        """ Display the menu. """
        for item in self.items:
            print(item)

    def needs_update(self, new_module, new_stage):
        """ Check if the menu needs to be updated. """
        return new_module != self.current_module or new_stage != self.current_stage

    def update(self, new_module, new_stage):
        """ Update the menu. """
        if self.needs_update(new_module, new_stage):
            self.current_module = new_module
            self.current_stage = new_stage
            self.items = self.get_menu_items()


class Profile:
    """ Class representing a profile. """

    def __init__(self, profile_name=None, openai_api_key=None, gpt_model=None):
        """ Initialize the profile. """
        self.profile_name = profile_name
        self.openai_api_key = openai_api_key
        self.gpt_model = gpt_model

    def __str__(self):
        """ Return a string representation of the profile. """
        return (f'{self.profile_name} (OpenAI API Key: sk-...{self.openai_api_key[-4:]}, GPT Model: '
                f'{self.gpt_model})')

    def as_dict(self):
        """ Return the profile as a dictionary. """
        return {
            'profile_name': self.profile_name,
            'openai_api_key': self.openai_api_key,
            'gpt_model': self.gpt_model
        }


class ProfileManager:
    """ Class responsible for managing profiles. """

    def __init__(self, profiles_dir='profiles', settings_file='settings.json'):
        """ Initialize the profile manager. """
        self.settings_file = settings_file
        self.profiles_dir = profiles_dir
        self.profiles = self.load_profiles()
        self.profile = self.determine_current_profile()

    def load_profiles(self):
        """ Load profiles from files. """
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
                        if self.is_valid_profile_file(profile_data):
                            profile = Profile(**profile_data)
                            profiles.append(profile)
                    except json.JSONDecodeError:
                        print(f'Error decoding JSON from file "{file_path}".')
        return profiles

    def select_profile(self):
        """ Select a profile from the list of profiles. """
        self.profiles = self.load_profiles()
        for index, profile in enumerate(self.profiles):
            print(f'{index + 1}. {profile}')
        while True:
            choice = input(f'Select profile (1-{len(self.profiles)}) >>>> ')
            if choice.isdigit() and int(choice) in range(1, len(self.profiles) + 1):
                self.profile = self.profiles[int(choice) - 1]
                self.validate_profile(self.profile)
                self.update_profile_if_needed(self.profile)
                self.save_current_profile(self.profile.profile_name)
                return self.profile
            else:
                print(f'Invalid choice. Please enter a number between 1 and {len(self.profiles)}.')

    def update_profile_if_needed(self, profile):
        """ Update the profile if necessary. """
        validation_errors = self.validate_profile(profile)
        if 'openai_api_key' in validation_errors:
            clear_screen()
            print(validation_errors['openai_api_key'])
            profile.openai_api_key = self.get_openai_api_key_from_user()
            print(f'The OpenAI Key in profile "{profile.profile_name}" has been updated')
        if 'gpt_model' in validation_errors:
            clear_screen()
            print(validation_errors['gpt_model'])
            profile.gpt_model = self.select_model()
            print(f'The GPT model in profile "{profile.profile_name}" has been updated')
        self.save_to_file(profile, f'profiles/{profile.profile_name}.json')

    @staticmethod
    def is_valid_profile_file(data):
        """ Validate if file is a valid profile file. """
        requires_fields = ['profile_name', 'openai_api_key', 'gpt_model']
        return all(field in data for field in requires_fields)

    def validate_profile(self, profile):
        """ Validate profile data and update it if necessary. """
        validation_errors = {}
        if not self.is_valid_openai_api_key(profile.openai_api_key):
            validation_errors['openai_api_key'] = (f'Invalid or no OpenAI API Key selected in profile '
                                                   f'"{profile.profile_name}"')
        if not self.is_valid_gpt_model(profile.gpt_model):
            validation_errors['gpt_model'] = f'Invalid or no GPT model selected for profile "{profile.profile_name}"'
        return validation_errors

    @staticmethod
    def is_valid_openai_api_key(openai_api_key):
        return len(openai_api_key) == 51 and openai_api_key.startswith('sk-') and openai_api_key[3:].isalnum()

    @staticmethod
    def is_valid_gpt_model(gpt_model):
        return gpt_model in openai_models

    def add_new_profile(self):
        """ Add a new profile. """
        while True:
            profile_name = input('Enter your new profile name: ')
            if self.is_unique_profile_name(profile_name):
                break
            else:
                print(f'Profile {profile_name} already exist')
        openai_api_key = self.get_openai_api_key_from_user()
        gpt_model = self.select_model()
        new_profile = Profile(profile_name, openai_api_key, gpt_model)
        self.save_to_file(new_profile, f'profiles/{profile_name}.json')

    def edit_profile(self):
        """ Edit a profile from the list of profiles."""
        # TODO: After selecting a profile and then editing it, selected profile is changed to None (even if no
        #  changes has been made).
        selected_profile = self.select_profile()
        profile_dict = selected_profile.as_dict()
        original_profile_name = selected_profile.profile_name
        clear_screen()

        options = {
            '1': ('profile_name', 'Enter new profile name: '),
            '2': ('openai_api_key', self.get_openai_api_key_from_user),
            '3': ('gpt_model', self.select_model)
        }

        while True:
            clear_screen()
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
        if self.profile and self.profile.profile_name == original_profile_name:
            self.profile = next((profile for profile in self.profiles if profile.profile_name == profile_dict['profile_name']), None)

    @staticmethod
    def save_to_file(profile, file_path):
        """ Save the profile to a file. """
        directory = os.path.dirname(file_path)
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(profile.as_dict(), file, indent=4)

    @staticmethod
    def display_edit_menu(profile_dict):
        """ Display the edit menu for the profile. """
        print('What you want to edit: ')
        for index, (key, _) in enumerate(profile_dict.items(), start=1):
            print(f'{index}. {key.replace("_", " ").upper()}')
        print('9. Finish editing')

    def is_unique_profile_name(self, profile_name):
        """ Check if the profile name is unique. """
        return not any(profile.profile_name == profile_name for profile in self.profiles)

    def update_profile(self, original_profile_name, profile_dict):
        """ Update the profile with new data. """
        new_profile = Profile(**profile_dict)
        self.save_to_file(new_profile, os.path.join('profiles', f'{new_profile.profile_name}.json'))
        if original_profile_name != new_profile.profile_name:
            old_file_path = os.path.join('profiles', f'{original_profile_name}.json')
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        self.profiles = self.load_profiles()

    @staticmethod
    def get_openai_api_key_from_user():
        """ Get OpenAI API key from the user. """
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
        """ Select GPT model from the list of available models."""
        while True:
            print('Select GPT model:')
            for index, model in enumerate(openai_models):
                print(f'{index}. {model}')
            choice = input(f'(0-{len(openai_models) - 1}) >>>> ')
            if choice.isdigit() and int(choice) in range(len(openai_models)):
                return openai_models[int(choice)]
            else:
                print(f'Invalid choice. Please enter a number between 0 and {len(openai_models) - 1}.')

    def save_current_profile(self, profile_name):
        """ Save the current profile information to settings.json file. """
        with open(self.settings_file, 'w') as file:
            json.dump({'current_profile': profile_name}, file)

    def display_profile_info(self):
        """ Display the current profile information. """
        if not self.profile:
            print(f'>>>>> Current profile: NO PROFILE SELECTED <<<<<')
        else:
            print(f'>>>>> Current profile: {self.profile}] <<<<<')

    def determine_current_profile(self):
        if not os.path.exists(self.settings_file):
            return None
        with open(self.settings_file, 'r') as file:
            settings = json.load(file)
        current_profile_name = settings.get('current_profile')
        return next((profile for profile in self.profiles if profile.profile_name == current_profile_name), None)


class Action:
    """ Class representing an action. """

    def __init__(self, app_inst):
        """ Initialize the action. """
        self.app_inst = app_inst

    def execute(self):
        """ Execute the action """
        raise NotImplementedError("Subclasses should implement this!")

    @staticmethod
    def log(message):
        """ Log a message. """
        print(f'[LOG] {message}')


class AddNewProfile(Action):
    """ Class representing an action of adding a new profile. """

    def __init__(self, app_inst, profile_manager):
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        """ Execute the action """
        clear_screen()
        self.log('Adding a new profile...')

        self.profile_manager.add_new_profile()

        print('New profile added.')
        input('Press Enter to continue...')
        clear_screen()
        profiles = self.profile_manager.load_profiles()
        if profiles and not self.profile_manager.profile:
            self.app_inst.stage_and_module_handler.change_stage('no_profile_selected')


class SelectProfile(Action):
    """ Class representing an action of selecting a profile. """

    def __init__(self, app_inst, profile_manager):
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        """ Execute the action """
        clear_screen()
        self.log('Profile selection...')

        profile = self.profile_manager.select_profile()

        print(f'Profile: {profile} selected.')
        input('Press Enter to continue...')
        clear_screen()
        self.app_inst.stage_and_module_handler.change_stage('profile_selected')


class EditProfile(Action):
    """ Class representing an action of editing a profile. """

    def __init__(self, app_inst, profile_manager):
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        """ Execute the action """
        clear_screen()
        self.log('Profile editing...')
        print('Which profile you want to edit?')
        self.profile_manager.edit_profile()
        print('Profile edited.')
        input('Press Enter to continue...')
        clear_screen()


class ExitProgram(Action):
    """ Class representing an action of exiting the program. """

    def __init__(self, app_inst, profile_manager):
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self):
        """ Execute the action """
        clear_screen()
        while True:
            answer = input('Are you sure you want to close this application? (Y/N) ')
            if answer.upper() == 'Y':
                clear_screen()
                sys.exit()
            if answer.upper() == 'N':
                clear_screen()
                break
            else:
                print('Invalid answer, select "Y" or "N".')
                input('Press Enter to continue...')
                clear_screen()
                pass


def run_application():
    """ Create an application instance and run it. """
    app = Application()
    app.main()


if __name__ == "__main__":
    run_application()
