from enum import Enum


class MenuState(str, Enum):
    LOG_MENU = 'log_menu'
    MAIN_MENU = 'main_menu'
    PROFILE_MENU = 'profile_menu'
    AI_MENU = 'ai_menu'
    SOURCE_MENU = 'source_menu'


class StageState(str, Enum):
    NO_PROFILE_SELECTED = 'no_profile_selected'
    NO_AI = 'no_ai'
    NO_NOTE_SELECTED = 'no_note_selected'
    NO_CARDS_GENERATED = 'no_cards_generated'
    CARDS_GENERATED = 'cards_generated'


log_menu = {
    'login': '1. Login',
    'new_user': '2. Add user',
    'remove_user': '3. Remove user',
    'exit': '0. Quit program'
}

main_menu = {
    'profile_menu': '1. Manage profiles',
    'ai_menu': '2. Configure AI',
    'source_menu': '3. Select source note',
    'generate_cards': '4. Generate flashcards',
    'work_with_cards': '5. Work with flashcards',
    'logout': '9. Logout',
    'exit': '0. Quit program'
}

profile_menu = {
    'new_profile': '1. Add new profile',
    'select_profile': '2. Select profile',
    'edit_profile': '3. Edit profile',
    'main_menu': '8. Back to main menu',
    'logout': '9. Logout',
    'exit': '0. Quit program'
}

ai_menu = {
    'setup_open_ai': '1. Setup OpenAI',
    'main_menu': '8. Back to main menu',
    'logout': '9. Logout',
    'exit': '0. Quit program'
}

source_menu = {
    'source_file': '1. Select the note from file (.txt)',
    'source_notion': '2. Select Notion note (coming soon)',
    'main_menu': '8. Back to main menu',
    'logout': '9. Logout',
    'exit': '0. Quit program'
}

menu_list = {
    'log_menu': log_menu,
    'main_menu': main_menu,
    'profile_menu': profile_menu,
    'ai_menu': ai_menu,
    'source_menu': source_menu
}

stages = {
    'no_profile_selected': ['profile_menu', 'logout', 'exit'],
    'no_ai': ['profile_menu', 'ai_menu', 'logout', 'exit'],
    'no_note_selected': ['profile_menu', 'ai_menu', 'source_menu', 'logout', 'exit'],
    'no_cards_generated': ['profile_menu', 'ai_menu', 'source_menu', 'generate_cards', 'logout', 'exit'],
    'cards_generated': ['profile_menu', 'ai_menu', 'source_menu', 'generate_cards', 'work_with_cards', 'logout', 'exit']
}
