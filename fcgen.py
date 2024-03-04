import sys

from data import menu_list, stages
from profile_module import ProfileManager
from source_module import SourceManager
from tools import clear_screen
from cards_module import OpenAIComms


class Application:
    """ Main class of the application. It is responsible for managing the flow of the application. """

    def __init__(self) -> None:
        """ Initialize the application. """
        self.current_menu = 'main_menu'
        self.current_stage = None
        self.profile_manager = ProfileManager()
        self.source_manager = SourceManager()
        self.current_profile = self.profile_manager.current_profile
        self.current_source = self.source_manager.current_source
        self.menu_and_stage_handler = MenuAndStageHandler(self)
        self.menu_and_stage_handler.determine_current_stage()
        self.user_input_handler = UserInputHandler(self)
        self.menu = Menu(self.current_menu, self.current_stage)
        self.action_dispatcher = {
            'new_profile': AddNewProfile(self, self.profile_manager),
            'select_profile': SelectProfile(self, self.profile_manager),
            'edit_profile': EditProfile(self, self.profile_manager),
            'select_source_note': SelectSource(self),
            'source_file': SourceFile(self),
            # 'source_notion': '',
            'generate_cards': GenerateCards(self),
            'main_menu': BackToMainMenu(self),
            'exit': ExitProgram(self, self.profile_manager)
        }

    def main(self) -> None:
        """ Main loop for the application. """
        clear_screen()
        while True:
            self.profile_manager.display_profile_info()
            self.source_manager.display_source_info()
            self.menu.update(self.current_menu, self.current_stage)
            self.menu.display_menu()
            user_input = input('>>>> ')
            self.user_input_handler.handle_user_input(user_input)


class MenuAndStageHandler:
    """ Class responsible for managing the current stage and module of the application. """

    def __init__(self, app_inst) -> None:
        """ Initialize the handler. """
        self.app_inst = app_inst

    def determine_current_stage(self) -> None:
        """ Determine the current stage of the application. """
        if not self.app_inst.profile_manager.profiles:
            self.set_current_stage('initiation')
        elif not self.app_inst.current_profile:
            self.set_current_stage('no_profile_selected')
        elif self.app_inst.current_profile and not self.app_inst.current_source:
            self.set_current_stage('profile_selected')
        elif self.app_inst.current_profile and self.app_inst.current_source:
            self.set_current_stage('note_selected')

    def set_current_menu(self, menu) -> None:
        """ Set the current stage of the application. """
        self.app_inst.current_menu = menu

    def set_current_stage(self, stage) -> None:
        """ Set the current stage of the application. """
        self.app_inst.current_stage = stage

    def change_stage(self, new_stage) -> None:
        """ Change the current stage of the application. """
        if new_stage in stages:
            self.app_inst.current_stage = new_stage
            self.app_inst.menu = Menu(self.app_inst.current_menu, self.app_inst.current_stage)
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
        menu_items_dict = menu_list[self.app_inst.current_menu]
        return {v: k for k, v in menu_items_dict.items()}


class Menu:
    """ Class responsible for managing the menu of the application. """

    def __init__(self, current_menu: str, current_stage="") -> None:
        """ Initialize the menu. """
        self.current_menu = current_menu
        self.current_stage = current_stage
        self.items = self.get_menu_items()

    def get_menu_items(self) -> list:
        """ Get menu items for the current stage and module. """
        menu_items_dict = menu_list[self.current_menu]
        if self.current_menu == 'main_menu':
            return [menu_items_dict[item_id] for item_id in stages[self.current_stage]]
        else:
            return [menu_items_dict[item_id] for item_id in menu_items_dict]

    def display_menu(self) -> None:
        """ Display the menu. """
        print('Select your next action:')
        for item in self.items:
            print(item)

    def update(self, new_menu, new_stage) -> None:
        """ Update the menu. """
        if self.needs_update(new_menu, new_stage):
            self.current_menu = new_menu
            self.current_stage = new_stage
            self.items = self.get_menu_items()

    def needs_update(self, new_menu, new_stage) -> bool:
        """ Check if the menu needs to be updated. """
        return new_menu != self.current_menu or new_stage != self.current_stage


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
            self.app_inst.menu_and_stage_handler.change_stage('no_profile_selected')


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
        if profile:
            self.app_inst.current_profile = profile
        print(f'Profile "{profile.profile_name}" selected.')
        input('Press Enter to continue...')
        clear_screen()
        if self.app_inst.current_source:
            self.app_inst.menu_and_stage_handler.change_stage('note_selected')
        else:
            self.app_inst.menu_and_stage_handler.change_stage('profile_selected')


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


class SelectSource(Action):
    """ Class representing an action of selecting a source. """

    def __init__(self, app_inst) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)

    def execute(self) -> None:
        """ Execute the action """
        clear_screen()
        self.app_inst.menu_and_stage_handler.set_current_menu('source_menu')


class SourceFile(Action):
    """ Class representing an action of selecting a TXT or PDF file as a source. """

    def __init__(self, app_inst) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)

    def execute(self) -> None:
        """ Execute the action """
        self.app_inst.current_source = self.app_inst.source_manager.load_note()
        clear_screen()
        if self.app_inst.current_source:
            self.app_inst.menu_and_stage_handler.set_current_menu('source_menu')
            self.app_inst.menu_and_stage_handler.set_current_stage('note_selected')


class GenerateCards(Action):
    """ Class representing an action of generating flashcards. """

    def __init__(self, app_inst) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)

    def execute(self) -> None:
        """ Execute the action """
        clear_screen()
        if not self.app_inst.current_profile:
            print('No profile selected.')
            input('Press Enter to continue...')
            clear_screen()
            return
        self.log('Generating flashcards...')
        api_key = self.app_inst.current_profile.openai_api_key
        model = self.app_inst.current_profile.gpt_model
        content = self.app_inst.source_manager.read_note_content()
        openai_comms = OpenAIComms(api_key)
        flashcards = openai_comms.generate_flashcards(model, content)
        if flashcards:
            print(f'Flashcards generated: {flashcards}')
            self.app_inst.menu_and_stage_handler.change_stage('cards_generated')
        else:
            print('Flashcards could not be generated.')
        input('Press Enter to continue...')
        clear_screen()


class BackToMainMenu(Action):
    """ Class representing an action of going back to the profile menu. """

    def __init__(self, app_inst) -> None:
        """ Initialize the action. """
        super().__init__(app_inst)

    def execute(self) -> None:
        """ Execute the action """
        clear_screen()
        self.app_inst.menu_and_stage_handler.set_current_menu('main_menu')


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
