"""LLM-assisted change-understanding quiz for PR quality gates."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from agentic_project_starter.shared.config import Settings

ARTIFACT_VERSION = 1
QUESTION_COUNT = 5
PASSING_SCORE = 4
DEFAULT_ARTIFACT_PATH = Path(".change-quiz/result.json")

IGNORED_EXACT_PATHS = {
    ".change-quiz/result.json",
    "uv.lock",
}
IGNORED_NAMES = {
    ".terraform.lock.hcl",
}
IGNORED_PARTS = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".terraform",
    ".uv-cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "target",
}
IGNORED_SUFFIXES = {
    ".7z",
    ".avif",
    ".bin",
    ".bmp",
    ".bz2",
    ".class",
    ".coverage",
    ".db",
    ".egg-info",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".lock",
    ".mo",
    ".mp3",
    ".mp4",
    ".otf",
    ".pdf",
    ".png",
    ".pot",
    ".pyc",
    ".pyo",
    ".so",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tgz",
    ".ttf",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}

JsonProvider = Callable[[str], Mapping[str, Any]]
InputFn = Callable[[str], str]
PrintFn = Callable[[str], None]


class QuizError(RuntimeError):
    """Raised when quiz generation, grading, or artifact validation cannot proceed."""


@dataclass(frozen=True, slots=True)
class ChangeSet:
    """Git diff context used to generate and verify a change quiz."""

    base_ref: str
    head_ref: str
    base_sha: str
    head_sha: str
    merge_base_sha: str
    changed_files: tuple[str, ...]
    relevant_files: tuple[str, ...]
    diff: str

    @property
    def diff_hash(self) -> str:
        """Return a stable hash for the quiz-relevant diff."""

        return _sha256_text(self.diff)

    @property
    def file_list_hash(self) -> str:
        """Return a stable hash for the quiz-relevant file list."""

        return _sha256_json(list(self.relevant_files))


@dataclass(frozen=True, slots=True)
class QuizQuestion:
    """A single change-specific question and expected answer guide."""

    question_id: int
    question: str
    answer_guide: str


@dataclass(frozen=True, slots=True)
class GradedAnswer:
    """A developer answer after LLM grading."""

    question_id: int
    question: str
    answer: str
    answer_guide: str
    correct: bool
    feedback: str


@dataclass(frozen=True, slots=True)
class QuizValidation:
    """Validation result for a committed quiz artifact."""

    valid: bool
    message: str


def collect_change_set(
    *,
    base_ref: str,
    head_ref: str,
    repo_path: Path | str | None = None,
) -> ChangeSet:
    """Collect the quiz-relevant files and diff between two git refs."""

    repo = Path.cwd() if repo_path is None else Path(repo_path)
    base_sha = _git(["rev-parse", base_ref], repo).strip()
    head_sha = _git(["rev-parse", head_ref], repo).strip()
    merge_base_sha = _git(["merge-base", base_ref, head_ref], repo).strip()
    changed_output = _git(["diff", "--name-only", f"{merge_base_sha}..{head_sha}"], repo)
    changed_files = tuple(line for line in changed_output.splitlines() if line)
    relevant_files = filter_quiz_relevant_files(changed_files)
    diff = ""

    if relevant_files:
        diff = _git(
            [
                "diff",
                "--no-ext-diff",
                "--find-renames",
                f"{merge_base_sha}..{head_sha}",
                "--",
                *relevant_files,
            ],
            repo,
            strip=False,
        )

    return ChangeSet(
        base_ref=base_ref,
        head_ref=head_ref,
        base_sha=base_sha,
        head_sha=head_sha,
        merge_base_sha=merge_base_sha,
        changed_files=changed_files,
        relevant_files=relevant_files,
        diff=diff,
    )


def filter_quiz_relevant_files(paths: Sequence[str]) -> tuple[str, ...]:
    """Return changed paths that should be covered by a comprehension quiz."""

    return tuple(path for path in paths if is_quiz_relevant_file(path))


def is_quiz_relevant_file(path: str) -> bool:
    """Return whether a changed path should influence quiz generation."""

    normalized = path.replace("\\", "/").strip("/")
    if normalized in IGNORED_EXACT_PATHS:
        return False

    parts = tuple(part for part in normalized.split("/") if part)
    if not parts:
        return False

    if any(part in IGNORED_PARTS for part in parts):
        return False

    name = parts[-1]
    if name in IGNORED_NAMES:
        return False

    lowered = name.lower()
    return not any(lowered.endswith(suffix) for suffix in IGNORED_SUFFIXES)


def generate_questions(change_set: ChangeSet, provider: JsonProvider) -> tuple[QuizQuestion, ...]:
    """Generate five quiz questions from a git diff using a JSON LLM provider."""

    if not change_set.relevant_files:
        raise QuizError("No quiz-relevant files changed.")

    payload = provider(_question_prompt(change_set))
    raw_questions = payload.get("questions")
    if not isinstance(raw_questions, list) or len(raw_questions) != QUESTION_COUNT:
        raise QuizError("Quiz provider must return exactly five questions.")

    questions: list[QuizQuestion] = []
    for index, raw_question in enumerate(raw_questions, start=1):
        if not isinstance(raw_question, Mapping):
            raise QuizError("Each generated question must be a JSON object.")

        question = str(raw_question.get("question", "")).strip()
        answer_guide = str(raw_question.get("answer_guide", "")).strip()
        if not question or not answer_guide:
            raise QuizError("Each generated question needs question and answer_guide fields.")

        questions.append(
            QuizQuestion(
                question_id=index,
                question=question,
                answer_guide=answer_guide,
            )
        )

    return tuple(questions)


def grade_answers(
    *,
    questions: Sequence[QuizQuestion],
    answers: Sequence[str],
    provider: JsonProvider,
) -> tuple[GradedAnswer, ...]:
    """Grade developer quiz answers with a JSON LLM provider."""

    if len(questions) != QUESTION_COUNT or len(answers) != QUESTION_COUNT:
        raise QuizError("The quiz must contain exactly five questions and answers.")

    payload = provider(_grading_prompt(questions, answers))
    raw_grades = payload.get("graded_answers")
    if not isinstance(raw_grades, list) or len(raw_grades) != QUESTION_COUNT:
        raise QuizError("Quiz provider must return exactly five graded answers.")

    grades_by_id: dict[int, Mapping[str, Any]] = {}
    for raw_grade in raw_grades:
        if not isinstance(raw_grade, Mapping):
            raise QuizError("Each graded answer must be a JSON object.")
        question_id = int(raw_grade.get("id", 0))
        grades_by_id[question_id] = raw_grade

    graded_answers: list[GradedAnswer] = []
    for question, answer in zip(questions, answers, strict=True):
        raw_grade = grades_by_id.get(question.question_id)
        if raw_grade is None:
            raise QuizError(f"Missing grade for question {question.question_id}.")

        graded_answers.append(
            GradedAnswer(
                question_id=question.question_id,
                question=question.question,
                answer=answer.strip(),
                answer_guide=question.answer_guide,
                correct=bool(raw_grade.get("correct", False)),
                feedback=str(raw_grade.get("feedback", "")).strip(),
            )
        )

    return tuple(graded_answers)


def run_interactive_quiz(
    *,
    change_set: ChangeSet,
    settings: Settings,
    artifact_path: Path = DEFAULT_ARTIFACT_PATH,
    provider: JsonProvider | None = None,
    input_fn: InputFn = input,
    print_fn: PrintFn = print,
) -> int:
    """Run the local interactive quiz and write the result artifact."""

    if not change_set.relevant_files:
        print_fn("No quiz-relevant files changed; quiz artifact is not required.")
        return 0

    json_provider = provider or build_openai_json_provider(settings)
    questions = generate_questions(change_set, json_provider)
    answers: list[str] = []

    print_fn("Answer these five questions about the current diff.")
    print_fn("A score of 4 out of 5 is required before opening the PR.")
    for question in questions:
        print_fn("")
        print_fn(f"{question.question_id}. {question.question}")
        answers.append(input_fn("Answer: "))

    graded_answers = grade_answers(
        questions=questions,
        answers=answers,
        provider=json_provider,
    )
    payload = build_quiz_payload(
        change_set=change_set,
        graded_answers=graded_answers,
        model=settings.openai_model,
    )
    write_quiz_payload(payload, artifact_path)

    score = int(payload["score"])
    passed = bool(payload["passed"])
    print_fn("")
    print_fn(f"Quiz score: {score}/{QUESTION_COUNT}")
    print_fn(f"Wrote quiz artifact: {artifact_path}")
    if passed:
        print_fn("Quiz passed.")
        return 0

    print_fn("Quiz failed; review the diff and re-run the quiz.")
    return 1


def build_quiz_payload(
    *,
    change_set: ChangeSet,
    graded_answers: Sequence[GradedAnswer],
    model: str,
) -> dict[str, Any]:
    """Build a checksum-backed quiz artifact payload."""

    if len(graded_answers) != QUESTION_COUNT:
        raise QuizError("Quiz artifact must contain exactly five graded answers.")

    score = sum(1 for answer in graded_answers if answer.correct)
    payload: dict[str, Any] = {
        "artifact_version": ARTIFACT_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "base_ref": change_set.base_ref,
        "head_ref": change_set.head_ref,
        "base_sha": change_set.base_sha,
        "head_sha": change_set.head_sha,
        "merge_base_sha": change_set.merge_base_sha,
        "changed_files": list(change_set.changed_files),
        "relevant_files": list(change_set.relevant_files),
        "diff_hash": change_set.diff_hash,
        "file_list_hash": change_set.file_list_hash,
        "question_count": QUESTION_COUNT,
        "passing_score": PASSING_SCORE,
        "score": score,
        "passed": score >= PASSING_SCORE,
        "model": model,
        "answers": [
            {
                "id": answer.question_id,
                "question": answer.question,
                "answer": answer.answer,
                "answer_guide": answer.answer_guide,
                "correct": answer.correct,
                "feedback": answer.feedback,
            }
            for answer in graded_answers
        ],
    }
    payload["artifact_hash"] = artifact_hash(payload)
    return payload


def write_quiz_payload(payload: Mapping[str, Any], artifact_path: Path) -> None:
    """Write a quiz artifact as stable, reviewable JSON."""

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_quiz_artifact(
    *,
    artifact_path: Path = DEFAULT_ARTIFACT_PATH,
    base_ref: str,
    head_ref: str,
    repo_path: Path | str | None = None,
) -> QuizValidation:
    """Validate that a committed quiz artifact matches the current diff."""

    change_set = collect_change_set(base_ref=base_ref, head_ref=head_ref, repo_path=repo_path)
    if not change_set.relevant_files:
        return QuizValidation(valid=True, message="No quiz-relevant files changed.")

    if not artifact_path.exists():
        return QuizValidation(
            valid=False,
            message=f"Missing quiz artifact: {artifact_path}",
        )

    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return QuizValidation(valid=False, message=f"Invalid quiz artifact JSON: {exc}")

    if not isinstance(payload, Mapping):
        return QuizValidation(valid=False, message="Quiz artifact must be a JSON object.")

    return validate_quiz_payload(payload=payload, change_set=change_set)


def validate_quiz_payload(
    *,
    payload: Mapping[str, Any],
    change_set: ChangeSet,
) -> QuizValidation:
    """Validate a quiz artifact payload against a collected change set."""

    stored_hash = payload.get("artifact_hash")
    if not isinstance(stored_hash, str) or stored_hash != artifact_hash(payload):
        return QuizValidation(valid=False, message="Quiz artifact hash is invalid.")

    expected_values: tuple[tuple[str, Any], ...] = (
        ("artifact_version", ARTIFACT_VERSION),
        ("merge_base_sha", change_set.merge_base_sha),
        ("diff_hash", change_set.diff_hash),
        ("file_list_hash", change_set.file_list_hash),
        ("question_count", QUESTION_COUNT),
        ("passing_score", PASSING_SCORE),
    )
    for key, expected in expected_values:
        if payload.get(key) != expected:
            return QuizValidation(
                valid=False,
                message=f"Quiz artifact {key} is stale or invalid.",
            )

    if payload.get("relevant_files") != list(change_set.relevant_files):
        return QuizValidation(valid=False, message="Quiz artifact file list is stale.")

    answers = payload.get("answers")
    if not isinstance(answers, list) or len(answers) != QUESTION_COUNT:
        return QuizValidation(valid=False, message="Quiz artifact must contain five answers.")

    score = payload.get("score")
    if not isinstance(score, int) or score < PASSING_SCORE:
        return QuizValidation(valid=False, message="Quiz score is below 4 out of 5.")

    if payload.get("passed") is not True:
        return QuizValidation(valid=False, message="Quiz artifact is not marked as passed.")

    return QuizValidation(valid=True, message="Quiz artifact is valid.")


def artifact_hash(payload: Mapping[str, Any]) -> str:
    """Return the artifact checksum, excluding the checksum field itself."""

    hashable_payload = {key: value for key, value in payload.items() if key != "artifact_hash"}
    return _sha256_json(hashable_payload)


def build_openai_json_provider(settings: Settings) -> JsonProvider:
    """Build an OpenAI-backed JSON provider for quiz generation and grading."""

    if not settings.openai_api_key:
        raise QuizError("OPENAI_API_KEY is required to generate and grade a change quiz.")

    def call_openai(prompt: str) -> Mapping[str, Any]:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response: Any = client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )
        output_text = cast(str, response.output_text)
        return _parse_json_object(output_text)

    return call_openai


def _question_prompt(change_set: ChangeSet) -> str:
    files = "\n".join(f"- {path}" for path in change_set.relevant_files)
    return f"""
You generate comprehension quizzes for developers reviewing AI-assisted changes.

Create exactly {QUESTION_COUNT} short-answer questions about this git diff.
The questions must be answerable from the diff only and should test:
- what behavior changed
- why the change was made
- important tests or docs affected
    (but do not be too exhaustive about listing every single test or doc change)
- configuration or workflow impact
- risks, assumptions, or edge cases introduced by the change
    (but do not make the questions too difficult or nitpicky)

Return JSON only, with this shape:
{{
  "questions": [
    {{"question": "...", "answer_guide": "..."}}
  ]
}}

Changed files:
{files}

Diff:
{change_set.diff}
""".strip()


def _grading_prompt(questions: Sequence[QuizQuestion], answers: Sequence[str]) -> str:
    quiz_items = [
        {
            "id": question.question_id,
            "question": question.question,
            "answer_guide": question.answer_guide,
            "developer_answer": answer,
        }
        for question, answer in zip(questions, answers, strict=True)
    ]
    return f"""
Grade these developer answers for a change-understanding quiz.

Mark an answer correct only when it demonstrates practical understanding of the
diff-specific behavior, risk, or test/docs impact. Be fair about wording, but do
not give credit for vague answers that could apply to any change.
At the same time do not be too strict, and if the answer shows understanding
but misses some details, mark it correct but provide feedback on what was missed.
If the question is asking to list lots of details,
be lenient if the answer lists at least some of them,
but provide feedback on what was missed.

Return JSON only, with this shape:
{{
  "graded_answers": [
    {{"id": 1, "correct": true, "feedback": "..."}}
  ]
}}

Quiz items:
{json.dumps(quiz_items, indent=2)}
""".strip()


def _parse_json_object(text: str) -> Mapping[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:-1]).strip()

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise QuizError("LLM response did not contain a JSON object.") from None
        payload = json.loads(stripped[start : end + 1])

    if not isinstance(payload, Mapping):
        raise QuizError("LLM response must be a JSON object.")
    return payload


def _git(
    args: Sequence[str],
    repo_path: Path,
    *,
    strip: bool = True,
) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise QuizError(f"git {' '.join(args)} failed: {stderr}")

    return completed.stdout.strip() if strip else completed.stdout


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json(value: object) -> str:
    return _sha256_text(json.dumps(value, sort_keys=True, separators=(",", ":")))
