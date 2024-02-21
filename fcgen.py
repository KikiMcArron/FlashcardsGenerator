import sys

from data import *
from profile_module import *

clear_command = 'cls' if os.name == 'nt' else 'clear'


def clear_screen() -> None:
    """ Clear the screen. """
    os.system(clear_command)


class Application:
    """ Main class of the application. It is responsible for managing the flow of the application. """

    def __init__(self) -> None:
        """ Initialize the application. """
        self.current_module = None
        self.current_stage = None
        self.profile_manager = ProfileManager()
        self.current_profile = self.profile_manager.current_profile
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

    def main(self) -> None:
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

    def __init__(self, app_inst) -> None:
        """ Initialize the handler. """
        self.app_inst = app_inst

    def determine_current_stage(self) -> None:
        """ Determine the current stage of the application. """
        if not self.app_inst.profile_manager.profiles:
            self.set_current_stage('profile', 'initiation')
        elif not self.app_inst.current_profile:
            self.set_current_stage('profile', 'no_profile_selected')
        elif self.app_inst.current_profile:
            self.set_current_stage('profile', 'profile_selected')

    def set_current_stage(self, module, stage) -> None:
        """ Set the current stage of the application. """
        self.app_inst.current_module = module
        self.app_inst.current_stage = stage

    def change_stage(self, new_stage) -> None:
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

    def __init__(self, app_inst) -> None:
        """ Initialize the handler. """
        self.app_inst = app_inst

    def handle_user_input(self, user_input) -> None:
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

    def input_to_action_key(self) -> dict:
        """ Convert user input to action key. """
        menu_items_dict = module_menus[self.app_inst.current_module]
        return {v: k for k, v in menu_items_dict.items()}


class Menu:
    """ Class responsible for managing the menu of the application. """

    def __init__(self, current_module: str, current_stage: str) -> None:
        """ Initialize the menu. """
        self.current_module = current_module
        self.current_stage = current_stage
        self.items = self.get_menu_items()

    def get_menu_items(self) -> list:
        """ Get menu items for the current stage and module. """
        menu_items_dict = module_menus[self.current_module]
        return [menu_items_dict[item_id] for item_id in stages[self.current_stage]]

    def display_menu(self) -> None:
        """ Display the menu. """
        for item in self.items:
            print(item)

    def needs_update(self, new_module, new_stage) -> bool:
        """ Check if the menu needs to be updated. """
        return new_module != self.current_module or new_stage != self.current_stage

    def update(self, new_module, new_stage) -> None:
        """ Update the menu. """
        if self.needs_update(new_module, new_stage):
            self.current_module = new_module
            self.current_stage = new_stage
            self.items = self.get_menu_items()


class Action:
    """ Class representing an action. """

    def __init__(self, app_inst) -> None:
        """ Initialize the action. """
        self.app_inst = app_inst

    def execute(self) -> None:
        """ Execute the action """
        raise NotImplementedError("Subclasses should implement this!")

    @staticmethod
    def log(message) -> None:
        """ Log a message. """
        print(f'[LOG] {message}')


class AddNewProfile(Action):
    """ Class representing an action of adding a new profile. """

    def __init__(self, app_inst, profile_manager) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self) -> None:
        """ Execute the action """
        clear_screen()
        self.log('Adding a new profile...')

        self.profile_manager.add_new_profile()

        print('New profile added.')
        input('Press Enter to continue...')
        clear_screen()
        profiles = self.profile_manager.load_profiles()
        if profiles and not self.profile_manager.current_profile:
            self.app_inst.stage_and_module_handler.change_stage('no_profile_selected')


class SelectProfile(Action):
    """ Class representing an action of selecting a profile. """

    def __init__(self, app_inst, profile_manager) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self) -> None:
        """ Execute the action """
        clear_screen()
        self.log('Profile selection...')

        profile = self.profile_manager.select_current_profile()

        print(f'Profile "{profile.profile_name}" selected.')
        input('Press Enter to continue...')
        clear_screen()
        self.app_inst.stage_and_module_handler.change_stage('profile_selected')


class EditProfile(Action):
    """ Class representing an action of editing a profile. """

    def __init__(self, app_inst, profile_manager) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self) -> None:
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

    def __init__(self, app_inst, profile_manager) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)
        self.profile_manager = profile_manager

    def execute(self) -> None:
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


def run_application() -> None:
    """ Create an application instance and run it. """
    app = Application()
    app.main()


if __name__ == "__main__":
    run_application()
