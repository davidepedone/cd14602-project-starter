# Concept 3: Complexity Control

## Exercise Overview

Master XML techniques for controlling solution complexity and preventing over-engineering through examples and scope boundaries.

**Scenario**: AI tends to create overly complex solutions for simple tasks, introducing unnecessary design patterns, abstractions, or architectural complexity. Your task is to use examples and constraints to guide AI toward appropriately-scoped solutions.

**Your Task**: Create XML structures that prevent over-engineering by demonstrating appropriate complexity levels and setting clear scope boundaries.

## Learning Objectives

- Master `<example>` tags to show appropriate complexity levels
- Use `<complexity_limits>` and scope boundaries to prevent over-engineering
- Prevent the over-engineering pattern from Lesson 2
- Guide AI toward solutions that match your system's complexity needs

## Files

| File | Purpose |
|---|---|
| `starter/over_engineering_examples.py` | Three prompts that lead to over-engineering, the typical AI responses, and the simple solutions |
| `starter/simplicity_tester.py` | Scores how well a prompt controls complexity |
| `starter/complexity_control_templates.py` | The three prompts as templates, with `[STUDENT TODO]` slots for you to complete |
| `starter/test_complexity_control.py` | Tests your completed prompts (`STUDENT_PROMPTS` at the top of the file) |
| `solution/controlled_prompts.py` | Completed prompts and an analysis of the techniques used (in the Udacity workspace) |
| `PROMPTS.md` | The structured prompts shown on this exercise's Solution page in the classroom |

## Instructions

### Step 1: Review Prompts That Lead to Over-Engineering
```bash
cd starter
python over_engineering_examples.py
```

**What you'll see:**
- Three prompts: name formatting, email validation, and API endpoint configuration
- The over-engineered responses AI typically gives to each one
- The simple solution that would be enough
- Warning phrases and missing constraints that invite complexity

### Step 2: See How Complexity Controls Are Scored
```bash
python simplicity_tester.py
```

**What you'll see:** the analysis of a high-risk prompt next to a well-controlled one, with risk factors (trigger words such as "enterprise" and "scalable") and protective factors (complexity control tags, simple examples).

### Step 3: Complete the Templates
```bash
python complexity_control_templates.py
```

1. **Review** the three templates, the guidance for each constraint type, and the completion checklist
2. **Complete** each template in `complexity_control_templates.py` by replacing every `[STUDENT TODO]`:
   - `<complexity_limits>`: measurable boundaries, such as "Single function, maximum 10 lines"
   - `<forbidden_approaches>`: patterns to rule out, such as "No design patterns (Strategy, Factory, Builder)"
   - `<scope_boundaries>` / `<simplicity_requirements>`: keep the change focused and simple
   - `<example>`: a short function or object from the existing codebase that shows the size you want, in a plain `<example>` tag (the form the tests look for)
3. **Optionally**, ask Claude Code to draft the constraints, then review every line: confirm each limit fits the task and that the original task, context, and requirements are all still there

### Step 4: Run the Tests
1. Open `test_complexity_control.py` and find `STUDENT_PROMPTS` near the top
2. Replace each `<!-- STUDENT TODO ... -->` comment with your completed prompt: `name_formatting` (Template 1), `email_validation` (Template 2), `api_configuration` (Template 3)
3. Run:
```bash
pytest test_complexity_control.py -v
```

**Expected Output:**
- **Complexity control tests**: each prompt has `<complexity_limits>` or `<forbidden_approaches>`
- **Over-engineering prevention tests**: no more than one trigger word or vague phrase outside the constraint sections
- **Constraint quality tests**: scored on measurable limits, specific forbidden patterns, and a short example; a prompt passes with at least as many strengths as weaknesses

A prompt that still contains `STUDENT TODO` is skipped, not failed. Before you add your prompts, you'll see 3 passed and 9 skipped.

### Step 5: Compare with the Solution
In the Udacity workspace, the `solution` folder sits next to `starter`:
```bash
cd ../solution
python controlled_prompts.py
```

## Exercise Template

### Complexity Risk Analysis

For each prompt, identify:
- **Trigger Language**: Which words invite over-engineering ("scalable", "extensible", "best practices")?
- **Missing Limits**: What size or structure boundaries are absent?
- **Missing Examples**: What existing code would show the right complexity level?
- **Scope Creep**: What could AI add that the task never asked for?

### Complexity Control Checklist

- [ ] `<complexity_limits>` sets measurable boundaries (lines, functions, classes)
- [ ] `<forbidden_approaches>` names the patterns and frameworks to avoid
- [ ] `<scope_boundaries>` or `<simplicity_requirements>` keeps the change focused
- [ ] `<example>` shows a short, simple piece of the existing codebase
- [ ] Trigger words like "enterprise" or "extensible" are kept out of everything except the constraint sections

### Quality Assessment

Rate your controlled prompts on:
- **Measurability**: Can each limit be checked by counting?
- **Specificity**: Do forbidden approaches name concrete patterns?
- **Proportion**: Does the example match the size of the problem?
- **Fit**: Would each limit still make sense for this project, or is it too restrictive?

## Key Learning Points

- Examples show AI the expected complexity and architectural style
- Measurable limits work better than "keep it simple"
- Forbidden approaches stop AI from reaching for patterns a simple task doesn't need
- Limits should match the problem: too strict a limit can be as unhelpful as none

## Success Criteria

After this exercise, you should be able to:
1. Design examples that demonstrate appropriate solution complexity
2. Set measurable complexity limits and specific forbidden approaches
3. Use scope boundaries to keep AI changes focused
4. Prevent over-engineering through well-chosen constraints and examples

This completes the Lesson 3 exercises.
