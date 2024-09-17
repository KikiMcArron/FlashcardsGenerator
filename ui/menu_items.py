log_menu = {
    'login': '1. Login',
    'new_user': '2. Add user',
    'remove_user': '3. Remove user',
    'exit': '0. Quit program'
}

main_menu = {
    'new_profile': '1. Add new profile',
    'select_profile': '2. Select profile',
    'edit_profile': '3. Edit profile',
    'select_source_note': '4. Select source note',
    'generate_cards': '5. Generate flashcards',
    'work_with_cards': '6. Work with flashcards',
    'logout': '9. Logout current user',
    'exit': '0. Quit program'
}

source_menu = {
    'source_file': '1. Select the note from file (.txt)',
    'source_notion': '2. Select Notion note (coming soon)',
    'main_menu': '8. Back to main menu',
    'logout': '9. Logout current user',
    'exit': '0. Quit program'
}

menu_list = {
    'log_menu': log_menu,
    'main_menu': main_menu,
    'source_menu': source_menu
}

stages = {
    'initiation': ['new_profile', 'logout', 'exit'],
    'no_profile_selected': ['new_profile', 'select_profile', 'edit_profile', 'logout', 'exit'],
    'profile_selected': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'logout', 'exit'],
    'note_selected': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'generate_cards',
                      'logout', 'exit'],
    'cards_generated': ['new_profile', 'select_profile', 'edit_profile', 'select_source_note', 'generate_cards',
                        'work_with_cards', 'logout', 'exit']
}
