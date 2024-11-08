import stdiomask  # type: ignore
import sys

from custom_exceptions import InvalidPassword, ValidationError, DuplicateProfileError
from profiles.user_profile import Profile
from profiles.manager import AuthenticationManager, UserManager
from profiles.repository import JSONStorage
from profiles.security import Bcrypt, PasswordValidator
from settings import STORAGE_DIR, USERS_FILE
from ui.ui_manager import ContextManager, MenuManager
from ui.menu_items import MenuState, StageState
from utils import clear_screen


class Application:
    def __init__(self):
        self.context_manager = ContextManager()
        self.menu_manager = MenuManager(self.context_manager)
        self.encryption_strategy = Bcrypt()
        self.storage = JSONStorage(f'{STORAGE_DIR}/{USERS_FILE}')
        self.user_manager = UserManager(self.encryption_strategy, self.storage)
        self.auth_manager = AuthenticationManager(self.user_manager)
        # TODO: Do I need this action_dispatcher. Maybe I can execute menu actions via class method
        self.action_dispatcher = {
            'login': LogIn(self.context_manager, self.auth_manager),
            'logout': LogOut(self.context_manager, self.auth_manager),
            'new_user': NewUser(self.user_manager),
            'remove_user': RemoveUser(self.auth_manager),
            'new_profile': NewProfile(self.context_manager, self.user_manager),
            'select_profile': SelectProfile(self.context_manager),
            'profile_menu': ProfileMenu(self.context_manager),
            'ai_menu': AIMenu(self.context_manager),
            'source_menu': SourceMenu(self.context_manager),
            # 'edit_profile': EditProfile(self, self.profile_manager),
            # 'select_source_note': SelectSource(self),
            # 'source_file': SourceFile(self),
            # 'source_notion': '',
            # 'generate_cards': GenerateCards(self),
            'main_menu': MainMenu(self.context_manager),
            'exit': Exit(self.auth_manager)
        }

    def main(self):
        clear_screen()
        while True:
            if self.context_manager.current_user:
                print('###########################################################')
                print(f'                Active user: "{self.context_manager.current_user.user_name}".')
                print('###########################################################\n')
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


class LogIn(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self) -> None:
        user_manager = self.auth_manager.user_manager
        if not user_manager.users:
            self.log('No users! Please create new user first.')
            input('Press enter to continue...')
            return
        self.log('Logging in...')
        user_name = input('Username: ')
        if not user_manager.user_exists(user_name):
            self.log(f'User "{user_name}" doesn\'t exists, try again with a different user name or create new user.')
            input('Press enter to continue...')
            return
        password = stdiomask.getpass(prompt='Password: ')
        try:
            self.auth_manager.login_user(user_name, password)
            self.context_manager.current_user = user_manager.users[user_name]
            self.context_manager.current_menu = MenuState.MAIN_MENU
            if self.context_manager.current_user.profiles:
                self.context_manager.current_stage = StageState.NO_PROFILE_SELECTED
            self.log(f'User {user_name} logged in successfully!')
        except InvalidPassword:
            self.log('Invalid password.')
        input('Press enter to continue...')


class LogOut(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self) -> None:
        self.log('Logging out...')
        self.auth_manager.logout_users()
        self.log('Logged out successfully!')
        self.context_manager.current_menu = MenuState.LOG_MENU
        self.context_manager.current_user = None
        input('Press enter to continue...')


class NewUser(Action):
    def __init__(self, user_manager: UserManager) -> None:
        self.password_validator = PasswordValidator()
        self.user_manager = user_manager

    def execute(self) -> None:
        self.log('Adding new user...')
        user_name = input('Please provide new username: ')
        if not user_name:
            self.log('User name can\'t be empty.')
            input('Press enter to continue...')
            return
        if self.user_manager.user_exists(user_name):
            self.log(f'User {user_name} already exists, try again with a different name or login for existing user.')
            input('Press enter to continue...')
            return
        while True:
            # TODO: Add double check password functionality
            password = stdiomask.getpass(prompt='Please provide your password: ')
            try:
                self._validate_password(password)
                self.user_manager.add_user(user_name, password)
                self.user_manager.get_user(user_name).add_profile(Profile('main'))
                self.log('User added successfully!')
                input('Press enter to continue...')
                return
            except ValueError as e:
                if "Password validation failed" in str(e):
                    self.log(f'Error: {e}')
                    self.log('Please try again with a different password.')
                else:
                    raise

    def _validate_password(self, password: str) -> None:
        try:
            self.password_validator.is_valid(password)
        except ValidationError as e:
            raise ValueError(f'Password validation failed: {e}')


class RemoveUser(Action):
    def __init__(self, auth_manager: AuthenticationManager) -> None:
        self.auth_manager = auth_manager

    def execute(self) -> None:
        user_manager = self.auth_manager.user_manager
        if not user_manager.users:
            self.log('No users! Please create new user first.')
            input('Press enter to continue...')
            return
        self.log('Removing user...')
        user_name = input('Please provide username to remove: ')
        if not user_manager.user_exists(user_name):
            self.log(f'User "{user_name}" doesn\'t exists.')
            input('Press enter to continue...')
            return
        password = stdiomask.getpass(prompt=f'Please provide password for user "{user_name}": ')
        if not self.auth_manager.password_match(user_manager.users[user_name], password):
            self.log('Invalid password.')
            input('Press enter to continue...')
            return
        # TODO: Add confirmation of user deletion.
        user_manager.remove_user(user_name)
        self.log(f'User "{user_name}" removed successful.')
        input('Press enter to continue...')


class ProfileMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.PROFILE_MENU


class AIMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.AI_MENU


class SourceMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.SOURCE_MENU


class MainMenu(Action):
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager

    def execute(self):
        self.context_manager.current_menu = MenuState.MAIN_MENU


class NewProfile(Action):
    def __init__(self, context_manager: ContextManager, user_manager: UserManager) -> None:
        self.context_manager = context_manager
        self.user_manager = user_manager

    def execute(self):
        self.log('Adding new profile...')
        current_user = self.context_manager.current_user
        profile_name = input('Provide New Profile name: ')
        if not profile_name:
            self.log('Profile name can\'t be empty.')
            input('Press enter to continue...')
            return
        try:
            current_user.add_profile(Profile(profile_name))
            self.user_manager.save_users()
            if self.context_manager.current_profile:
                self.context_manager.current_stage = 'profile_selected'
            else:
                self.context_manager.current_stage = 'no_profile_selected'
            self.log(f'Profile "{profile_name}" created successful.')
            input('Press enter to continue...')
            return
        except DuplicateProfileError:
            self.log(f'Profile "{profile_name}" already exist.\nTry other profile name or use exist profile.''')
            input('Press enter to continue...')
            return


class SelectProfile(Action):
    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager

    def execute(self):
        self.log('Profile selection...')
        profile_name = input('Please provide profile name: ')
        if not self.context_manager.current_user.profile_exists(profile_name):
            self.log(f'Profile "{profile_name}" does\'t exists, try again with a different profile name or create new.')
            input('Press enter to continue...')
            return
        self.context_manager.current_profile = self.context_manager.current_user.get_profile(profile_name)
        self.context_manager.current_stage = StageState.NO_AI
        self.log(f'Profile "{profile_name}" selected.')
        input('Press enter to continue...')
        return


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
                print('Invalid answer, select "Y" or "N".')
                input('Press Enter to continue...')
                clear_screen()


app = Application()
app.main()
