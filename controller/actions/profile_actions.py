from controller.actions.base_action import Action
from ui.ui_manager import ContextManager
from profiles.manager import UserManager
from profiles.user_profile import Profile
from custom_exceptions import DuplicateProfileError
from ui.menu_items import StageState


class NewProfile(Action):
    def __init__(self, context_manager: ContextManager, user_manager: UserManager) -> None:
        self.context_manager = context_manager
        self.user_manager = user_manager

    def execute(self):
        self.log('Adding new profile...')
        current_user = self.context_manager.current_user
        profile_name = input('Provide New Profile name: ')
        if not profile_name:
            self.error('Profile name can\'t be empty.')
            return
        try:
            current_user.add_profile(Profile(profile_name))
            self.user_manager.save_users()
            if not self.context_manager.current_profile:
                self.context_manager.current_stage = StageState.NO_PROFILE_SELECTED
            self.info(f'Profile "{profile_name}" created successful.')
            return
        except DuplicateProfileError:
            self.error(f'Profile "{profile_name}" already exist.\nTry other profile name or use exist profile.''')
            return


class SelectProfile(Action):
    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager

    def execute(self):
        self.log('Profile selection...')
        profile_name = input('Please provide profile name: ')
        if not self.context_manager.current_user.profile_exists(profile_name):
            self.error(
                f'Profile "{profile_name}" does\'t exists, try again with a different profile name or create new.')
            return
        self.context_manager.current_profile = self.context_manager.current_user.get_profile(profile_name)
        if not self.context_manager.current_ai:
            self.context_manager.current_stage = StageState.NO_AI
        self.info(f'Profile "{profile_name}" selected.')
        return
