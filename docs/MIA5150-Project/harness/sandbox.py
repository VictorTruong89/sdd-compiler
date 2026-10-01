"""A bubblewrap sandbox for one agent run, or for scoring its code.

Inside, the run sees: the system read-only, a fresh home, its own working directory read-write, and
the network (the model is hosted). It does not see /home (the repository, ~/sddc-runs, the hidden
tests) or the host's /tmp. The environment is cleared, so ANTHROPIC_API_KEY never reaches it.

Claude Code's login is the one exception to "nothing from home": the credentials file is bind-mounted
read-write so a token refresh works. The agent can read it — as any process it starts could anyway.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

HOME_IN = "/home/agent"
WORK_IN = "/home/work"
CLAUDE_IN = "/home/bin/claude"


def claude_binary() -> Path:
    found = shutil.which("claude")
    if not found:
        raise SystemExit("harness: `claude` is not on PATH")
    return Path(found).resolve()


def bwrap_argv(run_dir: Path, work_dir: Path, with_claude: bool = True,
               extra_ro: dict[str, str] | None = None) -> list[str]:
    """The bwrap prefix. `run_dir/home` becomes the fresh home; `work_dir` is mounted at /home/work."""
    home = run_dir / "home"
    (home / ".claude").mkdir(parents=True, exist_ok=True)
    config = home / ".claude.json"
    if not config.exists():
        config.write_text(json.dumps({"hasCompletedOnboarding": True}), encoding="utf-8")
    argv = [
        "bwrap", "--die-with-parent", "--unshare-pid", "--unshare-ipc", "--unshare-uts",
        "--ro-bind", "/", "/",
        "--tmpfs", "/home", "--tmpfs", "/tmp", "--tmpfs", "/root",
        "--dev", "/dev", "--proc", "/proc",
        "--bind", str(home), HOME_IN,
        "--bind", str(work_dir), WORK_IN,
        "--chdir", WORK_IN,
        "--clearenv",
        "--setenv", "HOME", HOME_IN,
        "--setenv", "PATH", "/home/bin:/usr/local/bin:/usr/bin:/bin",
        "--setenv", "LANG", os.environ.get("LANG", "C.UTF-8"),
        "--setenv", "TERM", "dumb",
        "--setenv", "DISABLE_AUTOUPDATER", "1",
    ]
    if with_claude:
        credentials = Path.home() / ".claude" / ".credentials.json"
        if not credentials.exists():
            raise SystemExit(f"harness: no Claude Code login at {credentials}")
        argv += ["--ro-bind", str(claude_binary()), CLAUDE_IN,
                 "--bind", str(credentials), f"{HOME_IN}/.claude/.credentials.json"]
    for source, target in (extra_ro or {}).items():
        argv += ["--ro-bind", source, target]
    return argv
