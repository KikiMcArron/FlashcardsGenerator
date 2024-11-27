import sys
from controller.actions.base_action import Action
from ui.ui_manager import ContextManager
from ui.menu_items import MenuState
from utils import clear_screen
from profiles.manager import AuthenticationManager


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
                self.error('Invalid answer, select "Y" or "N".')
                clear_screen()
