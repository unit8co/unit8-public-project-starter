# Change Understanding Quiz

The starter includes a PR gate that asks developers five questions about their
own diff before a pull request can merge. It is meant for
AI-assisted work where a developer needs to prove they understand what Codex or
another LLM changed.

The gate is intentionally lightweight:

- it asks exactly five short-answer questions about the current git diff
- it requires four correct answers to pass
- it writes `.change-quiz/result.json`
- CI verifies that the artifact still matches the PR diff

This is a comprehension guardrail, not a security boundary. The checksum catches
stale or accidentally edited artifacts, but it is not a substitute for code
review, branch protection, or normal tests.

## Local Use

Run the quiz before opening a PR:

```bash
uv run agentic-starter quiz-changes --base origin/main --head HEAD
```

The command requires `OPENAI_API_KEY` and uses `OPENAI_MODEL`. It creates
`.change-quiz/result.json`; commit that file with the code change.

If the code changes after the quiz, re-run the command so the artifact hash
matches the latest diff.

To verify the committed artifact without calling an LLM:

```bash
uv run agentic-starter quiz-changes --verify --base origin/main --head HEAD
```

## GitHub Enforcement

The workflow job runs by default on pull requests in downstream repos created
from this template.

To enforce it as a merge requirement in GitHub:

1. Make the `change-quiz` GitHub Actions check required in branch protection or
   a ruleset.
2. Ensure PR authors commit `.change-quiz/result.json` after passing the quiz.

`CHANGE_QUIZ_REQUIRED` is now an opt-out switch:

- unset: enforce the quiz job
- `true`: enforce the quiz job
- `false`: disable the quiz job for that repo

The CI job does not call an LLM. It only verifies the committed artifact, score,
merge-base SHA, relevant file list, and diff hash. It records the PR head SHA for
audit, but does not enforce it because committing the quiz artifact necessarily
changes the head commit.

## File Selection

The quiz ignores generated, cache, binary, lockfile, and artifact paths such as:

- `uv.lock`
- `.terraform.lock.hcl`
- `.change-quiz/result.json`
- `__pycache__/`
- `.pytest_cache/`
- image, archive, font, and compiled binary files

Everything else in the diff is considered quiz-relevant, including source,
tests, docs, infrastructure, and workflow files.
