"""Entry point for the Flashcard Quizzer CLI.

Usage examples::

    python main.py
    python main.py -m adaptive -f data/python_basics.json --stats

All user interaction lives here: loading and quiz logic come from
``utils.file_handler`` and ``utils.quiz_engine``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Callable, List, Optional, TextIO

from utils.file_handler import FlashcardLoadError, load_flashcards
from utils.quiz_engine import (
    QuizMode,
    QuizStats,
    available_modes,
    create_quiz_mode,
    normalize_answer,
)

DEFAULT_DECK = Path(__file__).resolve().parent / "data" / "python_basics.json"
DEFAULT_MODE = "sequential"
EXIT_COMMAND = "exit"
MOST_MISSED_LIMIT = 3

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"

GOODBYE_MESSAGE = "Goodbye! It's a pity to abandon the game."

InputFunc = Callable[[str], str]


class QuitRequested(Exception):
    """Raised when the user asks to leave the quiz."""


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Quiz yourself with flashcards loaded from a JSON deck.",
        epilog=f'Type "{EXIT_COMMAND}" or press Ctrl+C at any time to quit.',
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=DEFAULT_DECK,
        help="path to a JSON deck (default: data/python_basics.json)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str.lower,
        choices=available_modes(),
        default=DEFAULT_MODE,
        help=f"order of the questions (default: {DEFAULT_MODE})",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="show a detailed summary at the end of the quiz",
    )
    return parser


def color_enabled(stream: TextIO) -> bool:
    """Return True if ``stream`` should get colors.

    Colors are off when the NO_COLOR environment variable is set to any
    non-empty value (https://no-color.org) or when ``stream`` is not a terminal.
    """
    if os.environ.get("NO_COLOR"):
        return False
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())


def colorize(text: str, color: str, enabled: bool) -> str:
    """Wrap ``text`` in an ANSI color code when ``enabled``."""
    return f"{color}{text}{RESET}" if enabled else text


def ask(prompt: str, input_func: InputFunc) -> str:
    """Read one answer; raise QuitRequested on "exit", Ctrl+C or Ctrl+D."""
    try:
        answer = input_func(prompt)
    except (KeyboardInterrupt, EOFError):
        raise QuitRequested from None
    if normalize_answer(answer) == EXIT_COMMAND:
        raise QuitRequested
    return answer


def format_score(stats: QuizStats) -> str:
    """One-line score shown at the end of every finished quiz."""
    return f"Score: {stats.correct}/{stats.total} correct ({stats.accuracy:.1f}%)"


def format_summary(stats: QuizStats) -> str:
    """Detailed end-of-quiz summary shown with --stats."""
    lines = [
        "--- Quiz statistics ---",
        f"Answers given: {stats.total}",
        f"Correct:       {stats.correct}",
        f"Incorrect:     {stats.incorrect}",
        f"Accuracy:      {stats.accuracy:.1f}%",
    ]
    most_missed = stats.mistakes.most_common(MOST_MISSED_LIMIT)
    if most_missed:
        lines.append("Most missed:")
        lines.extend(
            f"  {front} ({count} {'time' if count == 1 else 'times'})"
            for front, count in most_missed
        )
    else:
        lines.append("Most missed:   none, perfect round!")
    return "\n".join(lines)


def run_quiz(
    mode: QuizMode,
    *,
    show_stats: bool = False,
    input_func: InputFunc = input,
    out: TextIO = sys.stdout,
    use_color: bool = False,
) -> bool:
    """Play a quiz session until the deck is done or the user quits.

    Returns:
        True if the quiz was completed, False if the user quit.
    """
    number = 0
    try:
        while (card := mode.next_card()) is not None:
            number += 1
            print(f"\nQuestion {number}: {card.front}", file=out)
            answer = ask("> ", input_func)
            if mode.submit_answer(answer):
                print(colorize("✓ Correct!", GREEN, use_color), file=out)
            else:
                message = f"✗ Incorrect. The answer is: {card.back}"
                print(colorize(message, RED, use_color), file=out)
    except QuitRequested:
        print(f"\n{GOODBYE_MESSAGE}", file=out)
        return False

    print(f"\n{format_score(mode.stats)}", file=out)
    if show_stats:
        print(format_summary(mode.stats), file=out)
    return True


def main(
    argv: Optional[List[str]] = None,
    *,
    input_func: InputFunc = input,
    out: TextIO = sys.stdout,
    err: TextIO = sys.stderr,
) -> int:
    """Run the CLI and return the process exit code."""
    args = build_parser().parse_args(argv)

    try:
        cards = load_flashcards(args.file)
        mode = create_quiz_mode(args.mode, cards)
        print(
            f"Flashcard Quizzer: {len(cards)} cards, {mode.name} mode. "
            f'Type "{EXIT_COMMAND}" or press Ctrl+C to quit.',
            file=out,
        )
        run_quiz(
            mode,
            show_stats=args.stats,
            input_func=input_func,
            out=out,
            use_color=color_enabled(out),
        )
    except FlashcardLoadError as exc:
        print(f"Error: {exc}", file=err)
        return 1
    except KeyboardInterrupt:
        # Ctrl+C outside a prompt, e.g. while a large deck is loading.
        print(f"\n{GOODBYE_MESSAGE}", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
