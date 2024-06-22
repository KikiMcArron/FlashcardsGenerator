import uuid
from dataclasses import dataclass, field
from typing import List

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

    def __init__(self) -> None:
        self.cards: List[Card] = []

    def load_cards(self, cards: List[Card]) -> None:
        """
        Load multiple cards into the deck.

        :param cards: List of Card objects to be loaded to the deck.
        """
        self.cards.extend(cards)
        logger.info(f"{len(cards)} valid cards loaded into deck.")

    def remove_card(self, card: Card) -> None:
        """
        Remove a single card from the deck.

        :param card: Card object to be removed from the deck.
        :raises NoCardError: If the card is not found in the deck.
        """
        try:
            self.cards.remove(card)
            logger.info(f'Card (id: {card.card_id}) removed from deck.')
        except ValueError:
            logger.error(f'Failed to remove card from deck, card (id: {card.card_id}) not found.')
            raise NoCardError('Card not found in deck.') from None
