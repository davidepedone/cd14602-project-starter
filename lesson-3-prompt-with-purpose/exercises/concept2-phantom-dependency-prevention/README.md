# Concept 2: Phantom Dependency Prevention

## Exercise Overview

Learn to use XML constraint techniques to prevent AI from suggesting non-existent libraries and dependencies.

**Scenario**: AI keeps suggesting libraries that don't exist in your environment or aren't available in your project. Your task is to use constraint tags to explicitly define what libraries are available and prevent phantom dependencies.

**Your Task**: Create constraint structures that eliminate AI suggestions of non-existent libraries and dependencies.

## Learning Objectives

- Master `<allowed_libraries>`, `<forbidden_approaches>`, and `<constraints>` tags
- Prevent the phantom dependency pattern from Lesson 2
- Explicitly define available vs. unavailable dependencies
- Create constraints that guide AI toward implementable solutions

## Files

| File | Purpose |
|---|---|
| `starter/problem_prompts.py` | Three XML prompts that lack constraints, their risks, and an improvement checklist |
| `starter/constraint_templates.py` | The three prompts as templates, with `[STUDENT TODO]` constraint slots for you to complete |
| `solution/enhanced_prompts.py` | Completed prompts and an analysis of how the constraints work (in the Udacity workspace) |
| `PROMPTS.md` | The structured prompts shown on this exercise's Solution page in the classroom |

This exercise has no automated tests: you check your constraints against the improvement checklist and the solution.

## Instructions

### Step 1: Review Problem Prompts
```bash
cd starter
python problem_prompts.py
```

**What you'll see:**
- Three XML prompts that lack proper constraints: large CSV file processing, logging in a discount calculator, and a mobile notification system
- The missing constraints, phantom dependency risks, and over-engineering risks for each
- A constraint improvement checklist for each prompt

### Step 2: Practice Constraint Design
```bash
python constraint_templates.py
```

1. **Examine** the problematic prompts in `problem_prompts.py`
2. **Identify** what constraints are missing, using the improvement checklist from Step 1
3. **Add** appropriate constraint tags by completing the templates in `constraint_templates.py` (replace every `[STUDENT TODO]`)
4. **Optionally**, ask Claude Code to draft the constraints. Then check that every library it lists really exists (on PyPI or in its official documentation), remove anything it claims about tools you don't have, and confirm the original `<context>` is still there

### Step 3: Compare with Solution
In the Udacity workspace, the `solution` folder sits next to `starter`:
```bash
cd ../solution
python enhanced_prompts.py
```

**What you'll see:** the three completed prompts, then an analysis of how their constraints prevent phantom dependencies, prevent over-engineering, and keep the solution compatible with the existing system.

## Exercise Template

### Problem Pattern Analysis

For each problematic prompt, identify:
- **Phantom Dependency Risk**: What non-existent libraries might AI suggest?
- **Over-Engineering Risk**: Where might AI add unnecessary complexity?
- **Architecture Mismatch Risk**: What solutions wouldn't fit existing systems?
- **Missing Constraint Types**: What boundaries need to be set?

### Constraint Design Checklist

- [ ] `<allowed_libraries>` explicitly lists available dependencies
- [ ] `<forbidden_approaches>` prevents problematic patterns
- [ ] `<complexity_limits>` sets appropriate solution boundaries
- [ ] `<scope_boundaries>` and `<preservation_requirements>` keep changes limited to what was asked
- [ ] `<integration_requirements>` and `<existing_services>` specify system compatibility needs

### Quality Assessment

Rate your constraint-enhanced prompts on:
- **Phantom Prevention**: Do constraints eliminate invalid dependencies?
- **Complexity Control**: Do constraints prevent over-engineering?
- **Architecture Fit**: Do constraints ensure system compatibility?
- **Specificity**: Are constraints measurable and testable?

## Key Learning Points

- Explicit constraints prevent AI from hallucinating non-existent solutions
- Complexity limits guide AI toward appropriately-scoped implementations
- Forbidden approaches eliminate patterns that cause integration problems
- Well-designed constraints improve AI output reliability and system fit

## Success Criteria

After this exercise, you should be able to:
1. Identify constraint gaps that lead to phantom dependencies
2. Design effective constraint structures using multiple tag types
3. Prevent over-engineering through complexity boundaries
4. Create constraints that ensure architectural compatibility

Progress to Concept 3 to learn complexity control with examples and scope boundaries.
