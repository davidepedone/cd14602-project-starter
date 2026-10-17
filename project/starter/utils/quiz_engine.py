"""Quiz engine: the order in which flashcards are asked.

Design:

* Strategy pattern - :class:`QuizMode` is the abstract strategy. It owns the
  shared session logic (tracking the current card, checking answers, keeping
  :class:`QuizStats`) and leaves two decisions to its subclasses: which card
  comes next (:meth:`QuizMode._select_next`) and how to react to an answer
  (:meth:`QuizMode._after_answer`). :class:`SequentialMode`,
  :class:`RandomMode` and :class:`AdaptiveMode` are the concrete strategies.
* Factory pattern - :func:`create_quiz_mode` turns a mode name from the
  command line into the matching strategy, using the :data:`QUIZ_MODES`
  registry.

The engine does no input or output, so the CLI decides how to talk to the
user and the logic can be tested on its own.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import ClassVar, Deque, Dict, List, Optional, Sequence, Type

from utils.file_handler import Flashcard


class UnknownQuizModeError(ValueError):
    """Raised when the factory is asked for a mode that does not exist."""


def normalize_answer(text: str) -> str:
    """Return ``text`` with case and extra whitespace removed, for comparison."""
    return " ".join(text.split()).casefold()


def is_correct(card: Flashcard, answer: str) -> bool:
    """Return True if ``answer`` matches the card's back, ignoring case and spaces."""
    return normalize_answer(answer) == normalize_answer(card.back)


@dataclass
class QuizStats:
    """Running totals for one quiz session."""

    correct: int = 0
    incorrect: int = 0
    mistakes: Counter[str] = field(default_factory=Counter)

    @property
    def total(self) -> int:
        """Number of answers given so far."""
        return self.correct + self.incorrect

    @property
    def accuracy(self) -> float:
        """Share of correct answers as a percentage; 0.0 before any answer."""
        if self.total == 0:
            return 0.0
        return 100.0 * self.correct / self.total

    def record(self, card: Flashcard, correct: bool) -> None:
        """Count one answer to ``card``."""
        if correct:
            self.correct += 1
        else:
            self.incorrect += 1
            self.mistakes[card.front] += 1


class QuizMode(ABC):
    """Abstract strategy for serving flashcards during a quiz session.

    Usage::

        mode = create_quiz_mode("adaptive", cards)
        while (card := mode.next_card()) is not None:
            mode.submit_answer(input(card.front))

    Args:
        cards: The deck to quiz on. It must contain at least one card.
        rng: Source of randomness, for modes that need one. Pass a seeded
            ``random.Random`` to get repeatable sessions in tests.

    Raises:
        ValueError: If ``cards`` is empty.
    """

    name: ClassVar[str]

    def __init__(
        self, cards: Sequence[Flashcard], rng: Optional[random.Random] = None
    ) -> None:
        if not cards:
            raise ValueError("A quiz needs at least one card.")
        self._cards: List[Flashcard] = list(cards)
        self._rng = rng if rng is not None else random.Random()
        self._current: Optional[Flashcard] = None
        self.stats = QuizStats()

    @property
    def current_card(self) -> Optional[Flashcard]:
        """The card waiting for an answer, or None."""
        return self._current

    @property
    @abstractmethod
    def is_finished(self) -> bool:
        """True when the session has no more cards to ask."""

    def next_card(self) -> Optional[Flashcard]:
        """Return the next card to ask, or None when the session is over.

        Raises:
            RuntimeError: If the previous card has not been answered yet.
        """
        if self._current is not None:
            raise RuntimeError("Answer the current card before asking for the next.")
        if self.is_finished:
            return None
        self._current = self._select_next()
        return self._current

    def submit_answer(self, answer: str) -> bool:
        """Check ``answer`` against the current card and record the result.

        Returns:
            True if the answer is correct.

        Raises:
            RuntimeError: If there is no card waiting for an answer.
        """
        card = self._current
        if card is None:
            raise RuntimeError("There is no card waiting for an answer.")
        correct = is_correct(card, answer)
        self.stats.record(card, correct)
        self._current = None
        self._after_answer(card, correct)
        return correct

    @abstractmethod
    def _select_next(self) -> Flashcard:
        """Remove and return the next card; only called when not finished."""

    def _after_answer(self, card: Flashcard, correct: bool) -> None:
        """React to an answer. The default does nothing."""


class _QueueMode(QuizMode):
    """Shared implementation for modes that serve cards from a queue."""

    def __init__(
        self, cards: Sequence[Flashcard], rng: Optional[random.Random] = None
    ) -> None:
        super().__init__(cards, rng)
        self._queue: Deque[Flashcard] = deque(self._initial_order())

    def _initial_order(self) -> List[Flashcard]:
        """The order of the first pass; defaults to the deck order."""
        return list(self._cards)

    @property
    def is_finished(self) -> bool:
        return not self._queue

    def _select_next(self) -> Flashcard:
        return self._queue.popleft()


class SequentialMode(_QueueMode):
    """Ask every card once, in deck order."""

    name = "sequential"


class RandomMode(_QueueMode):
    """Ask every card once, in shuffled order."""

    name = "random"

    def _initial_order(self) -> List[Flashcard]:
        order = list(self._cards)
        self._rng.shuffle(order)
        return order


class AdaptiveMode(_QueueMode):
    """Repeat cards answered wrong until every card has been answered correctly.

    Cards start in deck order. A card answered wrong goes back into the queue
    ahead of the cards not asked yet, after ``retry_gap`` other cards, so it
    comes back soon without being repeated straight away. A card leaves the
    queue only when it is answered correctly.

    Args:
        cards: The deck to quiz on.
        rng: Accepted for a uniform constructor; not used.
        retry_gap: How many other cards to ask before a missed card returns.
            When fewer cards remain, the missed card goes to the end.
    """

    name = "adaptive"
    DEFAULT_RETRY_GAP: ClassVar[int] = 2

    def __init__(
        self,
        cards: Sequence[Flashcard],
        rng: Optional[random.Random] = None,
        retry_gap: int = DEFAULT_RETRY_GAP,
    ) -> None:
        if retry_gap < 0:
            raise ValueError("retry_gap cannot be negative.")
        super().__init__(cards, rng)
        self._retry_gap = retry_gap

    def _after_answer(self, card: Flashcard, correct: bool) -> None:
        if not correct:
            self._queue.insert(min(self._retry_gap, len(self._queue)), card)


QUIZ_MODES: Dict[str, Type[QuizMode]] = {
    mode.name: mode for mode in (SequentialMode, RandomMode, AdaptiveMode)
}


def available_modes() -> List[str]:
    """Return the valid mode names, for help text and error messages."""
    return list(QUIZ_MODES)


def create_quiz_mode(
    name: str, cards: Sequence[Flashcard], rng: Optional[random.Random] = None
) -> QuizMode:
    """Build the quiz mode called ``name`` (case-insensitive).

    Raises:
        UnknownQuizModeError: If ``name`` is not one of :func:`available_modes`.
        ValueError: If ``cards`` is empty.
    """
    mode_class = QUIZ_MODES.get(name.strip().lower())
    if mode_class is None:
        raise UnknownQuizModeError(
            f'Unknown quiz mode "{name}". Choose one of: '
            f"{', '.join(available_modes())}."
        )
    return mode_class(cards, rng=rng)
