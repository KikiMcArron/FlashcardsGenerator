from flashcards.deck import Card, Deck
from flashcards.editor import DataclassEditor
import utils

CARDS = [Card(front='Front 1', back='Back 1'), Card(front='Front 2', back='Back 2'),
         Card(front='Front 3', back='Back 3')]


def main():
    card_editor = DataclassEditor[Card](display_fields=['card_id', 'front'])
    tmp_deck = Deck()
    tmp_deck.load_cards(CARDS)
    final_deck = Deck()

    for card in tmp_deck.cards:
        print(card)
        print('---')
        print('What you want to do with this card?')
        print('1. Approve card.')
        print('2. Reject card.')
        print('3. Edit card.')
        answer = input('1-3: ')
        if answer == '1':
            final_deck.load_cards([card])
        elif answer == '2':
            print('Card rejected.')
        elif answer == '3':
            edited_card = card_editor.edit_dataclass(card)
            final_deck.load_cards([Card(front=edited_card.front, back=edited_card.back)])
        input('Press enter to continue...')
        utils.clear_screen()

    print('Temporary deck:')
    for card in tmp_deck.cards:
        print(card)

    print('---')

    print('Final deck:')
    for card in final_deck.cards:
        print(card)


if __name__ == "__main__":
    main()