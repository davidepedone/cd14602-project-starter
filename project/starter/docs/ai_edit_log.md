# AI Edit Log

**Instructions:** Use this document to track all your interactions with AI assistants during the project. This log will help you reflect on your AI collaboration process and demonstrate your learning journey.

## How to Use This Log

For each AI interaction, create a new entry with the following structure:

### Entry Template
```
## [Date] - [Brief Description]

**Context:** What were you trying to accomplish?
**AI Tool Used:** Claude/ChatGPT/Copilot/etc.
**Prompt/Request:** What exactly did you ask the AI?
**AI Response:** Summary of what the AI generated (don't copy entire code blocks)
**Changes Made:** What modifications did you make to the AI's suggestions?
**Reasoning:** Why did you make those changes?
**Outcome:** What was the final result?
**Lessons Learned:** What did you learn from this interaction?
```

---

## Your Log Entries

### 2026-10-16 - Phase 1: Flashcard Data Layer & Validation

**Context:** Phase 1 of the project: build the system that loads flashcard decks from JSON, supports both deck formats, and reports bad data with a friendly message instead of a Python traceback.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "The app must support JSON input in two formats: array [{"front":"..."},{"back":".."}] and wrapper object: {"cards":[...]}. Create a system to load and validate flashcard data. if json is malformed or missing fields the app must catch the error and print a friendly message. absolutely no raw python tracebacks"

**AI Response:**
- Pointed out that the array example in the prompt put `front` and `back` in two separate objects, while the spec and `data/glossary.json` keep both fields in the same object (`[{"front": "...", "back": "..."}]`). It implemented the spec version.
- Created `utils/file_handler.py` with a frozen `Flashcard` dataclass, a `FlashcardLoadError` exception, `load_flashcards(path)` (file reading and JSON decoding) and `parse_flashcards(data)` (shape and field validation).
- Each failure gets its own readable message: missing file, directory, permission or other OS error, non-UTF-8 file, malformed JSON (with line and column), wrong top-level type, missing `"cards"` key, empty deck, a card that isn't an object, a missing field, and an empty or non-text field. Messages give the 1-based card number.
- Errors are re-raised with `from None`, so the original exception chain is not shown.
- Created `tests/test_flashcard_loader.py` with the three required tests (`test_load_valid_flashcards_array`, `test_load_invalid_json`, `test_load_missing_required_field`) plus tests for the object format, both sample decks and every error branch.
- The first run of the checks found a test line too long for black/flake8. The AI ran black and added tests for the permission and OS error branches. Final result: 31 tests passing, 100% coverage of `utils/file_handler.py`, and black, flake8 and mypy all clean.

**Changes Made:**
- 2026-10-17, after review: the AI had noted that duplicate `front` values were allowed. I asked it not to allow duplicate values. The loader now rejects a deck in which two cards share the same `front`, ignoring letter case and surrounding whitespace, with a message such as `Card 3 repeats the "front" of card 1: "API". Each question must be unique.` At first the AI kept duplicate `back` values allowed, reasoning that different questions can share an answer. I asked for duplicates to be rejected on `back` as well, so both fields must now be unique (`Each answer must be unique.`). If a card repeats both fields, the error reports the `front`. The same text may still appear as one card's `front` and another card's `back`.

**Reasoning:** 
- The first version proposed by the AI pointed out a potential issue with duplicates, so I asked it to fix it. The fix was not complete, so I had to give it another prompt.

**Outcome:**
- Phase 1 looks OK to me.

**Lessons Learned:**
- I made a mistake in the prompt. The AI noticed it and luckily fixed it the right way, thanks to the supporting files. I need to be more careful when prompting.

---

### 2026-10-17 - Phase 2: Quiz Engine with Strategy and Factory Patterns

**Context:** Phase 2 of the project: build the quiz engine. It needs three ways of serving questions (sequential, random, adaptive), implemented with the Strategy pattern, plus a Factory that picks the mode from user input.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "We need to implement quiz engine using the Strategy Pattern. I want 3 different ways to ask question, sequential mode, randome mode and adaptive mode. Create a quiz mode abstract class and then use factory pattern to select the correct mode based on user input. ask me if you need  more details about how implementing the 3 modes"

Before the prompt, the AI listed the decisions the brief leaves open (session end, adaptive behaviour, answer matching, stats, unknown modes, randomness in tests, keeping input/output out of the engine). Because the prompt invited questions, it asked four multiple-choice questions before writing code. My answers:
- Adaptive behaviour: "prioritize cards the user gets wrong"
- Session end: every card once in sequential and random mode; adaptive mode runs until every card has been answered correctly
- Answer matching: ignore case and spaces
- Unknown mode name: raise a clear error

**AI Response:**
- Noted that my adaptive answer restated the brief rather than choosing a mechanism, and stated how it interpreted it: a card answered wrong goes back into the queue ahead of the cards not yet asked, after 2 other cards (`retry_gap`, configurable), and leaves the queue only when answered correctly. It asked me to say if I meant something else.
- Created `utils/quiz_engine.py`:
  - Strategy: an abstract `QuizMode` holds the shared session logic (current card, answer checking, `QuizStats` with correct/incorrect/accuracy and mistakes per card). Subclasses decide only which card comes next (`_select_next`) and how to react to an answer (`_after_answer`). `SequentialMode`, `RandomMode` and `AdaptiveMode` share a small queue-based helper class.
  - Factory: `create_quiz_mode(name, cards)` looks the name up in a `QUIZ_MODES` registry, ignoring case and spaces. An unknown name raises `UnknownQuizModeError`, which lists the valid modes.
  - The engine has no `input()` or `print()`, so the Phase 3 CLI owns all user interaction. `RandomMode` accepts a seeded `random.Random` so tests are repeatable.
- Created `tests/test_quiz_modes.py` with the required `test_quiz_mode_factory` and `test_adaptive_mode_behavior`, plus tests for every mode, the retry gap, answer matching, stats and misuse (for example, asking for the next card before answering). 84 tests pass in total, `quiz_engine.py` has 100% coverage, and black, flake8 and mypy are clean. After the first run, the AI tightened one type hint (`Counter` to `Counter[str]`).

**Changes Made:**
- None. I accepted the adaptive mode implementation proposed by the AI.

**Reasoning:**
- Nothing to mention.

**Outcome:**
- Phase 2 completed.

**Lessons Learned:**
- The prompt was slightly better than the first one, but it still needed more clarity.

---

### 2026-10-17 - Phase 3: Command-Line Interface

**Context:** Phase 3 of the project: build the user interface in `main.py`, on top of the Phase 1 loader and the Phase 2 quiz engine.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "let's move to phase 3 where we need to build the UI. here are the requirements: 1. use argparse to hangle flags like -f (file), -m (mode), and --stats. 2. Display text colors (Green for correct, Red for incorrect). 3. Allow the user to type "exit" or press Ctrl+C to quit gracefully without errors. if you have doubt ask and do not just assume"

Because the prompt said not to assume, the AI asked two rounds of questions before writing code. My answers:
- `--stats`: always show a one-line score at the end; `--stats` adds a detailed summary
- Defaults: both flags have defaults (`-f data/python_basics.json`, `-m sequential`)
- On quit: I wrote my own answer instead of the offered options: "goodbye and say that it's a pity to abandon game". In the follow-up round I confirmed: only the goodbye message, no stats
- Wrong answers: show the correct answer in red
- Colors: off when the output isn't a terminal or `NO_COLOR` is set
- Quitting: `exit` ignores case and spaces, and Ctrl+D also quits (I didn't select the `quit` alias)

**AI Response:**
- Noted the one case my answers didn't settle, a blank answer, and said it would count as wrong unless I preferred re-asking.
- Wrote `main.py` (CLI only; no quiz logic):
  - argparse with `-f/--file`, `-m/--mode` (choices taken from the engine's registry, case-insensitive) and `--stats`
  - a green `✓ Correct!` and a red `✗ Incorrect. The answer is: ...`
  - `exit`, Ctrl+C and Ctrl+D all print `Goodbye! It's a pity to abandon the game.` and exit with code 0. Ctrl+C is also handled outside a prompt, for example while a deck is loading
  - deck errors are printed as `Error: ...` on stderr with exit code 1 and no traceback
- Wrote `tests/test_integration.py` with the required `test_full_session` (3 answers, 2 correct and 1 wrong, checking the final stats), plus tests for a full adaptive game on the default deck, each way of quitting, error messages, `--help`, colors on and off, and one test that runs `main.py` as a real process.
- Mistake caught: one test passed `retry_gap` to the factory, which doesn't accept it. The AI noticed while reviewing its own code, before running the tests, and simplified the test.
- Results: 107 tests pass, total coverage (`--cov=.`) is 99%, and black, flake8 and mypy are clean. The AI also ran the real app: a full `-m adaptive -f data/python_basics.json` game (a missed card came back after two others), quitting with `exit`, a bad deck and an unknown mode. In its first manual run the AI guessed the deck's answers wrongly and input ran out mid-game. It said so and reran with the answers taken from the deck.

**Changes Made:**
- None. I tested it on my machine and it works as expected.

**Reasoning:**
- I was impressed that the AI made 2 mistakes but caught and fixed them itself.

**Outcome:**
- The AI couldn't verify the colors in the terminal, but Phase 3 is done.

**Lessons Learned:**
- "Ask, don't assume" made the conversation more interactive, so potential issues were addressed earlier.
- The AI has limits, like testing the colors. It goes without saying that I need to be extra careful when testing.

---

### 2026-10-17 - QA: Strengthening the Required Data Loader Tests

**Context:** Start of the QA phase. The three required loader tests already existed from Phase 1, so the goal was to check whether they really prove what their names claim.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "I've commited phase 3. now we need to move forward and focus on QA. let's start with data loader (test_flashcard_loader.py). here some important thing to cover: test_load_valid_flashcards_array: Does it load a list correctly?, test_load_invalid_json: Does it gracefully handle bad syntax?, test_load_missing_required_field: Does it reject cards without a "Back"?"

**AI Response:**
- Reviewed the existing tests and listed their gaps:
  - the array test used a single card, so it couldn't show that order is kept or every card is read
  - the invalid-JSON test covered only one kind of syntax error and didn't check that the error was free of the raw `JSONDecodeError` traceback
  - the missing-field test covered only card 1 of an array
- Rewrote the three tests in `tests/test_flashcard_loader.py`:
  - `test_load_valid_flashcards_array`: 3 cards, checking exact content, order and type. A companion test loads the real `data/glossary.json` and compares it with the raw file.
  - `test_load_invalid_json`: 7 kinds of bad syntax (missing value, trailing comma, unclosed bracket, single quotes, unquoted keys, missing comma, CSV instead of JSON). Each checks for our own error type, a one-line message with the file name, line and column, and no chained traceback. A companion test checks that the line and column are right in a file with several lines.
  - `test_load_missing_required_field`: `back` missing from the only card, from the last card of an array, and from the object format, and in a card where other keys (`answer`, `hint`) don't replace `back`. The message must name the right card.
- Mistake caught: the line/column test first failed because the AI miscounted the column (it expected 29; the right value is 28). The loader was correct, and the AI fixed the test.
- Mutation check: the AI broke `file_handler.py` in 7 ways, one at a time, and ran only the three required tests, then restored the file (verified identical to the commit).
  - new tests: all 7 mutations caught
  - old tests: 3 missed: keeping only the first card, reversing card order, and showing the chained traceback. Two of those were caught elsewhere in the suite, but not by the required tests.
- Results: 118 tests pass, total coverage is 99%, and black, flake8 and mypy are clean. `file_handler.py` was not changed.
- Open question raised by the AI: the brief says cards without a "Back" (capital B), but the loader only accepts lowercase keys. It asked whether `"Front"`/`"Back"` should also be accepted. After my answer (lowercase only), it added `test_load_field_names_are_lowercase_only`: a card with `"Back"`, `"BACK"` or `"Front"` is rejected with the usual "missing field" message, so the behaviour can't change by accident. 122 tests pass; the other checks are still clean.

**Changes Made:**
- I asked the AI to keep keys lowercase only.

**Reasoning:**
- I didn't specifically ask for mutation testing, but it was awesome that the AI did it.

**Outcome:**
- Data loader testing complete.

**Lessons Learned:** 
- Passing tests and 100% coverage didn't mean the required tests were strong. The mutation check showed what they would have missed.

---

### 2026-10-17 - QA: Mutation Testing the Quiz Logic Tests

**Context:** Second QA step: the two required quiz engine tests in `tests/test_quiz_modes.py`, using mutation testing to find the edge cases they miss.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "let's move to quiz logic testing, focusing in particular on: test_quiz_mode_factory: Does the factory return the correct class object? test_adaptive_mode_behavior: Does it actually repeat incorrect questions? use mutation to catch edge cases"

**AI Response:**
- Wrote a mutation runner (a scratch script, not part of the project) with 18 mutations of `utils/quiz_engine.py`: 6 in the factory, 12 in adaptive mode and answer checking. Each run had a 20-second timeout, because some mutations make a session never end. The original file was restored after every run and checked to be identical to the commit.
- Baseline, before changing any test: the two required tests caught only **10 of 18** mutations. They missed: the factory dropping the `rng`, passing only the first card, reusing one instance across calls, and becoming case-sensitive; and in adaptive mode, repeating a card only after its first miss, never repeating the last remaining card, exact-match answer checking, and re-queuing a different card. One mutation (re-queuing *correct* answers) was caught only by the timeout.
- Rewrote the two tests:
  - `test_quiz_mode_factory`: also tests mixed-case names (`"Adaptive"`, `" RANDOM "`). It checks the exact class (`type(...) is`, since a subclass would pass `isinstance`), that each call returns a new object, and that the mode plays exactly like the class built directly with the same 10-card deck and seeded `rng`.
  - `test_adaptive_mode_behavior`: one scripted session with a middle card missed twice, the last card missed twice (including while it is the only card left), and one correct answer typed with odd case and spacing. It checks the exact order of questions, that only missed cards repeat (once per miss), the stats, and that the session ends.
  - The session helper now fails with a clear message after 100 questions instead of hanging.
- Mistake caught: the first rerun reported 18/18, but the new tests were failing on the *unmodified* code. The helper looked up answers in a table that only had `Q1`-`Q5`, while the factory test used 10 cards. A test that always fails "catches" every mutation, so the AI flagged the 18/18 as meaningless, fixed the helper (answer with each card's own `back`), and added a guard to the runner: it now refuses to start unless the tests pass on the original code.
- Final result: the two required tests catch **18 of 18** mutations. 124 tests pass, total coverage is 99%, and black, flake8 and mypy are clean. An unused `ANSWERS` constant was removed. `utils/quiz_engine.py` was not changed.

**Changes Made:**
- None.

**Reasoning:**
- Nothing to mention.

**Outcome:**
- Quiz engine testing complete.

**Lessons Learned:** 
- A mutation score only means something if the tests pass on the real code first.

---

### 2026-10-17 - QA: Mutation Testing the Full-Session Integration Test

**Context:** Third QA step: the required integration test `test_full_session` in `tests/test_integration.py`, which simulates a user answering 3 questions and checks the final stats.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "now integration test: test_full_session: Simulate a user answering 3 questions and checking the final stats calculation."

**AI Response:**
- Applied the same mutation approach as for the quiz logic. It made the runner work on any file, kept the guard that refuses to run if the tests fail on the original code, and wrote 19 mutations: 6 in the stats calculation (`QuizStats`), 7 in how stats are displayed, and 6 in the session flow (`main.py`). Source files were restored after every run and checked to be identical to the commit.
- Baseline: the existing test caught **15 of 19**. It missed correct answers also being counted as mistakes, "Answers given" counting distinct missed cards instead of answers, the summary appearing without `--stats`, and questions numbered from 0. It also checked only printed text, never the calculated numbers.
- Rewrote `test_full_session`, still a 3-question game (right, wrong, and right with odd spacing):
  - it reads the engine's `QuizStats` through a spy on the factory: correct, incorrect, total, accuracy and mistakes;
  - it checks that exactly 3 answers were read;
  - it checks the questions and the feedback, line by line and in order;
  - it compares the whole final summary character for character.
- Added three companion tests for cases a 3-question game with `--stats` can't cover: no `--stats` (score only), an adaptive game where one card is missed twice (5 answers, 60.0%, "(2 times)"), and rounding at 100%, 33.3% and 0%.
- Final result: the tests together catch **19 of 19**. The required test alone catches 17; the two others (distinct-missed-cards counting and the summary without `--stats`) can't be caught by any 3-question game with `--stats`, so the companion tests cover them. 129 tests pass, total coverage is 99%, and black, flake8 and mypy are clean. `main.py` and `utils/quiz_engine.py` were not changed.

**Changes Made:**
- None.

**Reasoning:**
- Nothing to mention.

**Outcome:**
- Testing completed.

**Lessons Learned:**
- Nothing new about testing compared to the previous 2 steps.

---

### 2026-10-17 - QA: Options for Reaching 100% Coverage

**Context:** After the QA steps, total coverage was 99%. I wanted to know what it would take to reach 100%.

**AI Tool Used:** Claude Code (Claude Opus 5.5)

**Prompt/Request:** "what can we do to reach 100% coverage?"

**AI Response:**
- Ran coverage with `--cov-report=term-missing`. The only uncovered line is `main.py:199`, `sys.exit(main())` inside `if __name__ == "__main__":`. A test already runs `main.py` as a real process, but coverage doesn't measure a separate process by default.
- Proposed three options:
  1. (recommended) A test that runs `main.py` inside the test process with `runpy.run_path(..., run_name="__main__")`, which would also check that exit codes 0, 1 and 2 reach the operating system.
  2. Measure subprocesses with `[run] patch = subprocess` in a `.coveragerc` (supported by coverage 7.10.7).
  3. Exclude the line with `# pragma: no cover` or an `exclude_also` rule, which hides the line rather than testing it.
- Pointed out that `--cov=.` also measures `tests/`, which pushes the total up; the app code alone (`main.py` and `utils/`) is also at 99%.
- Pointed out that 100% coverage doesn't prove the tests catch bugs: the loader tests had 100% coverage and still missed 3 of 7 deliberate bugs in the mutation check.

**Changes Made:**
- I decided not to apply any of the options. Coverage stays at 99%, above the 80% target, and the code was not changed.

**Reasoning:**
- As the AI pointed out, 100% coverage doesn't mean that all bugs are caught.

**Outcome:**
- No changes.

**Lessons Learned:**
- The AI showed great reasoning skills.

---

## Tips for Effective AI Collaboration

### 1. Be Specific in Your Requests
- ❌ "Write a function"
- ✅ "Write a function that validates email addresses using regex, returns a boolean, and includes proper error handling"

### 2. Provide Context
- Include relevant code snippets
- Explain the larger goal
- Mention any constraints or requirements

### 3. Review and Understand
- Never copy AI code without understanding it
- Ask for explanations of complex logic
- Test the code before accepting it

### 4. Iterate and Refine
- Use follow-up questions to improve the code
- Ask for alternative implementations
- Request code reviews and suggestions

### 5. Document Your Process
- Keep detailed notes in this log
- Explain your decision-making process
- Track what works and what doesn't

## Common AI Collaboration Patterns

### Code Generation
- Initial implementation of classes/functions
- Boilerplate code creation
- Test case generation

### Code Review
- Ask AI to review your code for issues
- Request suggestions for improvements
- Get feedback on code structure

### Problem Solving
- Debugging help
- Algorithm suggestions
- Architecture advice

### Learning and Explanation
- Ask for explanations of complex concepts
- Request examples of design patterns
- Get guidance on best practices

## Reflection Questions

As you work through the project, consider these questions:

1. **What types of tasks did AI help with most effectively?**
2. **Where did you need to make the most modifications to AI suggestions?**
3. **What patterns did you notice in AI strengths and weaknesses?**
4. **How did your prompting technique improve over time?**
5. **What would you do differently in future AI collaborations?**

## Summary Statistics

At the end of your project, fill out these statistics:

- **Total AI interactions:** 7 logged above
- **Lines of AI-generated code used:** 1,674 (599 in `main.py` and `utils/`, 1,075 in `tests/`)
- **Lines of AI-generated code modified:** 0 by hand. All changes were made through follow-up prompts (duplicates on `front` and then `back`, lowercase-only keys)
- **Most helpful AI interaction:** ___
- **Most challenging AI interaction:** ___
- **Biggest lesson learned:** ___

---

**Note:** This log is a required component of your final project report. Be thorough and honest in your documentation to demonstrate your learning process and AI collaboration skills.