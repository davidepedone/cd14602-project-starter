"""Load and validate flashcard decks from JSON files.

Two deck formats are supported:

* Array format: ``[{"front": "...", "back": "..."}, ...]``
* Object format: ``{"cards": [{"front": "...", "back": "..."}, ...]}``

Every problem with a deck (missing file, malformed JSON, wrong shape, missing
or empty fields) is raised as :class:`FlashcardLoadError` with a message meant
for the end user, so the CLI can print it instead of a traceback.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union

REQUIRED_FIELDS = ("front", "back")


class FlashcardLoadError(Exception):
    """Raised when a deck cannot be loaded or fails validation."""


@dataclass(frozen=True)
class Flashcard:
    """A single question/answer pair."""

    front: str
    back: str


def load_flashcards(path: Union[str, Path]) -> List[Flashcard]:
    """Read a deck from ``path`` and return its validated flashcards.

    Args:
        path: Location of a JSON deck in array or object format.

    Returns:
        The flashcards in the order they appear in the file.

    Raises:
        FlashcardLoadError: If the file cannot be read, is not valid JSON,
            or does not contain a valid deck.
    """
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FlashcardLoadError(f"File not found: {file_path}") from None
    except IsADirectoryError:
        raise FlashcardLoadError(
            f"Expected a JSON file but got a directory: {file_path}"
        ) from None
    except PermissionError:
        raise FlashcardLoadError(f"Permission denied: {file_path}") from None
    except UnicodeDecodeError:
        raise FlashcardLoadError(
            f"Could not read {file_path}: the file is not valid UTF-8 text."
        ) from None
    except OSError as exc:
        raise FlashcardLoadError(
            f"Could not read {file_path}: {exc.strerror or exc}"
        ) from None

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FlashcardLoadError(
            f"{file_path} is not valid JSON: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})."
        ) from None

    return parse_flashcards(data)


def parse_flashcards(data: Any) -> List[Flashcard]:
    """Validate already-decoded JSON data and convert it to flashcards.

    Args:
        data: The decoded JSON value: a list of cards, or a dict with a
            ``"cards"`` list.

    Returns:
        The validated flashcards.

    Raises:
        FlashcardLoadError: If the data is not a valid deck.
    """
    if isinstance(data, dict):
        if "cards" not in data:
            raise FlashcardLoadError(
                'Deck object is missing the "cards" key. Expected '
                '{"cards": [...]} or a plain list of cards.'
            )
        cards = data["cards"]
        if not isinstance(cards, list):
            raise FlashcardLoadError('The "cards" value must be a list of cards.')
    elif isinstance(data, list):
        cards = data
    else:
        raise FlashcardLoadError(
            'A deck must be a list of cards or an object with a "cards" list.'
        )

    if not cards:
        raise FlashcardLoadError("The deck contains no cards.")

    flashcards = [
        _parse_card(card, number) for number, card in enumerate(cards, start=1)
    ]
    _reject_duplicates(flashcards)
    return flashcards


def _parse_card(card: Any, number: int) -> Flashcard:
    """Validate one card; ``number`` is 1-based and used in error messages."""
    if not isinstance(card, dict):
        raise FlashcardLoadError(
            f'Card {number} must be an object with "front" and "back" fields.'
        )

    values = {}
    for field in REQUIRED_FIELDS:
        if field not in card:
            raise FlashcardLoadError(f'Card {number} is missing the "{field}" field.')
        value = card[field]
        if not isinstance(value, str) or not value.strip():
            raise FlashcardLoadError(
                f'Card {number} has an empty or non-text "{field}" field.'
            )
        values[field] = value.strip()

    return Flashcard(front=values["front"], back=values["back"])


def _reject_duplicates(flashcards: List[Flashcard]) -> None:
    """Raise if two cards share a front or a back, ignoring letter case."""
    for field, noun in (("front", "question"), ("back", "answer")):
        first_seen: Dict[str, int] = {}
        for number, card in enumerate(flashcards, start=1):
            value = getattr(card, field)
            key = value.casefold()
            if key in first_seen:
                raise FlashcardLoadError(
                    f'Card {number} repeats the "{field}" of card '
                    f'{first_seen[key]}: "{value}". Each {noun} must be unique.'
                )
            first_seen[key] = number
