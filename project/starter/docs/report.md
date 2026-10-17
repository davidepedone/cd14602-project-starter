# AI-Assisted Development Project Report

**Student Name:** Davide Pedone
**Project Title:** Flashcard Quizzer
**Date:** 17.10.2026

## Executive Summary

I built the Flashcard Quizzer, a Python command-line app that loads flashcard decks from JSON and quizzes the user in sequential, random or adaptive mode. It validates deck files, gives colored feedback and shows statistics at the end.

I used one prompt for each build phase. For testing, I preferred three prompts, one for each module to test. As I went on, I refined how I wrote prompts based on the output of the previous ones. For example, in Phase 3 I wrote "if you have doubt ask and do not just assume".

## Project Overview

### Problem Statement

Flashcards work best when the cards you get wrong come back more often. The goal was a simple command-line tool that quizzes the user, adapts to their mistakes, and doesn't crash on badly written deck files.

### Solution Approach

The app has three layers: `utils/file_handler.py` loads and validates decks, `utils/quiz_engine.py` contains the quiz logic with no input or output, and `main.py` is only the CLI. It uses Python 3.9 and the standard library only. The development tools were pytest, black, isort, flake8 and mypy.

### Final Features

- [x] Array and `{"cards": [...]}` deck formats
- [x] Friendly errors with no tracebacks, including for duplicates and wrong key case
- [x] Sequential, random and adaptive modes
- [x] `-f`, `-m` and `--stats` flags with defaults
- [x] Green/red feedback; quitting with `exit`, Ctrl+C or Ctrl+D
- [x] End-of-quiz score and detailed statistics

## AI Collaboration Experience

### AI Tools Used

- [x] Claude (Claude Code, Claude Opus 5.5)

### Collaboration Workflow

1. Read the specification for the phase
2. Write the prompt
3. Review the code the AI produced
4. Run a manual round of tests
5. Think about the result and compare it with the Definition of Done
6. Ask for corrections when needed
7. Complete the entry in `ai_edit_log.md`
8. Commit and push

### Most Valuable AI Interactions

**1. A mistake in my own prompt.** My Phase 1 prompt described the array format wrongly, with `front` and `back` in two separate objects. The AI noticed that this contradicted the specification and the sample deck, followed the specification, and told me before writing any code.

**2. The false 18/18.** During the quiz logic QA, a mutation run reported that the tests caught all 18 deliberate bugs. The AI realised by itself that the result was worthless, because the new tests were already failing on the real code. It fixed the test helper and added a check so this can't happen again.

**3. Mutation testing.** I hadn't asked for it: the AI proposed and implemented it on the loader tests. Those tests had 100% coverage but missed 3 of 7 deliberate bugs. For the quiz logic the score went from 10/18 to 18/18. The quality of the tests improved considerably.

### Challenges with AI Collaboration

- It produces a large amount of code in a short time, so you have to limit the scope of each request to make the review easier.
- When it lacks context it makes assumptions, and that is a double-edged sword. Sometimes it's great, as with mutation testing. On the other hand, it risks implementing or touching parts of the code you didn't want changed.

## Software Engineering Practices

### Code Quality Measures

- [x] Formatting (black, isort) and linting (flake8, mypy)
- [x] Type hints and docstrings
- [x] Error handling: one error type for bad decks, and clean exits

### Testing Strategy

There are 129 pytest tests: loader tests, quiz mode tests, and integration tests that run full sessions through `main()` with scripted input. Coverage is 99%. Tests were written right after each feature, not before it, so this was not TDD. The required tests were then checked with mutation testing:

| Required tests | Bugs caught before | After |
|---|---|---|
| Data loader | 4/7 | 7/7 |
| Quiz logic | 10/18 | 18/18 |
| Full session | 15/19 | 19/19 |

### Design Patterns Used

- **Strategy:** the abstract `QuizMode` holds the shared session logic. `SequentialMode`, `RandomMode` and `AdaptiveMode` only decide which card comes next and what happens after an answer.
- **Factory:** `create_quiz_mode()` picks the class from the `-m` value through a registry, which also provides the CLI's choices.

## Technical Challenges and Solutions

### Challenge 1: black and flake8 disagreed on line length

**Problem:** black formats lines up to 88 characters, flake8 allows only 79.
**Solution:** a `.flake8` file with `max-line-length = 88`.
**Lessons Learned:** these tools are very useful for standardising the generated code and making it easier to read during review.

### Challenge 2: "No module named pytest"

**Problem:** the tests didn't run in my terminal.
**Solution:** activating the venv with `source venv/bin/activate`.
**Lessons Learned:** I had forgotten to activate the venv, and the AI found the problem immediately.

### Challenge 3: Tests that look strong but aren't

**Problem:** tests with 100% coverage still missed deliberate bugs.
**Solution:** mutation testing, and strengthening the tests until every mutation was caught.
**Lessons Learned:** I hadn't considered mutation testing. I'll definitely remember it next time and add it to the prompt or the requirements.

## Code Quality Analysis

### Metrics

- Lines of code: 599 in the app, 1,075 in the tests
- Test coverage: 99%
- Functions/classes: 43
- Linting: 0 flake8 errors; black and mypy clean

### Self-Assessment

- **Code Readability: 5.** Partly thanks to Python's expressiveness, the code is compact and easy to understand.
- **Code Maintainability: 4.** The code seems easy to change, because it is readable.
- **Test Quality: 5.** Even though I decided to stop at 99% coverage, the tests cover many edge cases.
- **Documentation: 4.** The README, docstrings and AI log are complete, but I'm not a fan of comments inside the code; they are often redundant.

## Learning Outcomes

You have to be very careful with prompts: a few typos are acceptable, but the output always needs reviewing. It's important to give strict guidelines. The answers are often very verbose, so there's a risk of missing parts of the reasoning.

## Reflection

### What Worked Well

Speed. In a short time I implemented all the required features, much faster than I would have on my own.

### What Could Be Improved

Much stricter prompts and guidelines from the start. For example: add comments only where strictly necessary, always ask when in doubt, and use mutation testing from the beginning.

### Future Enhancements

- Categories for the questions, so the user can choose a category instead of giving a file
- Letting the user add new questions and answers without editing the JSON file

## Conclusion

AI is here, and it's here to stay, but with great power comes great responsibility. The speed, the general accuracy of the answers and the amount of output produced in a short time can lead the user to accept answers without a critical eye.

## Appendix: AI Interaction Log

See `docs/ai_edit_log.md`, with 7 entries covering the three build phases, three QA steps and the coverage decision.
