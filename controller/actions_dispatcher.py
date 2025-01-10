from controller.actions.ai_actions import SetupOpenAI
from controller.actions.cards_actions import GenerateCards, WorkWithCards
from controller.actions.logging_actions import LogIn, LogOut
from controller.actions.menu_actions import AIMenu, Exit, MainMenu, ProfileMenu, SourceMenu, ExportMenu
from controller.actions.note_actions import NoteFromFile
from controller.actions.profile_actions import NewProfile, SelectProfile
from controller.actions.user_actions import NewUser, RemoveUser


class ActionsDispatcher:
    def __init__(self, context_manager, auth_manager, user_manager, file_selector):
        self.actions = {
            'login': LogIn(context_manager, auth_manager),
            'logout': LogOut(context_manager, auth_manager),
            'new_user': NewUser(user_manager),
            'remove_user': RemoveUser(auth_manager),
            'profile_menu': ProfileMenu(context_manager),
            'new_profile': NewProfile(context_manager, user_manager),
            'select_profile': SelectProfile(context_manager),
            'ai_menu': AIMenu(context_manager),
            'source_menu': SourceMenu(context_manager),
            'setup_open_ai': SetupOpenAI(context_manager, user_manager),
            'source_file': NoteFromFile(context_manager, file_selector),
            'generate_cards': GenerateCards(context_manager),
            'work_with_cards': WorkWithCards(context_manager),
            'export_cards': ExportMenu(context_manager),
            'main_menu': MainMenu(context_manager),
            'exit': Exit(auth_manager)
        }

    def dispatch(self, action_key: str) -> None:
        action = self.actions.get(action_key)
        if not action:
            print(f'[ERROR] Unknown action: {action_key}')
            input('Press enter to continue...')
            return
        action.execute()
