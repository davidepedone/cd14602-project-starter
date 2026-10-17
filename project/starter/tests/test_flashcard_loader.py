"""Tests for the flashcard data layer in utils.file_handler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from utils.file_handler import (
    Flashcard,
    FlashcardLoadError,
    load_flashcards,
    parse_flashcards,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def write_json(tmp_path: Path, data: Any, name: str = "deck.json") -> Path:
    """Write ``data`` as JSON to a temporary file and return its path."""
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# Required scenarios from the project specification


def test_load_valid_flashcards_array(tmp_path: Path) -> None:
    path = write_json(
        tmp_path,
        [{"front": "API", "back": "Application Programming Interface"}],
    )

    assert load_flashcards(path) == [
        Flashcard(front="API", back="Application Programming Interface")
    ]


def test_load_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('[{"front": "API", "back": }]', encoding="utf-8")

    with pytest.raises(FlashcardLoadError, match="not valid JSON.*line 1"):
        load_flashcards(path)


def test_load_missing_required_field(tmp_path: Path) -> None:
    path = write_json(tmp_path, [{"front": "API"}])

    with pytest.raises(FlashcardLoadError, match='Card 1 is missing the "back"'):
        load_flashcards(path)


# Supported formats and sample decks


def test_load_valid_flashcards_object_format(tmp_path: Path) -> None:
    path = write_json(tmp_path, {"cards": [{"front": "Q", "back": "A"}]})

    assert load_flashcards(path) == [Flashcard(front="Q", back="A")]


def test_load_preserves_card_order(tmp_path: Path) -> None:
    cards = [{"front": str(i), "back": str(i * 2)} for i in range(5)]

    loaded = load_flashcards(write_json(tmp_path, cards))

    assert [card.front for card in loaded] == ["0", "1", "2", "3", "4"]


def test_load_strips_whitespace_and_ignores_extra_keys(tmp_path: Path) -> None:
    path = write_json(tmp_path, [{"front": "  Q ", "back": " A\n", "hint": "x"}])

    assert load_flashcards(path) == [Flashcard(front="Q", back="A")]


def test_load_accepts_string_path(tmp_path: Path) -> None:
    path = write_json(tmp_path, [{"front": "Q", "back": "A"}])

    assert load_flashcards(str(path)) == [Flashcard(front="Q", back="A")]


@pytest.mark.parametrize("name", ["glossary.json", "python_basics.json"])
def test_sample_decks_load(name: str) -> None:
    cards = load_flashcards(DATA_DIR / name)

    assert cards
    assert all(card.front and card.back for card in cards)


# File-level errors


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FlashcardLoadError, match="File not found"):
        load_flashcards(tmp_path / "nope.json")


def test_load_directory_instead_of_file(tmp_path: Path) -> None:
    with pytest.raises(FlashcardLoadError, match="directory"):
        load_flashcards(tmp_path)


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (PermissionError(13, "Permission denied"), "Permission denied"),
        (OSError(5, "Input/output error"), "Input/output error"),
    ],
)
def test_load_unreadable_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: OSError,
    message: str,
) -> None:
    path = write_json(tmp_path, [{"front": "Q", "back": "A"}])

    def fail(*args: Any, **kwargs: Any) -> str:
        raise error

    monkeypatch.setattr(Path, "read_text", fail)

    with pytest.raises(FlashcardLoadError, match=message):
        load_flashcards(path)


def test_load_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "latin1.json"
    path.write_bytes(b'[{"front": "caf\xe9", "back": "coffee"}]')

    with pytest.raises(FlashcardLoadError, match="not valid UTF-8"):
        load_flashcards(path)


def test_load_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")

    with pytest.raises(FlashcardLoadError, match="not valid JSON"):
        load_flashcards(path)


def test_errors_hide_the_original_traceback(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(FlashcardLoadError) as excinfo:
        load_flashcards(path)

    assert excinfo.value.__suppress_context__


# Deck-level and card-level validation


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ("just a string", "must be a list of cards"),
        (42, "must be a list of cards"),
        (None, "must be a list of cards"),
        ({"deck": []}, 'missing the "cards" key'),
        ({"cards": {"front": "Q"}}, '"cards" value must be a list'),
        ([], "no cards"),
        ({"cards": []}, "no cards"),
        (["not a card"], "Card 1 must be an object"),
        ([{"back": "A"}], 'Card 1 is missing the "front"'),
        (
            [{"front": "Q", "back": "A"}, {"front": "Q2"}],
            'Card 2 is missing the "back"',
        ),
        ([{"front": "", "back": "A"}], 'empty or non-text "front"'),
        ([{"front": "Q", "back": "   "}], 'empty or non-text "back"'),
        ([{"front": "Q", "back": 42}], 'empty or non-text "back"'),
        ([{"front": None, "back": "A"}], 'empty or non-text "front"'),
    ],
)
def test_parse_rejects_invalid_decks(data: Any, message: str) -> None:
    with pytest.raises(FlashcardLoadError, match=message):
        parse_flashcards(data)


@pytest.mark.parametrize("field", ["front", "back"])
@pytest.mark.parametrize(
    "values",
    [
        ["API", "API"],
        ["API", "api"],
        ["API", "  API  "],
        ["API", "CPU", "Api"],
    ],
)
def test_parse_rejects_duplicate_values(field: str, values: List[str]) -> None:
    other = "back" if field == "front" else "front"
    cards = [{field: value, other: f"unique {i}"} for i, value in enumerate(values)]

    with pytest.raises(
        FlashcardLoadError,
        match=f'Card {len(values)} repeats the "{field}" of card 1',
    ):
        parse_flashcards(cards)


@pytest.mark.parametrize(
    ("cards", "message"),
    [
        (
            [{"front": "Q", "back": "A"}, {"front": "Q", "back": "B"}],
            "Each question must be unique",
        ),
        (
            [{"front": "Q1", "back": "A"}, {"front": "Q2", "back": "A"}],
            "Each answer must be unique",
        ),
    ],
)
def test_load_rejects_duplicates_in_object_format(
    tmp_path: Path, cards: List[Dict[str, str]], message: str
) -> None:
    path = write_json(tmp_path, {"cards": cards})

    with pytest.raises(FlashcardLoadError, match=message):
        load_flashcards(path)


def test_parse_reports_duplicate_front_before_back() -> None:
    cards = [{"front": "Q", "back": "A"}, {"front": "Q", "back": "A"}]

    with pytest.raises(FlashcardLoadError, match='repeats the "front"'):
        parse_flashcards(cards)


def test_parse_allows_same_text_as_front_and_back() -> None:
    cards = [{"front": "echo", "back": "x"}, {"front": "y", "back": "echo"}]

    assert len(parse_flashcards(cards)) == 2


def test_flashcard_is_immutable() -> None:
    card = Flashcard(front="Q", back="A")

    with pytest.raises(AttributeError):
        card.front = "changed"  # type: ignore[misc]
