"""CLI smoke tests."""

import pytest

from agentic_project_starter.cli.main import main
from agentic_project_starter.quality.change_quiz import QuizValidation


def test_doctor_command(capsys) -> None:
    main(["doctor"])

    captured = capsys.readouterr()

    assert "coordinator" in captured.out
    assert "chatkit" in captured.out


def test_run_agent_command(capsys) -> None:
    main(["run-agent", "--agent-name", "coordinator", "--prompt", "Draft a starter workflow"])

    captured = capsys.readouterr()

    assert "dry-run" in captured.out


def test_run_etl_command(capsys) -> None:
    main(["run-etl", "--job-name", "bootstrap_pipeline"])

    captured = capsys.readouterr()

    assert "bootstrap_pipeline" in captured.out


def test_quiz_changes_verify_command(monkeypatch, capsys) -> None:
    def fake_validate_quiz_artifact(**kwargs) -> QuizValidation:
        return QuizValidation(valid=True, message="Quiz artifact is valid.")

    monkeypatch.setattr(
        "agentic_project_starter.cli.main.validate_quiz_artifact",
        fake_validate_quiz_artifact,
    )

    main(["quiz-changes", "--verify", "--base", "origin/main", "--head", "HEAD"])

    captured = capsys.readouterr()

    assert "Quiz artifact is valid." in captured.out


def test_quiz_changes_verify_failure_exits(monkeypatch) -> None:
    def fake_validate_quiz_artifact(**kwargs) -> QuizValidation:
        return QuizValidation(valid=False, message="Missing quiz artifact")

    monkeypatch.setattr(
        "agentic_project_starter.cli.main.validate_quiz_artifact",
        fake_validate_quiz_artifact,
    )

    with pytest.raises(SystemExit) as exc:
        main(["quiz-changes", "--verify"])

    assert exc.value.code == 1
