# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

It configures Claude for the AI-assisted development course project.

## Project Context

This is a learning project for a software engineering course focused on AI-assisted development. Students are building a Python application while learning to effectively collaborate with AI coding assistants.

The application is **the Flashcard Quizzer**: a command-line app that loads flashcards from JSON and quizzes the user in sequential, random, or adaptive mode. The full specification is on the project Instructions page in the classroom.

### Current state and the CLI contract

`main.py`, `utils/` and `tests/` ship empty on purpose. Building them is the project, so expect to create modules rather than find them. Keep the existing layout: entry point in `main.py`, helpers in `utils/`, pytest suite in `tests/`.

The finished app must accept these flags exactly, because the specification and grading use them:

```bash
python main.py --help
python main.py --mode sequential --file data/glossary.json   # modes: sequential, random, adaptive
python main.py -m adaptive -f data/python_basics.json
```

The flashcard loader must accept both JSON shapes in `data/`:
- `data/glossary.json`: a top-level array, `[{"front": ..., "back": ...}]`
- `data/python_basics.json`: an object wrapper, `{"cards": [{"front": ..., "back": ...}]}`

Missing files, malformed JSON and cards without `front`/`back` should produce a clear message, not a traceback. `docs/ai_edit_log.md` shows the expected loader behaviour in its example entry.

### Target architecture

The project brief (`fde.txt`) fixes these module and class names:

- `utils/file_handler.py` - data layer: loads and validates decks in both JSON formats.
- `utils/quiz_engine.py` - quiz logic: an abstract base class `QuizMode`, three subclasses `SequentialMode` (order 1, 2, 3...), `RandomMode` (shuffled) and `AdaptiveMode` (prioritises cards answered wrong), plus a factory that picks the mode from the `-m` value. Graders check the Strategy and Factory patterns by inspecting this file.
- `main.py` - CLI only: `argparse` with `-f/--file`, `-m/--mode` and `--stats`. Correct answers print in green and incorrect ones in red (ANSI codes, no extra dependency). Typing `exit` or pressing Ctrl+C quits cleanly without a traceback.

`docs/design_patterns.md` describes Strategy and Factory with task-manager examples. Adapt the ideas rather than copying the code.

Required tests (the names are part of the spec):

- `tests/test_flashcard_loader.py`: `test_load_valid_flashcards_array`, `test_load_invalid_json`, `test_load_missing_required_field`
- `tests/test_quiz_modes.py`: `test_quiz_mode_factory`, `test_adaptive_mode_behavior` (incorrect cards really do come back)
- `tests/test_integration.py`: `test_full_session` (simulates 3 answers and checks the final stats)

### `docs/ai_edit_log.md` is the student's record

The log is graded evidence of the student's own AI collaboration. Never invent entries or write interactions that did not happen. After each milestone, Claude may draft a factual entry from the real session: the student's prompt verbatim, a summary of what was generated, and what the student had changed. Leave **Reasoning** and **Lessons Learned** for the student to write. The example entry in the template must be deleted before submission.

## Course Objectives

Students will:
- Build a functional Python application with clear requirements and constraints
- Collaborate effectively with AI assistants while maintaining code quality
- Apply software engineering principles including design patterns and separation of concerns
- Develop and maintain a comprehensive unit test suite
- Document their AI collaboration process and learning journey

## Student Responsibilities

### Code Quality
- Review and understand all AI-generated code before accepting it
- Test AI-generated code thoroughly with various inputs and edge cases
- Refactor code for clarity, maintainability, and adherence to project standards
- Implement proper error handling and input validation
- Follow Python coding conventions (PEP 8) and project style guidelines

### Software Engineering Practices
- Apply appropriate design patterns where beneficial
- Maintain separation of concerns and modular code structure
- Write comprehensive unit tests with good coverage (>80%)
- Use proper version control practices with descriptive commit messages
- Document code with clear docstrings and comments where necessary

### AI Collaboration
- Write specific, clear prompts that provide context and requirements
- Critically evaluate AI responses for correctness, security, and efficiency
- Document all AI interactions in the provided AI edit log
- Ask for explanations when AI logic is unclear
- Iterate on AI suggestions to improve code quality

### Documentation
- Maintain detailed logs of AI interactions and decisions
- Update project documentation as features are added
- Complete the final project report with reflections on AI collaboration
- Document any challenges faced and solutions implemented

## AI Assistant Guidelines

### Code Generation
- Provide clean, well-documented code that follows Python best practices
- Include type hints and proper error handling
- Suggest appropriate design patterns when beneficial
- Ask clarifying questions if requirements are unclear

### Code Review
- Point out potential security vulnerabilities
- Suggest improvements for readability and maintainability
- Identify edge cases that need testing
- Recommend refactoring opportunities

### Educational Support
- Explain complex concepts and design decisions
- Provide examples of best practices
- Suggest learning resources when appropriate
- Help debug issues and understand error messages

## Project Structure

The project follows this organization:
- `main.py` - Application entry point
- `utils/` - Reusable utility modules
- `data/` - Sample flashcard decks in JSON
- `tests/` - Comprehensive unit test suite
- `docs/` - Project documentation and templates
- `ai_guidance/` - AI collaboration best practices
- `.claude/` - Claude-specific configuration

## Development Tools

Students should use these tools for code quality:
- **pytest** for testing
- **black** for code formatting
- **isort** for import organization
- **flake8** for linting
- **mypy** for type checking

## Common Commands

Students can use these commands during development:
- `python main.py` - Run the application
- `python -m pytest` - Run all tests
- `python -m pytest --cov=. --cov-report=html` - Run tests with coverage
- `python -m black .` - Format code
- `python -m isort .` - Organize imports
- `python -m flake8 .` - Check linting
- `python -m mypy .` - Type checking
- `python -m pytest tests/test_file.py::test_name` - Run a single test (add `-k <expr>` to filter by name)
- `python -m pytest --cov=. --cov-report=term-missing` - Coverage report in the terminal

All of these must pass before submission: `python -m pytest --cov=. --cov-report=html` (>80% coverage), `python -m black --check .`, `python -m flake8 .` and `python -m mypy .`.

`.flake8` sets `max-line-length = 88` and `extend-ignore = E203` so flake8 agrees with black (88 characters, matching `.editorconfig`). If you add isort config, use `profile = "black"`.

Install packages with `python -m pip install -r requirements.txt`, and run every tool through `python -m` as listed above. In the provided workspace (`/voc/work/project/starter`), install directly; do not create a virtual environment. On a personal machine, the README recommends creating and activating a `venv` first.

### Claude-specific files in `.claude/`

- `.claude/commands/*` are standalone Python scripts with no `.md` extension, so Claude Code does not register them as slash commands. Each one prints a prompt template, for example `python .claude/commands/review-code --file main.py --focus testing`.
- `.claude/mcp.json` is not loaded by Claude Code, which reads project MCP servers from `.mcp.json` at the project root. Treat it as reference material for the tool commands it lists.

## Definition of Done

### Every task

A task is done only when all of these checks pass:

- [ ] `python -m pytest` - the test suite passes
- [ ] `python -m black --check .` - code formatting is enforced, so no files need reformatting
- [ ] `python -m mypy .` - static type checking reports no errors
- [ ] `python -m flake8 .` - linting reports zero errors

Before reporting a task as complete, run all four checks and report the results. If any check fails, fix it before calling the task done.

### The whole project

The project is complete when, in addition:

- [ ] `python main.py -m adaptive -f data/python_basics.json` plays a full game from start to finish
- [ ] `utils/quiz_engine.py` uses the Strategy pattern (`QuizMode` and its three subclasses) and the Factory pattern (mode selection)
- [ ] all the required tests listed above exist and pass
- [ ] `python -m pytest --cov=. --cov-report=html` reports coverage above 80%
- [ ] `docs/ai_edit_log.md` has at least 5 real entries showing improved prompts or corrected logic, and the example entry has been removed
- [ ] `README.md` is rewritten with current setup instructions and a description of the features
- [ ] the final report, written from `docs/report_template.md`, is 1000-1500 words

## Assessment Criteria

Projects will be evaluated on:
1. **Functionality** - Does the application work correctly?
2. **Code Quality** - Is the code well-structured and maintainable?
3. **Testing** - Are there comprehensive tests with good coverage?
4. **AI Collaboration** - Did the student effectively work with AI while maintaining quality?
5. **Documentation** - Are AI interactions and decisions well-documented?

## Best Practices for AI Collaboration

### Effective Prompting
- Be specific about requirements and constraints
- Provide context about the existing codebase
- Ask for explanations of complex logic
- Request code reviews and improvement suggestions

### Code Review Process
- Always understand AI-generated code before using it
- Test thoroughly with various inputs and edge cases
- Check for security vulnerabilities and edge cases
- Refactor for clarity and maintainability

### Learning Approach
- Use AI as a learning tool, not a replacement for understanding
- Ask follow-up questions to deepen understanding
- Experiment with different approaches
- Document lessons learned throughout the process

## Remember

The goal is not just to build a working application, but to learn effective AI collaboration while maintaining high software engineering standards. Students should:
- Take ownership of their code quality
- Use AI as a powerful tool while exercising good judgment
- Focus on learning and understanding, not just completion
- Document their journey for future reference and assessment

Success in this project comes from thoughtful collaboration with AI, not from accepting AI suggestions without review and understanding.