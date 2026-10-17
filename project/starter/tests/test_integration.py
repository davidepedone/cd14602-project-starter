"""End-to-end tests for the CLI in main.py."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable, Iterable, List

import pytest

import main
from utils.file_handler import Flashcard
from utils.quiz_engine import QuizStats, SequentialMode

PROJECT_DIR = Path(__file__).resolve().parent.parent
THREE_CARDS = [
    {"front": "Which keyword defines a function?", "back": "def"},
    {"front": "What is the boolean type called?", "back": "bool"},
    {"front": "Which keyword starts a loop?", "back": "for"},
]


class FakeTerminal(io.StringIO):
    """A text stream that claims to be a terminal, to exercise colors."""

    def isatty(self) -> bool:
        return True


def scripted(answers: Iterable[str]) -> Callable[[str], str]:
    """Return an input function that replays ``answers``, then hits Ctrl+D."""
    remaining = iter(answers)

    def fake_input(prompt: str) -> str:
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError from None

    return fake_input


def interrupt_after(answers: List[str]) -> Callable[[str], str]:
    """Return an input function that replays ``answers``, then presses Ctrl+C."""
    remaining = iter(answers)

    def fake_input(prompt: str) -> str:
        try:
            return next(remaining)
        except StopIteration:
            raise KeyboardInterrupt from None

    return fake_input


@pytest.fixture
def deck(tmp_path: Path) -> Path:
    path = tmp_path / "three.json"
    path.write_text(json.dumps(THREE_CARDS), encoding="utf-8")
    return path


def run_main(args: List[str], answers: Iterable[str]) -> tuple:
    """Run main() with scripted input; return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    code = main.main(args, input_func=scripted(answers), out=out, err=err)
    return code, out.getvalue(), err.getvalue()


# Required scenario from the project specification


def test_full_session(deck: Path) -> None:
    code, output, _ = run_main(
        ["-f", str(deck), "-m", "sequential", "--stats"],
        ["def", "int", "FOR"],
    )

    assert code == 0
    assert output.count("✓ Correct!") == 2
    assert "✗ Incorrect. The answer is: bool" in output
    assert "Score: 2/3 correct (66.7%)" in output
    assert "Answers given: 3" in output
    assert "Correct:       2" in output
    assert "Incorrect:     1" in output
    assert "Accuracy:      66.7%" in output
    assert "What is the boolean type called? (1 time)" in output


# Full games through main()


def test_adaptive_game_on_default_deck_runs_to_the_end() -> None:
    cards = main.load_flashcards(main.DEFAULT_DECK)
    answers = [card.back for card in cards]

    code, output, _ = run_main(["-m", "adaptive"], answers)

    assert code == 0
    assert f"{len(cards)} cards, adaptive mode" in output
    assert f"Score: {len(cards)}/{len(cards)} correct (100.0%)" in output


def test_adaptive_game_repeats_missed_card(deck: Path) -> None:
    code, output, _ = run_main(
        ["-f", str(deck), "-m", "adaptive"],
        ["wrong", "bool", "for", "def"],
    )

    assert code == 0
    assert output.count("Which keyword defines a function?") == 2
    assert "Score: 3/4 correct (75.0%)" in output


def test_stats_flag_controls_the_summary(deck: Path) -> None:
    _, without_stats, _ = run_main(["-f", str(deck)], ["def", "bool", "for"])
    _, with_stats, _ = run_main(["-f", str(deck), "--stats"], ["def", "bool", "for"])

    assert "Score: 3/3" in without_stats
    assert "Quiz statistics" not in without_stats
    assert "Most missed:   none, perfect round!" in with_stats


def test_mode_flag_is_case_insensitive(deck: Path) -> None:
    _, output, _ = run_main(["-f", str(deck), "-m", "ADAPTIVE"], ["def"] * 3)

    assert "adaptive mode" in output


# Quitting


@pytest.mark.parametrize("command", ["exit", "EXIT", "  Exit  "])
def test_exit_command_quits_with_goodbye(deck: Path, command: str) -> None:
    code, output, err = run_main(["-f", str(deck), "--stats"], ["def", command])

    assert code == 0
    assert output.rstrip().endswith(main.GOODBYE_MESSAGE)
    assert "Score" not in output
    assert "Quiz statistics" not in output
    assert err == ""


def test_ctrl_c_quits_with_goodbye(deck: Path) -> None:
    out = io.StringIO()

    code = main.main(["-f", str(deck)], input_func=interrupt_after(["def"]), out=out)

    assert code == 0
    assert out.getvalue().rstrip().endswith(main.GOODBYE_MESSAGE)


def test_ctrl_d_quits_with_goodbye(deck: Path) -> None:
    code, output, _ = run_main(["-f", str(deck)], [])

    assert code == 0
    assert output.rstrip().endswith(main.GOODBYE_MESSAGE)


def test_ctrl_c_outside_a_prompt_quits_with_goodbye(
    deck: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def interrupted_load(path: Path) -> List[Flashcard]:
        raise KeyboardInterrupt

    monkeypatch.setattr(main, "load_flashcards", interrupted_load)
    out = io.StringIO()

    assert main.main(["-f", str(deck)], input_func=scripted([]), out=out) == 0
    assert main.GOODBYE_MESSAGE in out.getvalue()


def test_run_quiz_reports_whether_it_finished() -> None:
    cards = [Flashcard(front="Q", back="A")]

    finished = main.run_quiz(SequentialMode(cards), input_func=scripted(["A"]))
    quit_early = main.run_quiz(SequentialMode(cards), input_func=scripted(["exit"]))

    assert finished is True
    assert quit_early is False


# Errors


def test_bad_deck_prints_friendly_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")

    code, output, err = run_main(["-f", str(bad)], [])

    assert code == 1
    assert err.startswith("Error: ")
    assert "not valid JSON" in err
    assert "Traceback" not in err + output


def test_missing_deck_prints_friendly_error(tmp_path: Path) -> None:
    code, _, err = run_main(["-f", str(tmp_path / "missing.json")], [])

    assert code == 1
    assert "File not found" in err


def test_unknown_mode_is_rejected_by_argparse(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main.main(["-m", "fast"])

    assert excinfo.value.code == 2
    assert "invalid choice: 'fast'" in capsys.readouterr().err


def test_help_lists_flags_and_modes(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main.main(["--help"])

    help_text = capsys.readouterr().out
    assert excinfo.value.code == 0
    for text in ["--file", "--mode", "--stats", "sequential,random,adaptive"]:
        assert text in help_text


# Colors


def test_answers_are_colored_on_a_terminal(
    deck: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
    out = FakeTerminal()

    main.main(["-f", str(deck)], input_func=scripted(["def", "int", "for"]), out=out)

    output = out.getvalue()
    assert f"{main.GREEN}✓ Correct!{main.RESET}" in output
    assert f"{main.RED}✗ Incorrect. The answer is: bool{main.RESET}" in output


def test_no_colors_when_not_a_terminal(deck: Path) -> None:
    _, output, _ = run_main(["-f", str(deck)], ["def", "int", "for"])

    assert "\033[" not in output


def test_no_color_env_disables_colors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")

    assert main.color_enabled(FakeTerminal()) is False


def test_empty_no_color_env_keeps_colors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_COLOR", "")

    assert main.color_enabled(FakeTerminal()) is True


def test_colorize_is_a_no_op_when_disabled() -> None:
    assert main.colorize("text", main.GREEN, enabled=False) == "text"


# Output formatting


def test_summary_pluralises_and_limits_most_missed() -> None:
    stats = QuizStats()
    for front, count in [("Q0", 3), ("Q1", 1), ("Q2", 2), ("Q3", 1)]:
        for _ in range(count):
            stats.record(Flashcard(front=front, back="x"), correct=False)

    summary = main.format_summary(stats)

    assert "Q0 (3 times)" in summary
    assert "Q2 (2 times)" in summary
    assert summary.count(" time)") == 1
    assert len([line for line in summary.splitlines() if line.startswith("  ")]) == 3


# Real process


def test_script_runs_without_traceback() -> None:
    result = subprocess.run(
        [sys.executable, "main.py", "-m", "adaptive"],
        cwd=PROJECT_DIR,
        input="exit\n",
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0
    assert main.GOODBYE_MESSAGE in result.stdout
    assert "Traceback" not in result.stderr
