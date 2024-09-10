main_menu = {
    'new_profile': '1. Add new profile',
    'select_profile': '2. Select profile',
    'edit_profile': '3. Edit profile',
    'select_source_note': '4. Select source note',
    'generate_cards': '5. Generate flashcards',
    'work_with_cards': '6. Work with flashcards',
    'exit': '9. Quit program'
}

source_menu = {
    'source_file': '1. Select the note from file (.txt)',
    'source_notion': '2. Select Notion note (coming soon)',
    'main_menu': '8. Back to main menu',
    'exit': '9. Quit program'
}

menu_list = {
    'main_menu': main_menu,
    'source_menu': source_menu
}

stages = {
    'initiation': ['new_profile', 'exit'],
    'no_profile_selected': ['new_profile', 'select_profile', 'edit_profile', 'exit'],
    'profile_selected': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'exit'],
    'note_selected': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'generate_cards', 'exit'],
    'cards_generated': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'generate_cards',
                        'work_with_cards', 'exit'],
}