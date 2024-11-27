from dataclasses import dataclass
from typing import Optional

from flashcards.deck import Deck
from profiles.credentials import Credentials
from profiles.user_profile import Profile, User
from ui.menu_items import MenuState, StageState


@dataclass
class ContextManager:
    current_menu: MenuState = MenuState.LOG_MENU
    current_stage: StageState = StageState.NO_PROFILE_SELECTED
    current_user: Optional[User] = None
    current_profile: Optional[Profile] = None
    current_ai: Optional[Credentials] = None
    current_note: Optional[str] = None
    temp_deck: Optional[Deck] = None
    final_deck: Optional[Deck] = None


class MenuManager:
    def __init__(self, menus: dict, stages: dict, context_manager: ContextManager) -> None:
        self.menus = menus
        self.stages = stages
        self.context_manager = context_manager
        self.menu_items: list[str] = []

    def display_menu(self) -> None:
        self.menu_items = self._generate_menu_items()
        for item in self.menu_items:
            print(item)

    def _generate_menu_items(self) -> list[str]:
        menu_actions: dict = self._get_menu_actions()

        if all(item in menu_actions for item in self.stages[self.context_manager.current_stage]):
            return self._filter_menu_actions_by_stage(menu_actions)
        return list(menu_actions.values())

    def _get_menu_actions(self) -> dict:
        try:
            return self.menus[self.context_manager.current_menu]
        except KeyError:
            raise ValueError(f'Menu "{self.context_manager.current_menu}" not found')

    def _filter_menu_actions_by_stage(self, menu_actions: dict[str, str]) -> list[str]:
        try:
            return [menu_actions[action_key] for action_key in self.stages[self.context_manager.current_stage]]
        except KeyError:
            raise ValueError(f'Stage "{self.context_manager.current_stage}" not found.')


class UserInputHandler:
    def __init__(self, menus: dict) -> None:
        self.menus = menus

    def process_input(self, user_input: str, current_menu: str, menu_items: list[str]) -> Optional[str]:
        if not user_input.strip():
            self._prompt_for_retry('No option selected. Please provide input.')
            return None

        action_key = self._map_input_to_actions(user_input, current_menu, menu_items)
        if action_key:
            return action_key

        self._prompt_for_retry(f'Option {user_input} is not available.')
        return None

    def _map_input_to_actions(self, user_input: str, current_menu: str, menu_items: list[str]) -> Optional[str]:
        menu_actions = self.menus[current_menu]
        input_to_action_key = {v: k for k, v in menu_actions.items()}
        selected_item = next((item for item in menu_items if item.startswith(user_input)), None)
        return input_to_action_key.get(selected_item)

    @staticmethod
    def _prompt_for_retry(message: str) -> None:
        print(message)
        input('Press Enter to continue...')
