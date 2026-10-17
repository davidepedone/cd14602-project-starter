"""Tests for the quiz engine in utils.quiz_engine."""

from __future__ import annotations

import random
from typing import Dict, List, Type

import pytest

from utils.file_handler import Flashcard
from utils.quiz_engine import (
    QUIZ_MODES,
    AdaptiveMode,
    QuizMode,
    QuizStats,
    RandomMode,
    SequentialMode,
    UnknownQuizModeError,
    available_modes,
    create_quiz_mode,
    is_correct,
    normalize_answer,
)

CARDS = [Flashcard(front=f"Q{i}", back=f"A{i}") for i in range(1, 6)]


MAX_STEPS = 100


def play_script(mode: QuizMode, script: Dict[str, List[str]]) -> List[str]:
    """Run a whole session and return the fronts in the order they were asked.

    ``script`` maps a card's front to the answers to give, in order, each time
    that card comes up; once a card's list runs out it is answered correctly.
    Fails instead of hanging if the session never ends.
    """
    pending = {front: list(answers) for front, answers in script.items()}
    asked: List[str] = []
    while (card := mode.next_card()) is not None:
        assert len(asked) < MAX_STEPS, f"session did not end: {asked[:20]}..."
        asked.append(card.front)
        answers = pending.get(card.front)
        mode.submit_answer(answers.pop(0) if answers else card.back)
    return asked


def play(mode: QuizMode, wrong_once: frozenset = frozenset()) -> List[str]:
    """Run a session where cards in ``wrong_once`` are missed the first time."""
    return play_script(mode, {front: ["wrong"] for front in wrong_once})


# Required scenarios from the project specification


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("sequential", SequentialMode),
        ("random", RandomMode),
        ("adaptive", AdaptiveMode),
        ("Adaptive", AdaptiveMode),
        (" RANDOM ", RandomMode),
    ],
)
def test_quiz_mode_factory(name: str, expected: Type[QuizMode]) -> None:
    deck = [Flashcard(front=f"Q{i}", back=f"A{i}") for i in range(1, 11)]

    mode = create_quiz_mode(name, deck, rng=random.Random(42))
    again = create_quiz_mode(name, deck, rng=random.Random(42))

    # The exact class, not just any QuizMode (a subclass would also pass
    # isinstance), and a fresh session on every call.
    assert type(mode) is expected
    assert isinstance(mode, QuizMode)
    assert mode is not again

    # Built with the deck and rng it was given: it plays exactly like the
    # class constructed directly with the same arguments.
    direct = expected(deck, rng=random.Random(42))
    assert play(mode) == play(direct)
    assert play(again) == play(expected(deck, rng=random.Random(42)))


def test_adaptive_mode_behavior() -> None:
    mode = AdaptiveMode(CARDS)  # default retry gap: 2 other cards

    asked = play_script(
        mode,
        {
            "Q2": ["wrong", "still wrong"],  # missed twice, from the middle
            "Q3": ["  a3 "],  # right answer with odd case and spacing
            "Q5": ["wrong", "wrong"],  # the last card, missed twice
        },
    )

    assert asked == [
        "Q1",
        "Q2",  # missed -> comes back after Q3 and Q4
        "Q3",  # correct despite the spacing, so it is not repeated
        "Q4",
        "Q2",  # missed again -> fewer than 2 cards left, goes after Q5
        "Q5",  # missed -> goes after Q2
        "Q2",  # correct at last
        "Q5",  # missed again while it is the only card left -> asked again
        "Q5",  # correct
    ]
    # Each missed card is asked once more per miss, and only missed cards repeat.
    assert {front: asked.count(front) - 1 for front in set(asked)} == {
        "Q1": 0,
        "Q2": 2,
        "Q3": 0,
        "Q4": 0,
        "Q5": 2,
    }
    assert mode.stats.mistakes == {"Q2": 2, "Q5": 2}
    assert (mode.stats.correct, mode.stats.incorrect) == (5, 4)
    assert mode.is_finished
    assert mode.next_card() is None


# Factory


@pytest.mark.parametrize("name", ["ADAPTIVE", " Random ", "Sequential"])
def test_factory_ignores_case_and_spaces(name: str) -> None:
    assert create_quiz_mode(name, CARDS).name == name.strip().lower()


def test_factory_rejects_unknown_mode() -> None:
    with pytest.raises(UnknownQuizModeError, match='"fast".*sequential, random'):
        create_quiz_mode("fast", CARDS)


def test_factory_passes_rng_to_random_mode() -> None:
    first = play(create_quiz_mode("random", CARDS, rng=random.Random(7)))
    second = play(create_quiz_mode("random", CARDS, rng=random.Random(7)))

    assert first == second


def test_available_modes_matches_registry() -> None:
    assert available_modes() == ["sequential", "random", "adaptive"]
    assert all(QUIZ_MODES[name].name == name for name in available_modes())


def test_quiz_mode_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        QuizMode(CARDS)  # type: ignore[abstract]


@pytest.mark.parametrize("name", ["sequential", "random", "adaptive"])
def test_modes_reject_empty_deck(name: str) -> None:
    with pytest.raises(ValueError, match="at least one card"):
        create_quiz_mode(name, [])


# Sequential and random modes


def test_sequential_mode_keeps_deck_order() -> None:
    assert play(SequentialMode(CARDS)) == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_sequential_mode_does_not_repeat_wrong_answers() -> None:
    mode = SequentialMode(CARDS)

    asked = play(mode, wrong_once=frozenset({"Q2"}))

    assert asked == ["Q1", "Q2", "Q3", "Q4", "Q5"]
    assert mode.stats.incorrect == 1


def test_random_mode_asks_every_card_once() -> None:
    asked = play(RandomMode(CARDS, rng=random.Random(1)))

    assert sorted(asked) == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_random_mode_shuffles() -> None:
    orders = {tuple(play(RandomMode(CARDS, rng=random.Random(s)))) for s in range(10)}

    assert len(orders) > 1


def test_random_mode_does_not_modify_the_deck() -> None:
    deck = list(CARDS)

    play(RandomMode(deck, rng=random.Random(3)))

    assert deck == CARDS


# Adaptive mode


def test_adaptive_mode_without_mistakes_is_one_pass() -> None:
    assert play(AdaptiveMode(CARDS)) == ["Q1", "Q2", "Q3", "Q4", "Q5"]


def test_adaptive_mode_repeats_until_correct() -> None:
    mode = AdaptiveMode(CARDS[:2])
    asked = []

    for answer in ["wrong", "A2", "wrong", "wrong", "A1"]:
        card = mode.next_card()
        assert card is not None
        asked.append(card.front)
        mode.submit_answer(answer)

    assert asked == ["Q1", "Q2", "Q1", "Q1", "Q1"]
    assert mode.next_card() is None
    assert mode.stats.mistakes == {"Q1": 3}


def test_adaptive_missed_card_goes_last_when_few_cards_remain() -> None:
    asked = play(AdaptiveMode(CARDS), wrong_once=frozenset({"Q4"}))

    assert asked == ["Q1", "Q2", "Q3", "Q4", "Q5", "Q4"]


@pytest.mark.parametrize(
    ("gap", "expected"),
    [
        (0, ["Q1", "Q1", "Q2", "Q3", "Q4", "Q5"]),
        (1, ["Q1", "Q2", "Q1", "Q3", "Q4", "Q5"]),
        (10, ["Q1", "Q2", "Q3", "Q4", "Q5", "Q1"]),
    ],
)
def test_adaptive_retry_gap(gap: int, expected: List[str]) -> None:
    asked = play(AdaptiveMode(CARDS, retry_gap=gap), wrong_once=frozenset({"Q1"}))

    assert asked == expected


def test_adaptive_rejects_negative_gap() -> None:
    with pytest.raises(ValueError, match="negative"):
        AdaptiveMode(CARDS, retry_gap=-1)


# Session protocol


def test_next_card_requires_an_answer_first() -> None:
    mode = SequentialMode(CARDS)
    mode.next_card()

    with pytest.raises(RuntimeError, match="Answer the current card"):
        mode.next_card()


def test_submit_answer_requires_a_card() -> None:
    with pytest.raises(RuntimeError, match="no card waiting"):
        SequentialMode(CARDS).submit_answer("A1")


def test_current_card_tracks_the_question() -> None:
    mode = SequentialMode(CARDS)
    assert mode.current_card is None

    card = mode.next_card()
    assert mode.current_card == card

    mode.submit_answer("A1")
    assert mode.current_card is None


def test_finished_session_keeps_returning_none() -> None:
    mode = SequentialMode(CARDS[:1])
    play(mode)

    assert mode.next_card() is None
    assert mode.next_card() is None


# Answer checking and stats


@pytest.mark.parametrize("answer", ["def", "DEF", "  Def  ", "\tdef\n"])
def test_answers_ignore_case_and_spaces(answer: str) -> None:
    assert is_correct(Flashcard(front="Keyword?", back="def"), answer)


@pytest.mark.parametrize("answer", ["", "   ", "de f", "define"])
def test_wrong_answers_are_rejected(answer: str) -> None:
    assert not is_correct(Flashcard(front="Keyword?", back="def"), answer)


def test_normalize_collapses_inner_whitespace() -> None:
    assert normalize_answer("  Secure   Shell ") == "secure shell"


def test_submit_answer_returns_result_and_updates_stats() -> None:
    mode = SequentialMode(CARDS)

    mode.next_card()
    assert mode.submit_answer("a1") is True
    mode.next_card()
    assert mode.submit_answer("nope") is False

    assert (mode.stats.correct, mode.stats.incorrect, mode.stats.total) == (1, 1, 2)
    assert mode.stats.accuracy == 50.0
    assert mode.stats.mistakes == {"Q2": 1}


def test_stats_accuracy_before_any_answer() -> None:
    assert QuizStats().accuracy == 0.0
