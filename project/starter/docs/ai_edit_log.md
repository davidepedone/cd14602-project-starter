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

## Example Entry

> This entry shows the expected level of detail. It does **not** count toward your five required entries. Delete it before you submit.

### 2024-01-15 - Flashcard Loader Validation

**Context:** I needed a module that loads flashcards from a JSON file and rejects bad data with a clear message instead of a traceback.

**AI Tool Used:** Claude Code

**Prompt/Request:** "Create `data_loader.py` with a function that loads flashcards from a JSON file. Support both a plain list of `{"front", "back"}` objects and a `{"cards": [...]}` wrapper. Raise a custom exception with a helpful message if the file is missing, the JSON is malformed, or a card has no `back`. Use type hints."

**AI Response:** Claude generated a `load_flashcards()` function and a `FlashcardLoadError` exception. It handled both JSON formats and a missing file, but it caught every exception with a bare `except:` and only checked for `front`.

**Changes Made:** 
- Replaced the bare `except:` with specific `FileNotFoundError` and `json.JSONDecodeError` handlers
- Added validation that every card has non-empty `front` and `back` strings
- Added the card's position to the error message so the user can find the bad entry

**Reasoning:** 
- A bare `except:` hides real bugs, including `KeyboardInterrupt`
- A card without a `back` would break the quiz loop later, far from the cause
- A message that names the bad card is far easier to act on

**Outcome:** The loader now rejects bad decks with one readable line, and `test_load_missing_required_field` passes.

**Lessons Learned:** 
- AI covered the happy path well but under-specified the error handling
- Naming the exact failure cases in the prompt produced better code than asking for "error handling"
- Each requirement in the prompt should map to a test

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

**Changes Made:** _[To complete after your review: what you changed or asked to change in the generated code. Also note your view on the array-format correction.]_

**Reasoning:** _[Your words: why you made those changes.]_

**Outcome:** _[Your words: the final state after your review.]_

**Lessons Learned:** _[Your words. Starting point: the example in the prompt contradicted the spec, so a precise example matters as much as the description.]_

---

### [Date] - [Brief Description]

**Context:** 

**AI Tool Used:** 

**Prompt/Request:** 

**AI Response:** 

**Changes Made:** 

**Reasoning:** 

**Outcome:** 

**Lessons Learned:** 

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

- **Total AI interactions:** ___
- **Lines of AI-generated code used:** ___
- **Lines of AI-generated code modified:** ___
- **Most helpful AI interaction:** ___
- **Most challenging AI interaction:** ___
- **Biggest lesson learned:** ___

---

**Note:** This log is a required component of your final project report. Be thorough and honest in your documentation to demonstrate your learning process and AI collaboration skills.