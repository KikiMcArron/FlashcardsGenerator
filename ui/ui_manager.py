from dataclasses import dataclass, field
from typing import Optional, List
from ui.menu_items import menu_list, stages
from profiles.user_profile import User, Profile


@dataclass
class ContextManager:
    current_menu: str = 'log_menu'
    current_stage: str = 'initiation'
    current_user: Optional[User] = None
    current_profile: Optional[Profile] = None


class MenuManager:
    def __init__(self, context_manager: ContextManager) -> None:
        self.context_manager = context_manager
        self.menu_items: List[str] = []

    def display_menu(self) -> None:
        self.menu_items = self._build_menu_items()
        for item in self.menu_items:
            print(item)

    def process_input(self, input_value: str) -> Optional[str]:
        if not input_value.strip():
            print('No option selected. Please provide input.')
            input('Press Enter to continue...')
            return None

        current_menu = self.context_manager.current_menu
        menu_items_dict = menu_list[current_menu]
        input_to_action_key = {v: k for k, v in menu_items_dict.items()}
        selected_item = next((item for item in self.menu_items if item.startswith(input_value)), None)

        if selected_item:
            action_key = input_to_action_key[selected_item]
            return action_key

        print(f'Option {input_value} is not available.')
        input('Press Enter to continue...')
        return None

    def _build_menu_items(self) -> list[str]:
        current_menu: str = self.context_manager.current_menu
        current_stage: str = self.context_manager.current_stage

        menu_items_dict: dict[str, str] = self._get_menu_list(current_menu)

        if all(item in menu_items_dict for item in stages[current_stage]):
            return self._filtered_menu_by_stage(menu_items_dict, current_stage)
        return list(menu_items_dict.values())

    @staticmethod
    def _get_menu_list(current_menu: str) -> dict:
        try:
            return menu_list[current_menu]
        except KeyError:
            raise ValueError(f'Menu "{current_menu}" not found')

    @staticmethod
    def _filtered_menu_by_stage(menu_items_dict: dict[str, str], current_stage: str) -> list[str]:
        try:
            return [menu_items_dict[item_id] for item_id in stages[current_stage]]
        except KeyError:
            raise ValueError(f'Stage "{current_stage}" not found.')
