"""Change-understanding quiz tests."""

from __future__ import annotations

from typing import Any

from agentic_project_starter.quality.change_quiz import (
    PASSING_SCORE,
    ChangeSet,
    GradedAnswer,
    build_quiz_payload,
    filter_quiz_relevant_files,
    generate_questions,
    grade_answers,
    validate_quiz_payload,
)


def test_filter_quiz_relevant_files_ignores_generated_artifacts() -> None:
    paths = [
        "src/agentic_project_starter/cli/main.py",
        "docs/getting-started.md",
        "uv.lock",
        ".change-quiz/result.json",
        "src/__pycache__/main.pyc",
        "assets/demo.png",
    ]

    assert filter_quiz_relevant_files(paths) == (
        "src/agentic_project_starter/cli/main.py",
        "docs/getting-started.md",
    )


def test_quiz_payload_passes_at_four_out_of_five() -> None:
    change_set = _sample_change_set()
    payload = build_quiz_payload(
        change_set=change_set,
        graded_answers=_graded_answers(correct_count=PASSING_SCORE),
        model="fake-model",
    )

    validation = validate_quiz_payload(payload=payload, change_set=change_set)

    assert payload["score"] == 4
    assert payload["passed"] is True
    assert validation.valid is True


def test_quiz_payload_fails_below_four_out_of_five() -> None:
    change_set = _sample_change_set()
    payload = build_quiz_payload(
        change_set=change_set,
        graded_answers=_graded_answers(correct_count=3),
        model="fake-model",
    )

    validation = validate_quiz_payload(payload=payload, change_set=change_set)

    assert payload["score"] == 3
    assert payload["passed"] is False
    assert validation.valid is False
    assert validation.message == "Quiz score is below 4 out of 5."


def test_quiz_payload_rejects_stale_diff_hash() -> None:
    original = _sample_change_set(diff="diff --git a/app.py b/app.py\n+new behavior\n")
    current = _sample_change_set(diff="diff --git a/app.py b/app.py\n+newer behavior\n")
    payload = build_quiz_payload(
        change_set=original,
        graded_answers=_graded_answers(correct_count=5),
        model="fake-model",
    )

    validation = validate_quiz_payload(payload=payload, change_set=current)

    assert validation.valid is False
    assert validation.message == "Quiz artifact diff_hash is stale or invalid."


def test_quiz_payload_allows_artifact_commit_to_change_head_sha() -> None:
    original = _sample_change_set(head_sha="code-change-sha")
    current = _sample_change_set(head_sha="artifact-commit-sha")
    payload = build_quiz_payload(
        change_set=original,
        graded_answers=_graded_answers(correct_count=5),
        model="fake-model",
    )

    validation = validate_quiz_payload(payload=payload, change_set=current)

    assert validation.valid is True


def test_quiz_payload_rejects_tampered_checksum() -> None:
    change_set = _sample_change_set()
    payload = build_quiz_payload(
        change_set=change_set,
        graded_answers=_graded_answers(correct_count=4),
        model="fake-model",
    )
    payload["score"] = 5

    validation = validate_quiz_payload(payload=payload, change_set=change_set)

    assert validation.valid is False
    assert validation.message == "Quiz artifact hash is invalid."


def test_quiz_generation_and_grading_use_injected_provider() -> None:
    change_set = _sample_change_set()

    def provider(prompt: str) -> dict[str, Any]:
        if "Create exactly 5 short-answer questions" in prompt:
            return {
                "questions": [
                    {
                        "question": f"What changed in area {index}?",
                        "answer_guide": f"Explain area {index}.",
                    }
                    for index in range(1, 6)
                ]
            }

        return {
            "graded_answers": [
                {"id": index, "correct": index != 5, "feedback": "ok"} for index in range(1, 6)
            ]
        }

    questions = generate_questions(change_set, provider)
    grades = grade_answers(
        questions=questions,
        answers=["answer"] * 5,
        provider=provider,
    )

    assert len(questions) == 5
    assert sum(1 for grade in grades if grade.correct) == 4


def _sample_change_set(
    diff: str = "diff --git a/app.py b/app.py\n+new behavior\n",
    head_sha: str = "head-sha",
) -> ChangeSet:
    return ChangeSet(
        base_ref="origin/main",
        head_ref="HEAD",
        base_sha="base-sha",
        head_sha=head_sha,
        merge_base_sha="merge-base-sha",
        changed_files=("src/app.py", "uv.lock"),
        relevant_files=("src/app.py",),
        diff=diff,
    )


def _graded_answers(correct_count: int) -> tuple[GradedAnswer, ...]:
    return tuple(
        GradedAnswer(
            question_id=index,
            question=f"Question {index}?",
            answer=f"Answer {index}",
            answer_guide=f"Guide {index}",
            correct=index <= correct_count,
            feedback="feedback",
        )
        for index in range(1, 6)
    )
