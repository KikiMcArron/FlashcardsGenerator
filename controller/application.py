from controller.actions_dispatcher import ActionsDispatcher
from profiles.manager import AuthenticationManager, UserManager
from profiles.repository import JSONStorage
from profiles.security import Bcrypt
from settings import FILE_TYPES, STORAGE_DIR, USERS_FILE
from ui.gui import FileSelector
from ui.menu_items import menus, stages
from ui.ui_manager import ContextManager, MenuManager, UserInputHandler
from utils import clear_screen


class Application:
    def __init__(self):
        self.context_manager = ContextManager()
        self.menu_manager = MenuManager(menus, stages, self.context_manager)
        self.input_handler = UserInputHandler(menus)
        self.encryption_strategy = Bcrypt()
        self.storage = JSONStorage(f'{STORAGE_DIR}/{USERS_FILE}')
        self.user_manager = UserManager(self.encryption_strategy, self.storage)
        self.auth_manager = AuthenticationManager(self.user_manager)
        self.file_selector = FileSelector(FILE_TYPES)

        self.actions_dispatcher = ActionsDispatcher(
            self.context_manager,
            self.auth_manager,
            self.user_manager,
            self.file_selector,
        )

    def main(self):
        clear_screen()
        while True:
            print('Select your action:')
            self.menu_manager.display_menu()
            user_input = input('>>>>> ')
            action_key = self.input_handler.process_input(
                user_input,
                self.context_manager.current_menu,
                self.menu_manager.menu_items
            )
            clear_screen()
            if not action_key:
                continue
            self.actions_dispatcher.dispatch(action_key)
            clear_screen()
