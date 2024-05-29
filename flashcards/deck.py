import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from custom_exceptions import NoCardError
from logger import logger


@dataclass
class Card:
    """Class representing a flashcard."""
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    front: str
    back: str

    def __str__(self) -> str:
        return f"Card ID: {self.card_id}\nFront: {self.front}\nBack: {self.back}"


class Deck:
    """Class representing a deck of flashcards."""
    def __init__(self, name: Optional[str] = None) -> None:
        """
        Initialize a deck with an optional name.

        :param name: Optional name for the deck.
        """
        self.cards: List[Card] = []
        self.name = name

    def load_cards(self, cards: List[Card]) -> None:
        """
        Load multiple cards into the deck.

        :param cards: List of Card objects to be loaded to the deck.
        """
        self.cards.extend(cards)
        logger.info(f"{len(cards)} valid cards loaded into deck.")

    def add_card(self, card: Card) -> None:
        """
        Add a single card to the deck.

        :param card: Card object to be added to the deck.
        """
        self.cards.append(card)
        logger.info(f"Card (id: {card.card_id}) added to deck {self.name}.")

    def remove_card(self, card: Card) -> None:
        """
        Remove a single card from the deck.

        :param card: Card object to be removed from the deck.
        :raises NoCardError: If the card is not found in the deck.
        """
        try:
            self.cards.remove(card)
            logger.info(f'Card (id: {card.card_id}) removed from deck {self.name}.')
        except ValueError:
            logger.error(f'Failed to remove card from deck {self.name}, card (id: {card.card_id}) not found.')
            raise NoCardError('Card not found in deck.') from None

    def replace_card(self, card: Card, new_card: Card) -> None:
        """
        Replace an existing card in the deck with a new card.

        :param card: Card object to be replaced.
        :param new_card: New Card object to replace the existing card.
        :raises NoCardError: If the card to be replaced is not found in the deck.
        """
        try:
            index = self.cards.index(card)
            self.cards[index] = new_card
            logger.info(
                f'Card (id: {card.card_id}) has been replaced with new card (id: {new_card.card_id}) in deck {self.name}.')
        except ValueError:
            logger.error(f'Could not replace card, card (id: {card.card_id}) not found in deck {self.name}.')
            raise NoCardError('Card not found in deck.') from None
