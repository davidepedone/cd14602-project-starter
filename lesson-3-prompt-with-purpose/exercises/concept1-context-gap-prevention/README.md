# Concept 1: Context Gap Prevention

## Exercise Overview

Learn to use XML structure to prevent the context gap pattern, where AI works from an incomplete picture of your system, guesses, and can drop or break existing functionality.

**Scenario**: You have three traditional conversational prompts. Each one leaves AI to guess: vague terms, an undescribed "current setup", or requirements buried in a run-on sentence. Your task is to convert them into structured XML prompts that state the task, context, requirements, and constraints explicitly, including what must keep working.

**Your Task**: Create XML prompts that give AI the context and requirements it needs, so it doesn't have to guess or break what already works.

## Learning Objectives

- Master the core XML tags: `<task>`, `<context>`, `<requirements>`, and `<constraints>`
- Prevent the context gap pattern from Lesson 2
- Turn vague terms and implied assumptions into explicit, checkable statements
- Separate buried requirements and constraints into clear lists
- Make existing functionality that must keep working explicit

## Files

| File | Purpose |
|---|---|
| `starter/traditional_prompts.py` | Three traditional prompts and the problems each one causes |
| `starter/xml_templates.py` | XML templates with `[STUDENT TODO]` slots for you to complete |
| `starter/prompt_tester.py` | Compares a sample traditional prompt with an XML version and scores both |
| `starter/test_prompt_structure.py` | Tests your XML prompts (`STUDENT_XML_PROMPTS` in the file) |
| `solution/completed_xml_prompts.py` | Completed XML prompts and the key improvements in each (in the Udacity workspace) |
| `PROMPTS.md` | The structured prompts shown on this exercise's Solution page in the classroom |

## Instructions

### Step 1: Review Traditional Prompts
```bash
cd starter
python traditional_prompts.py
```

**What you'll see:**
- 3 traditional prompts: data processing, API caching, and an authentication system
- The common problems each prompt causes
- Clear examples of ambiguity and missing context

### Step 2: Practice XML Conversion
```bash
python xml_templates.py
```

1. **Examine** the traditional prompts in `traditional_prompts.py`
2. **Convert** each prompt by completing its template in `xml_templates.py` (replace every `[STUDENT TODO]`)
3. **Optionally**, ask Claude Code to draft each conversion, then refine it. Start a fresh session (`/clear`) for each prompt, and remove anything it adds about systems you didn't describe
4. **Compare** traditional and XML prompts with `python prompt_tester.py`, which scores a sample pair for structure, clarity, and completeness

### Step 3: Run the Tests
1. Open `test_prompt_structure.py` and find `STUDENT_XML_PROMPTS`
2. Replace each `<!-- STUDENT TODO ... -->` comment with your XML prompt: `data_processing` (Prompt 1), `api_caching` (Prompt 2), `authentication` (Prompt 3)
3. Run:
```bash
pytest test_prompt_structure.py -v
```

**Expected Output:**
- **Structure tests**: Verify your XML prompts use all four tags
- **Content quality tests**: Check for a specific task, a context with system details, requirements as a list, and clear constraints

A prompt that still contains `STUDENT TODO` is skipped, not failed. Before you add your prompts, you'll see 2 passed and 6 skipped.

### Step 4: Compare with Solution
In the Udacity workspace, the `solution` folder sits next to `starter`:
```bash
cd ../solution
python completed_xml_prompts.py
```

## Exercise Template

### Traditional Prompt Analysis

For each prompt, identify:
- **Ambiguity Issues**: What could be interpreted multiple ways?
- **Missing Context**: What background information is assumed?
- **Unclear Requirements**: What specific outcomes are expected?
- **Constraint Gaps**: What limitations aren't specified?

### XML Conversion Checklist

- [ ] `<task>` clearly states the specific objective
- [ ] `<context>` provides necessary background information
- [ ] `<requirements>` lists explicit, testable outcomes
- [ ] `<constraints>` specifies limitations and boundaries

### Quality Assessment

Rate your XML prompts on:
- **Clarity**: Can AI understand exactly what's needed?
- **Completeness**: Are all necessary details included?
- **Specificity**: Are requirements measurable and testable?
- **Structure**: Does XML organization improve comprehension?

## Key Learning Points

- XML structure prevents information loss that occurs in conversational prompts
- Clear separation of task, context, and requirements improves AI accuracy
- Structured prompts are easier to iterate and improve
- Basic XML tags create the foundation for advanced prompt engineering

## Success Criteria

After this exercise, you should be able to:
1. Identify structural problems in traditional prompts
2. Convert conversational prompts to basic XML format
3. Use `<task>`, `<context>`, `<requirements>`, and `<constraints>` tags effectively
4. Explain how each tag removes a specific source of guesswork for AI

Progress to Concept 2 to learn advanced constraint techniques for preventing phantom dependencies.
