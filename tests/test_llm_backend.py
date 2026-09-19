"""M2 T6 — the model interface (F3 AC-3.1 … AC-3.5).

No test calls a live model: the Claude Code backend is driven through a fake
subprocess runner, and every other test uses the recorded fake backend (F3 D2).
Tier: unit, with contract tests on the answer envelope.
"""
from __future__ import annotations

import json
import subprocess

import pytest

from sdd_compiler.errors import ExitCode, SddcError
from sdd_compiler.llm import CallBudget, FakeBackend, Question, get_backend
from sdd_compiler.llm.claude_code import ClaudeCodeBackend
from sdd_compiler.profile import AtomizerSettings

SCHEMA = {"type": "object", "properties": {"atoms": {"type": "array"}}, "required": ["atoms"]}
QUESTION = Question(kind="q-atom", schema_version="q-atom/1", schema=SCHEMA, prompt="Split this block.")


def headless_payload(structured, cost=0.0012):
    return json.dumps({
        "type": "result",
        "subtype": "success",
        "result": "done",
        "session_id": "s-1",
        "total_cost_usd": cost,
        "num_turns": 1,
        "duration_ms": 850,
        "usage": {
            "input_tokens": 1200, "output_tokens": 300,
            "cache_read_input_tokens": 900, "cache_creation_input_tokens": 0,
        },
        "structured_output": structured,
    })


class FakeProcess:
    """Stands in for a completed `claude -p` subprocess."""

    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


@pytest.fixture()
def spy(monkeypatch):
    """Capture the argv and environment the backend would run."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append({"argv": argv, "env": kwargs.get("env", {}), "stdin": kwargs.get("stdin")})
        return FakeProcess(stdout=headless_payload({"atoms": [{"kind": "requirement"}]}))

    monkeypatch.setattr("sdd_compiler.llm.claude_code.subprocess.run", fake_run)
    monkeypatch.setattr("sdd_compiler.llm.claude_code.shutil.which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(ClaudeCodeBackend, "_read_cli_version", lambda self: "2.1.300")
    return calls


# -- AC-3.1 the child environment and command line --------------------------

def test_ac_3_1_child_environment_and_argv(spy, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-not-be-passed")
    backend = ClaudeCodeBackend(model="haiku")
    backend.ask(QUESTION)

    argv, env = spy[0]["argv"], spy[0]["env"]
    assert argv[0] == "claude"
    assert "-p" in argv
    assert argv[argv.index("--model") + 1] == "haiku"
    assert argv[argv.index("--output-format") + 1] == "json"
    assert "--json-schema" in argv
    assert json.loads(argv[argv.index("--json-schema") + 1]) == SCHEMA
    assert "--bare" not in argv

    assert env["SDD_COMPILER_CHILD"] == "1"
    assert "ANTHROPIC_API_KEY" not in env


def test_ac_3_1_the_key_is_passed_only_when_the_profile_asks(spy, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-deliberate")
    ClaudeCodeBackend(model="haiku", pass_api_key=True).ask(QUESTION)
    assert spy[0]["env"]["ANTHROPIC_API_KEY"] == "sk-deliberate"


def test_thinking_is_off_by_default_for_closed_questions(spy, monkeypatch):
    """F3 D10: extended thinking made one Q-DESC call 25-35 s instead of ~5 s (rel01 S21)."""
    monkeypatch.setenv("MAX_THINKING_TOKENS", "8000")
    ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert spy[0]["env"]["MAX_THINKING_TOKENS"] == "0"


def test_thinking_is_left_to_claude_code_when_the_profile_turns_it_on(spy, monkeypatch):
    monkeypatch.delenv("MAX_THINKING_TOKENS", raising=False)
    ClaudeCodeBackend(model="haiku", thinking=True).ask(QUESTION)
    assert "MAX_THINKING_TOKENS" not in spy[0]["env"]


# -- AC-3.2 .env stays inside the API backend -------------------------------

def test_ac_3_2_the_claude_code_backend_never_reads_dotenv(spy, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("ANTHROPIC_API_KEY=sk-from-dotenv\n", encoding="utf-8")
    ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert "sk-from-dotenv" not in json.dumps(spy[0]["env"])


def test_ac_3_2_the_api_backend_reads_the_key_from_dotenv(tmp_path, monkeypatch):
    from sdd_compiler.llm.anthropic_api import read_api_key

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    (tmp_path / ".env").write_text("# a comment\nANTHROPIC_API_KEY=sk-from-dotenv\n", encoding="utf-8")
    assert read_api_key(tmp_path) == "sk-from-dotenv"


def test_ac_3_2_a_missing_key_is_a_backend_error(tmp_path, monkeypatch):
    from sdd_compiler.llm.anthropic_api import read_api_key

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(SddcError) as excinfo:
        read_api_key(tmp_path)
    assert excinfo.value.exit_code is ExitCode.BACKEND


# -- AC-3.3 what every call records -----------------------------------------

def test_ac_3_3_usage_backend_model_and_version_are_recorded(spy):
    answer = ClaudeCodeBackend(model="haiku").ask(QUESTION)

    assert answer.data == {"atoms": [{"kind": "requirement"}]}
    assert answer.backend == "claude-code"
    assert answer.model == "haiku"
    assert answer.cli_version == "2.1.300"
    assert answer.usage == {
        "input_tokens": 1200, "output_tokens": 300,
        "cache_read_tokens": 900, "cache_creation_tokens": 0,
    }
    assert answer.cost_usd == pytest.approx(0.0012)
    assert answer.duration_ms >= 0


def test_the_cli_version_is_read_once_per_backend(spy, monkeypatch):
    calls = []
    monkeypatch.setattr(ClaudeCodeBackend, "_read_cli_version",
                        lambda self: calls.append(1) or "2.1.300")
    backend = ClaudeCodeBackend(model="haiku")
    backend.ask(QUESTION)
    backend.ask(QUESTION)
    assert len(calls) == 1


# -- AC-3.4 the backend is not there ----------------------------------------

def test_ac_3_4_a_missing_claude_binary_is_exit_6(monkeypatch):
    monkeypatch.setattr("sdd_compiler.llm.claude_code.shutil.which", lambda _: None)
    with pytest.raises(SddcError) as excinfo:
        ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert excinfo.value.exit_code is ExitCode.BACKEND
    assert "claude" in str(excinfo.value)


def test_a_failed_call_is_exit_6_with_the_stderr(monkeypatch):
    monkeypatch.setattr("sdd_compiler.llm.claude_code.shutil.which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(ClaudeCodeBackend, "_read_cli_version", lambda self: "2.1.300")
    monkeypatch.setattr("sdd_compiler.llm.claude_code.subprocess.run",
                        lambda argv, **kw: FakeProcess(returncode=1, stderr="not authenticated"))
    with pytest.raises(SddcError) as excinfo:
        ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert excinfo.value.exit_code is ExitCode.BACKEND
    assert "not authenticated" in str(excinfo.value)


def test_a_usage_limit_is_reported_in_words_not_as_json(monkeypatch):
    """I-11: Claude Code reports a 429 in its JSON `result`; stderr may hold only a warning."""
    payload = json.dumps({"type": "result", "is_error": True, "api_error_status": 429,
                          "result": "You've hit your session limit · resets 11:30pm"})
    monkeypatch.setattr("sdd_compiler.llm.claude_code.shutil.which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(ClaudeCodeBackend, "_read_cli_version", lambda self: "2.1.300")
    monkeypatch.setattr("sdd_compiler.llm.claude_code.subprocess.run",
                        lambda argv, **kw: FakeProcess(returncode=1, stdout=payload,
                                                       stderr="Warning: no stdin data received"))
    with pytest.raises(SddcError) as excinfo:
        ClaudeCodeBackend(model="haiku").ask(QUESTION)
    message = str(excinfo.value)
    assert excinfo.value.exit_code is ExitCode.BACKEND
    assert "session limit" in message and "429" in message
    assert "{" not in message


def test_the_child_gets_no_stdin(spy):
    """Without it, `claude -p` waits 3 s for stdin on every call."""
    ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert spy[0]["stdin"] is subprocess.DEVNULL


def test_output_that_is_not_json_is_a_backend_error(monkeypatch):
    monkeypatch.setattr("sdd_compiler.llm.claude_code.shutil.which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(ClaudeCodeBackend, "_read_cli_version", lambda self: "2.1.300")
    monkeypatch.setattr("sdd_compiler.llm.claude_code.subprocess.run",
                        lambda argv, **kw: FakeProcess(stdout="Hello, I am a chatty model"))
    with pytest.raises(SddcError) as excinfo:
        ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert excinfo.value.exit_code is ExitCode.BACKEND


def test_a_missing_structured_output_is_a_backend_error(monkeypatch):
    monkeypatch.setattr("sdd_compiler.llm.claude_code.shutil.which", lambda _: "/usr/bin/claude")
    monkeypatch.setattr(ClaudeCodeBackend, "_read_cli_version", lambda self: "2.1.300")
    payload = json.dumps({"type": "result", "result": "text only", "usage": {}})
    monkeypatch.setattr("sdd_compiler.llm.claude_code.subprocess.run",
                        lambda argv, **kw: FakeProcess(stdout=payload))
    with pytest.raises(SddcError) as excinfo:
        ClaudeCodeBackend(model="haiku").ask(QUESTION)
    assert "structured_output" in str(excinfo.value)


# -- AC-3.5 the call cap ----------------------------------------------------

def test_ac_3_5_the_budget_stops_the_run_at_the_cap():
    budget = CallBudget(max_calls=2)
    backend = FakeBackend([{"atoms": []}, {"atoms": []}, {"atoms": []}], budget=budget)
    backend.ask(QUESTION)
    backend.ask(QUESTION)
    with pytest.raises(SddcError) as excinfo:
        backend.ask(QUESTION)
    assert excinfo.value.exit_code is ExitCode.CALL_CAP
    assert budget.used == 2


def test_the_budget_is_shared_between_phases():
    """F6 D5 — atomization and pair judging spend from one pocket."""
    budget = CallBudget(max_calls=3)
    atomizer = FakeBackend([{"atoms": []}] * 2, budget=budget)
    judge = FakeBackend([{"relation": "none"}] * 2, budget=budget)
    atomizer.ask(QUESTION)
    judge.ask(QUESTION)
    atomizer.ask(QUESTION)
    assert budget.remaining == 0


# -- the fake backend itself ------------------------------------------------

def test_the_fake_backend_records_what_it_was_asked():
    backend = FakeBackend([{"atoms": [1]}])
    answer = backend.ask(QUESTION)
    assert answer.data == {"atoms": [1]}
    assert answer.backend == "fake"
    assert backend.asked[0].kind == "q-atom"


def test_the_fake_backend_runs_out_loudly():
    backend = FakeBackend([])
    with pytest.raises(AssertionError):
        backend.ask(QUESTION)


def test_get_backend_picks_from_the_profile():
    settings = AtomizerSettings(backend="claude-code", model="haiku")
    assert isinstance(get_backend(settings), ClaudeCodeBackend)
