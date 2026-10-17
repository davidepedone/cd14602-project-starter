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
ANSWERS: Dict[str, str] = {card.front: card.back for card in CARDS}


def play(mode: QuizMode, wrong_once: frozenset = frozenset()) -> List[str]:
    """Run a whole session and return the fronts in the order they were asked.

    Cards in ``wrong_once`` are answered wrong the first time they appear and
    correctly afterwards.
    """
    asked: List[str] = []
    missed: set = set()
    while (card := mode.next_card()) is not None:
        asked.append(card.front)
        if card.front in wrong_once and card.front not in missed:
            missed.add(card.front)
            mode.submit_answer("wrong")
        else:
            mode.submit_answer(ANSWERS[card.front])
    return asked


# Required scenarios from the project specification


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("sequential", SequentialMode),
        ("random", RandomMode),
        ("adaptive", AdaptiveMode),
    ],
)
def test_quiz_mode_factory(name: str, expected: Type[QuizMode]) -> None:
    mode = create_quiz_mode(name, CARDS)

    assert type(mode) is expected
    assert isinstance(mode, QuizMode)


def test_adaptive_mode_behavior() -> None:
    mode = AdaptiveMode(CARDS)

    asked = play(mode, wrong_once=frozenset({"Q1"}))

    # Q1 is missed, then returns after two other cards instead of at the end.
    assert asked == ["Q1", "Q2", "Q3", "Q1", "Q4", "Q5"]
    assert mode.stats.mistakes == {"Q1": 1}
    assert mode.is_finished


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
