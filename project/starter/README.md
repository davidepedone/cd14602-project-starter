# Flashcard Quizzer

A small command-line app to study with flashcards. It loads a deck from a JSON file and asks you the questions one by one, in order, shuffled, or in adaptive mode, where the cards you get wrong keep coming back until you get them right.

## Features

- Three quiz modes:
  - `sequential`: the cards in the order they appear in the file
  - `random`: the cards shuffled
  - `adaptive`: a card you miss comes back after two other cards, and the quiz ends only when every card has been answered correctly
- Two deck formats are supported (see [Deck format](#deck-format))
- Answers are checked ignoring upper/lower case and extra spaces, so `DEF`, `def` and ` def ` are all accepted
- Green for a correct answer, red for a wrong one, with the right answer shown
- Score at the end of every quiz, plus a detailed summary with `--stats` (accuracy and most missed cards)
- Type `exit`, or press Ctrl+C or Ctrl+D, to quit at any time
- Bad decks give a short error message instead of a Python traceback, for example `Error: Card 2 is missing the "back" field.`

## Setup

Requires Python 3.9 or newer.

On your own computer, create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
```

In the course workspace (`/voc/work/project/starter`) skip the venv and just run `python -m pip install -r requirements.txt`.

> If you get `No module named pytest` (or flake8, mypy...), the venv is probably not active in that terminal. Run `source venv/bin/activate` again; the prompt should start with `(venv)`.

The app itself only uses the standard library. `requirements.txt` is for the testing and code quality tools.

## Usage

```bash
python main.py                                        # python_basics deck, sequential mode
python main.py -m random -f data/glossary.json
python main.py -m adaptive -f data/python_basics.json --stats
python main.py --help
```

| Option | Description | Default |
|---|---|---|
| `-f`, `--file` | path to the JSON deck | `data/python_basics.json` |
| `-m`, `--mode` | `sequential`, `random` or `adaptive` (case doesn't matter) | `sequential` |
| `--stats` | show a detailed summary at the end | off |

Example session:

```
$ python main.py -m adaptive -f data/python_basics.json --stats
Flashcard Quizzer: 8 cards, adaptive mode. Type "exit" or press Ctrl+C to quit.

Question 1: Which keyword defines a function?
> function
✗ Incorrect. The answer is: def

Question 2: Which built-in function returns the length of a list?
> len
✓ Correct!

...

Score: 8/9 correct (88.9%)
--- Quiz statistics ---
Answers given: 9
Correct:       8
Incorrect:     1
Accuracy:      88.9%
Most missed:
  Which keyword defines a function? (1 time)
```

If you quit before the end you just get `Goodbye! It's a pity to abandon the game.`

Colors are turned off automatically when the output is not a terminal (for example when redirected to a file) or when the `NO_COLOR` environment variable is set.

## Deck format

A deck is a JSON file in one of these two formats.

Array:

```json
[
  {"front": "API", "back": "Application Programming Interface"},
  {"front": "CPU", "back": "Central Processing Unit"}
]
```

Object with a `cards` list:

```json
{
  "cards": [
    {"front": "Which keyword defines a function?", "back": "def"}
  ]
}
```

Rules checked when the deck is loaded:

- every card needs a non-empty `front` (the question) and `back` (the answer)
- field names are lowercase only: `"Back"` is not accepted
- no two cards can have the same `front`, and no two cards can have the same `back` (case and surrounding spaces are ignored)
- the deck can't be empty
- other fields in a card (for example `"hint"`) are ignored

Two sample decks are included in `data/`: `glossary.json` (10 tech acronyms, array format) and `python_basics.json` (8 Python questions, object format).

## Project structure

```
main.py                  CLI: arguments, input/output, colors, quitting
utils/file_handler.py    loading and validation of decks
utils/quiz_engine.py     quiz modes (Strategy pattern) and the mode factory
tests/                   pytest suite
data/                    sample decks
docs/                    AI edit log, design patterns notes, report
```

The quiz modes use the **Strategy pattern**: `QuizMode` is an abstract base class with the shared logic (current card, answer checking, stats), and `SequentialMode`, `RandomMode` and `AdaptiveMode` only decide which card comes next and what to do after an answer. `create_quiz_mode()` is a **factory** that picks the right class from the `-m` value. The engine doesn't do any input or output, so it can be tested without the CLI.

## Tests and code quality

```bash
python -m pytest                                  # run all tests
python -m pytest tests/test_quiz_modes.py         # one file
python -m pytest --cov=. --cov-report=html        # coverage report in htmlcov/index.html
python -m black --check .
python -m flake8 .
python -m mypy .
```

The suite has 129 tests in three files:

- `tests/test_flashcard_loader.py`: both formats, invalid JSON, missing or empty fields, duplicates, unreadable files
- `tests/test_quiz_modes.py`: the factory, each mode, the adaptive repeat logic, answer checking and stats
- `tests/test_integration.py`: full sessions through `main()`, quitting, error messages, colors and `--help`

Coverage is 99%. The only line not counted is `sys.exit(main())` at the bottom of `main.py`, which runs in a separate process in one of the tests. Black, flake8 (config in `.flake8`, max line length 88 to match black) and mypy all pass with no errors.

To check that the key tests actually catch bugs, I also used mutation testing: I introduced small bugs into the code on purpose and checked that the tests failed. The details are in `docs/ai_edit_log.md`.

## License

[License](../../LICENSE.txt)
