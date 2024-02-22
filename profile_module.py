# Module responsible for managing profiles.

import os
import json
import stdiomask

from data import openai_models
from fcgen import clear_screen


# TODO: Add encryption for profile files
# TODO: Add logging


class Profile:
    """ Class representing a profile. """

    def __init__(self, profile_name=None, openai_api_key=None, gpt_model=None) -> None:
        """ Initialize the profile. """
        self.profile_name = profile_name
        self.openai_api_key = openai_api_key
        self.gpt_model = gpt_model

    def __str__(self) -> str:
        """ Return a string representation of the profile. """
        return (f'{self.profile_name} (OpenAI API Key: sk-...{self.openai_api_key[-4:]}, GPT Model: '
                f'{self.gpt_model})')

    def as_dict(self) -> dict:
        """ Return the profile as a dictionary. """
        return {
            'profile_name': self.profile_name,
            'openai_api_key': self.openai_api_key,
            'gpt_model': self.gpt_model
        }


class ProfileManager:
    """ Class responsible for managing profiles. """

    def __init__(self, profiles_dir='profiles', settings_file='settings.json') -> None:
        """ Initialize the profile manager. """
        self.validator = ProfileValidations()
        self.ui_handler = ProfileUIHandler()
        self.settings_file = settings_file
        self.profiles_dir = profiles_dir
        self.profiles = self.load_profiles()
        self.current_profile = self.determine_current_profile()

    def determine_current_profile(self) -> Profile:
        if not os.path.exists(self.settings_file):
            return None
        with open(self.settings_file, 'r') as file:
            settings = json.load(file)
        current_profile_name = settings.get('current_profile')
        return next((profile for profile in self.profiles if profile.profile_name == current_profile_name), None)

    def display_profile_info(self) -> None:
        """ Display the current profile information. """
        if not self.current_profile:
            print('>>>>> Current profile: NO PROFILE SELECTED <<<<<')
        else:
            print(f'>>>>> Current profile: {self.current_profile}] <<<<<')

    def load_profiles(self) -> list:
        """ Load profiles from files. """
        self.validator.ensure_dir_exists(self.profiles_dir)
        profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.profiles_dir, filename)
                with open(file_path, 'r') as file:
                    try:
                        profile_data = json.load(file)
                        if self.validator.is_valid_profile_file(profile_data):
                            profile = Profile(**profile_data)
                            profiles.append(profile)
                    except json.JSONDecodeError:
                        print(f'Error decoding JSON from file "{file_path}".')
        return profiles

    def select_current_profile(self) -> Profile:
        """ Select a profile from the list of profiles. """
        self.profiles = self.load_profiles()
        self.current_profile = self.ui_handler.profile_selection(self.profiles)
        self.validator.validate_profile(self.current_profile)
        self.update_profile_if_needed(self.current_profile)
        self.save_current_profile(self.current_profile.profile_name)
        return self.current_profile

    def update_profile_if_needed(self, profile) -> None:
        """ Update the profile if necessary. """
        validation_errors = self.validator.validate_profile(profile)

        if 'openai_api_key' in validation_errors:
            clear_screen()
            print(validation_errors['openai_api_key'])
            profile.openai_api_key = self.ui_handler.get_openai_api_key_from_user()
            print(f'The OpenAI Key in profile "{profile.profile_name}" has been updated')

        if 'gpt_model' in validation_errors:
            clear_screen()
            print(validation_errors['gpt_model'])
            profile.gpt_model = self.ui_handler.select_model()
            print(f'The GPT model in profile "{profile.profile_name}" has been updated')
        self.save_to_file(profile, f'profiles/{profile.profile_name}.json')

    def add_new_profile(self) -> None:
        """ Add a new profile. """
        while True:
            profile_name = input('Enter your new profile name: ')
            if self.validator.is_unique_profile_name(self.profiles, profile_name):
                break
            else:
                print(f'Profile {profile_name} already exist')

        openai_api_key = self.ui_handler.get_openai_api_key_from_user()
        gpt_model = self.ui_handler.select_model()
        new_profile = Profile(profile_name, openai_api_key, gpt_model)
        self.save_to_file(new_profile, f'profiles/{profile_name}.json')

    def edit_profile(self) -> None:
        """ Edit a profile from the list of profiles."""
        profile = self.ui_handler.profile_selection(self.profiles)
        profile_dict = profile.as_dict()
        original_profile_name = profile.profile_name
        clear_screen()

        options = {
            '1': ('profile_name', 'Enter new profile name: ', 'Profile name has been updated'),
            '2': ('openai_api_key', self.ui_handler.get_openai_api_key_from_user, 'OpenAI API Key has been updated'),
            '3': ('gpt_model', self.ui_handler.select_model, 'GPT model has been updated')
        }

        while True:
            clear_screen()
            self.ui_handler.display_edit_menu(profile_dict)
            choice = input('Select >>>>  ')

            if choice in options:
                field, handler, message = options[choice]
                if callable(handler):
                    clear_screen()
                    profile_dict[field] = handler()
                    print(message)
                    input('Press Enter to continue...')
                else:
                    clear_screen()
                    profile_dict[field] = input(handler)
                    print(message)
                    input('Press Enter to continue...')
                if field == 'profile_name' and not self.validator.is_unique_profile_name(self.profiles,
                                                                                         profile_dict[field]):
                    print(f'Profile {profile_dict[field]} already exists. Please choose a different name.')
                    continue
            elif choice == '9':
                break
            else:
                print('Invalid choice. Please select 1-3 to edit selected element or 9 to finish editing.')

        self.update_profile(original_profile_name, profile_dict)
        if self.current_profile and self.current_profile.profile_name == original_profile_name:
            self.current_profile = next(
                (profile for profile in self.profiles if profile.profile_name == profile_dict['profile_name']), None)
            self.save_current_profile(self.current_profile.profile_name)

    def save_to_file(self, profile, file_path) -> None:
        """ Save the profile to a file. """
        directory = os.path.dirname(file_path)
        self.validator.ensure_dir_exists(directory)
        with open(file_path, 'w') as file:
            json.dump(profile.as_dict(), file, indent=4)

    def update_profile(self, original_profile_name, profile_dict) -> None:
        """ Update the profile with new data. """
        new_profile = Profile(**profile_dict)
        self.save_to_file(new_profile, os.path.join('profiles', f'{new_profile.profile_name}.json'))
        if original_profile_name != new_profile.profile_name:
            old_file_path = os.path.join('profiles', f'{original_profile_name}.json')
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        self.profiles = self.load_profiles()

    def save_current_profile(self, profile_name) -> None:
        """ Save the current profile information to settings.json file. """
        try:
            with open(self.settings_file, 'r') as file:
                settings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}

        settings['current_profile'] = profile_name

        with open(self.settings_file, 'w') as file:
            json.dump(settings, file, indent=4)


class ProfileUIHandler:
    """ Class responsible for handling the profile UI. """

    def __init__(self) -> None:
        """ Initialize the handler. """

    pass

    def profile_selection(self, profiles) -> Profile:
        """ Select a profile from the list of profiles. """
        self.profile_selection_menu(profiles)
        while True:
            choice = input(f'Select profile (1{"-" + str(len(profiles)) if len(profiles) > 1 else ""}) >>>> ')
            if choice.isdigit() and int(choice) in range(1, len(profiles) + 1):
                return profiles[int(choice) - 1]
            else:
                print(f'Invalid choice. Please enter a number between 1 and {len(profiles)}')

    @staticmethod
    def profile_selection_menu(profiles) -> None:
        """ Display the profile selection menu. """
        print('Select profile: ')
        for index, profile in enumerate(profiles, start=1):
            print(f'{index}. {profile}')
        # TODO Add option: print('9. Back to previews menu')

    @staticmethod
    def get_openai_api_key_from_user() -> str:
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
    def display_edit_menu(profile_dict) -> None:
        """ Display the edit menu for the profile. """
        print('What you want to edit: ')
        for index, (key, _) in enumerate(profile_dict.items(), start=1):
            print(f'{index}. {key.replace("_", " ").upper()}')
        print('9. Finish editing')

    @staticmethod
    def select_model() -> str:
        """ Select GPT model from the list of available models."""
        while True:
            print('Select GPT model:')
            for index, model in enumerate(openai_models, start=1):
                print(f'{index}. {model}')
            choice = input(f'(1-{len(openai_models)}) >>>> ')
            if choice.isdigit() and int(choice) in range(1, len(openai_models) + 1):
                return openai_models[int(choice) - 1]
            else:
                print(f'Invalid choice. Please enter a number between 1 and {len(openai_models)}.')


class ProfileValidations:
    """ Class responsible for validating profiles. """

    @staticmethod
    def ensure_dir_exists(directory) -> None:
        """ Ensure that the directory exists. """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def is_unique_profile_name(profiles, profile_name) -> bool:
        """ Check if the profile name is unique. """
        return not any(profile.profile_name == profile_name for profile in profiles)

    @staticmethod
    def is_valid_profile_file(data) -> bool:
        """ Validate if file is a valid profile file. """
        requires_fields = ['profile_name', 'openai_api_key', 'gpt_model']
        return all(field in data for field in requires_fields)
        pass

    def validate_profile(self, profile) -> dict:
        """ Validate the profile. """
        validation_errors = {}
        if not self.is_valid_openai_api_key(profile.openai_api_key):
            validation_errors['openai_api_key'] = 'Invalid or no OpenAI API Key selected'
        if not self.is_valid_gpt_model(profile.gpt_model):
            validation_errors['gpt_model'] = 'Invalid or no GPT model selected'
        return validation_errors

    @staticmethod
    def is_valid_openai_api_key(openai_api_key) -> bool:
        return len(openai_api_key) == 51 and openai_api_key.startswith('sk-') and openai_api_key[3:].isalnum()

    @staticmethod
    def is_valid_gpt_model(gpt_model) -> bool:
        return gpt_model in openai_models
