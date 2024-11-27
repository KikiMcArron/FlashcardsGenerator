import stdiomask  # type: ignore

from controller.actions.base_action import Action
from custom_exceptions import InvalidPassword
from profiles.manager import AuthenticationManager
from ui.menu_items import MenuState, StageState
from ui.ui_manager import ContextManager


class LogIn(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self) -> None:
        user_manager = self.auth_manager.user_manager
        if not user_manager.users:
            self.error('No users! Please create new user first.')
            return
        self.log('Logging in...')
        user_name = input('Username: ')
        if not user_manager.user_exists(user_name):
            self.error(
                f'User "{user_name}" doesn\'t exists, try again with a different user name or create new user.')
            return
        password = stdiomask.getpass(prompt='Password: ')
        try:
            self.auth_manager.login_user(user_name, password)
        except InvalidPassword:
            self.error('Invalid password.')
            return
        user = user_manager.users[user_name]
        self.context_manager.current_user = user
        self.context_manager.current_menu = MenuState.MAIN_MENU
        profile = self.context_manager.current_user.get_profile('main')
        self.context_manager.current_profile = profile
        default_ai = profile.default_ai
        if default_ai:
            self.context_manager.current_ai = profile.get_credentials(default_ai)
            self.context_manager.current_stage = StageState.NO_NOTE_SELECTED
        else:
            self.context_manager.current_stage = StageState.NO_AI
        self.info(f'User {user_name} logged in successfully!')


class LogOut(Action):
    def __init__(self, context_manager: ContextManager, auth_manager: AuthenticationManager) -> None:
        self.context_manager = context_manager
        self.auth_manager = auth_manager

    def execute(self) -> None:
        self.log('Logging out...')
        self.auth_manager.logout_users()
        self.context_manager.current_menu = MenuState.LOG_MENU
        self.context_manager.current_user = None
        self.info('Logged out successfully!')
