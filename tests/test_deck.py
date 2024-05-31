from unittest.mock import patch

import pytest

from flashcards.deck import Card, Deck
from custom_exceptions import NoCardError

VALID_CARD_DATA = {
    'front': 'What is Python?',
    'back': 'Python is a programming language'
}

CARDS = [Card(front='Front 1', back='Back 1'), Card(front='Front 2', back='Back 2')]


def test_card_creation():
    card = Card(**VALID_CARD_DATA)
    assert card.front == 'What is Python?'
    assert card.back == 'Python is a programming language'
    assert len(card.card_id) > 0


def test_card_str():
    card = Card(**VALID_CARD_DATA)
    assert 'Card ID' in str(card)
    assert 'What is Python?' in str(card)
    assert 'Python is a programming language' in str(card)


def test_deck_initialization():
    deck = Deck()
    assert len(deck.cards) == 0


@patch('flashcards.deck.logger')
def test_load_cards(mock_logger):
    deck = Deck()
    deck.load_cards(CARDS)
    assert len(deck.cards) == 2
    assert deck.cards == CARDS
    mock_logger.info.assert_called_with(f'{len(CARDS)} valid cards loaded into deck.')


@patch('flashcards.deck.logger')
def test_load_cards_empty_list(mock_logger):
    deck = Deck()
    deck.load_cards([])
    assert len(deck.cards) == 0
    mock_logger.info.assert_called_with('0 valid cards loaded into deck.')


# @patch('flashcards.deck.logger')
# def test_add_card(mock_logger):
#     deck = Deck()
#     card = Card(**VALID_CARD_DATA)
#     deck.add_card(card)
#     assert len(deck.cards) == 1
#     assert deck.cards[0] == card
#     mock_logger.info.assert_called_with(f'Card (id: {card.card_id}) added to deck.')


@patch('flashcards.deck.logger')
def test_remove_card(mock_logger):
    deck = Deck()
    deck.load_cards(CARDS)
    deck.remove_card(CARDS[0])
    assert len(deck.cards) == 1
    mock_logger.info.assert_called_with(f'Card (id: {CARDS[0].card_id}) removed from deck.')


@patch('flashcards.deck.logger')
def test_remove_card_not_found(mock_logger):
    deck = Deck()
    card = Card(**VALID_CARD_DATA)
    with pytest.raises(NoCardError):
        deck.remove_card(card)
    mock_logger.error.assert_called_with(f'Failed to remove card from deck, card (id: {card.card_id}) not found.')


# @patch('flashcards.deck.logger')
# def test_replace_card(mock_logger):
#     deck = Deck()
#     card1 = Card(**VALID_CARD_DATA)
#     card2 = Card(front='New front', back='New back')
#     deck.add_card(card1)
#     deck.replace_card(card1, card2)
#     assert len(deck.cards) == 1
#     assert deck.cards[0] == card2
#     mock_logger.info.assert_called_with(f'Card (id: {card1.card_id}) has been replaced with new card '
#                                         f'(id: {card2.card_id}) in deck.')
#
#
# @patch('flashcards.deck.logger')
# def test_replace_card_not_found(mock_logger):
#     deck = Deck()
#     card1 = Card(**VALID_CARD_DATA)
#     card2 = Card(front='New front', back='New back')
#     with pytest.raises(NoCardError):
#         deck.replace_card(card1, card2)
#     mock_logger.error.assert_called_with(f'Could not replace card, card (id: {card1.card_id}) not found in deck.')
