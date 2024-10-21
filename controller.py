import stdiomask  # type: ignore

from profiles.manager import UserManager, AuthenticationManager
from profiles.security import PasswordValidator, Bcrypt
from ui.ui_manager import ContextManager, MenuManager
from utils import clear_screen
from custom_exceptions import ValidationError, InvalidUsername, InvalidPassword, UserAlreadyExists
from settings import USERS_FILE, STORAGE_DIR


class Application:
    def __init__(self):
        self.context_manager = ContextManager()
        self.menu_manager = MenuManager(self.context_manager)
        self.encryption_strategy = Bcrypt()
        self.user_manager = UserManager(self.encryption_strategy)
        self.auth_manager = AuthenticationManager(self.user_manager)
        self.action_dispatcher = {
            'login': LogIn(self.context_manager, self.auth_manager),
            'logout': LogOut(self.context_manager, self.auth_manager),
            'new_user': NewUser(self.user_manager)
            # 'new_profile': AddNewProfile(self, self.profile_manager),
            # 'select_profile': SelectProfile(self, self.profile_manager),
            # 'edit_profile': EditProfile(self, self.profile_manager),
            # 'select_source_note': SelectSource(self),
            # 'source_file': SourceFile(self),
            # 'source_notion': '',
            # 'generate_cards': GenerateCards(self),
            # 'main_menu': BackToMainMenu(self),
            # 'exit': ExitProgram(self, self.profile_manager)
        }

    def main(self):
        clear_screen()
        while True:
            print('Select your action:')
            self.menu_manager.display_menu()
            user_input = input('>>>>> ')
            action_key = self.menu_manager.process_input(user_input)
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
        self.user_manager = self.auth_manager.user_manager

    def execute(self):
        clear_screen()
        self.log('Logging in...')
        user_name = input('Username: ')
        if not self.user_manager.user_exists(user_name):
            self.log(f'User "{user_name}" doesn\'t exists, try again with a different user name or create new user.')
            input('Press enter to continue...')
            return
        password = stdiomask.getpass(prompt='Password: ')
        try:
            self.auth_manager.login_user(user_name, password)
            self.context_manager.update_user(self.user_manager.users[user_name])
            self.context_manager.update_menu('main_menu')
            self.log(f'User {user_name} logged in successfully!')
        except InvalidUsername:
            self.log('Invalid username. Try again or create new user.')
        except InvalidPassword:
            self.log('Invalid password.')
        input('Press enter to continue...')


class LogOut(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self):
        clear_screen()
        self.log('Logging out...')
        self.auth_manager.logout_all_users()
        self.log('Logged out successfully!')
        self.context_manager.update_menu('log_menu')
        input('Press enter to continue...')


class NewUser(Action):
    def __init__(self, user_manager: UserManager) -> None:
        self.password_validator = PasswordValidator()
        self.user_manager = user_manager

    def execute(self):
        clear_screen()
        self.log('Adding new user...')
        user_name = input('Please provide new username: ')
        if self.user_manager.user_exists(user_name):
            self.log(f'User {user_name} already exists, try again with a different name or login for existing user.')
            input('Press enter to continue...')
            return
        while True:
            password = stdiomask.getpass(prompt='Please provide your password: ')
            try:
                self._validate_password(password)
                self.user_manager.add_user(user_name,
                                           password)
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


app = Application()
app.main()
