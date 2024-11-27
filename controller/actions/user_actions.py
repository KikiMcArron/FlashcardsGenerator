import stdiomask  # type: ignore

from controller.actions.base_action import Action
from custom_exceptions import ValidationError
from profiles.manager import AuthenticationManager, UserManager
from profiles.security import PasswordValidator
from utils import clear_screen


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
