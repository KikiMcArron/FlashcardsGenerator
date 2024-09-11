from ui.menu_items import menu_list, stages
from typing import Optional


class MenuHandler:
    def __init__(self, current_menu: str, current_stage: str = ''):
        self.current_menu = current_menu
        self.current_stage = current_stage
        self.menu_items = self._build_menu_items()

    def _build_menu_items(self):
        menu_items_dict = self._get_menu_list()

        if self.current_menu == 'main_menu':
            return self._filtered_menu_by_stage(menu_items_dict)
        return list(menu_items_dict.values())

    def _get_menu_list(self) -> dict:
        try:
            return menu_list[self.current_menu]
        except KeyError:
            raise ValueError(f'Menu "{self.current_menu}" not found')

    def _filtered_menu_by_stage(self, menu_items_dict):
        try:
            return [menu_items_dict[item_id] for item_id in stages[self.current_stage]]
        except KeyError:
            raise ValueError(f'Stage "{self.current_stage}" not found.')

    def display_menu(self):
        print('Select your action:')
        for item in self.menu_items:
            print(item)


class UserInputHandler:
    def __init__(self, current_menu: str, available_items: list):
        self.current_menu = current_menu
        self.available_items = available_items

    def input_to_action(self, input_value: str) -> Optional[str]:
        """Process user input and ensure it matches displayed menu items."""
        menu_items_dict = menu_list[self.current_menu]
        input_to_action_key = {v: k for k, v in menu_items_dict.items()}

        # Validate user input only against the available items (filtered menu)
        matching_items = [item for item in self.available_items if item.startswith(input_value)]

        if matching_items:
            selected_item = matching_items[0]  # Taking the first match for simplicity
            action_key = input_to_action_key[selected_item]
            print(f"Action selected: {action_key}")
            return action_key

        print(f'Option "{input_value}" is not available.')
        input('Press Enter to continue...')
        return None

