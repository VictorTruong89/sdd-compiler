"""F1 CT-1.4 — the project profile: what counts as a spec source, and how.

The profile is the only hand-edited file in `.sdd/`. It is validated strictly:
an unknown key is a defect, not a hint, because a misspelled setting that is
silently ignored looks exactly like a setting that does not work.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

from .errors import ExitCode, SddcError

STORE_DIR = ".sdd"
PROFILE_NAME = "profile.yaml"

BACKENDS = ("claude-code", "anthropic-api")

#: F3 CT-3.4 adds the atomizer settings and the weak-word lexicon.
DEFAULT_ATOMIZER: dict[str, Any] = {
    "backend": "claude-code",
    "model": "haiku",
    "pass_api_key": False,
    "max_calls_per_run": 200,
    "timeout_s": 120,
    "thinking": False,
}

#: F5 CT-5.2 — retrieval settings. Starting values to tune with measurement (F5 D6).
DEFAULT_RETRIEVAL: dict[str, Any] = {
    "max_pairs_per_node": 10,
    "min_score": 1.0,
    "min_shared_keywords": 2,
}

#: F6 CT-6.3 — the check phase.
DEFAULT_CONFLICTS: dict[str, Any] = {
    "judge_ambiguous": True,
    "subsumption_conflict_only_when_differing": True,
}

DEFAULT_WEAK_WORDS = [
    "fast", "quickly", "appropriate", "user-friendly", "as needed", "etc", "robust", "simple",
]

DEFAULT_PROFILE: dict[str, Any] = {
    "spec_globs": ["sdd/specs/**/*.md"],
    "exclude_globs": ["sdd/specs/_templates/**"],
    "include_code_blocks": False,
    "atomizer": dict(DEFAULT_ATOMIZER),
    "retrieval": dict(DEFAULT_RETRIEVAL),
    "conflicts": dict(DEFAULT_CONFLICTS),
    "weak_words": list(DEFAULT_WEAK_WORDS),
    "layers": {},
}

_TEMPLATE = """\
# SDD Compiler profile (F1 CT-1.4) — the only hand-edited file in .sdd/
spec_globs: {spec_globs}
exclude_globs: {exclude_globs}

# Fenced code blocks are stored but not atomized unless this is true.
include_code_blocks: {include_code_blocks}

# Read by the atomizer (F3), recorded here so a run is reproducible.
atomizer:
  backend: {backend}   # claude-code | anthropic-api
  model: {model}
  pass_api_key: false        # keep ANTHROPIC_API_KEY out of headless calls
  max_calls_per_run: {max_calls}   # one budget, shared by atomizing and judging
  timeout_s: {timeout}
  thinking: false            # extended thinking; off for closed questions (F3 D10)

# Read by retrieval (F5 CT-5.2): how many candidate pairs a node may propose, the
# score a pair must reach, and how many keywords count as shared.
retrieval:
  max_pairs_per_node: {max_pairs_per_node}
  min_score: {min_score}
  min_shared_keywords: {min_shared_keywords}

# Read by the check phase (F6 CT-6.3): whether an ambiguous node is judged at all,
# and whether a subsumption is a conflict only when the two claims differ (F6 D2).
conflicts:
  judge_ambiguous: {judge_ambiguous}
  subsumption_conflict_only_when_differing: {subsumption_conflict_only_when_differing}

# Words that suggest a vague claim (F3 guard G6).
weak_words: {weak_words}

# Layer display names and section-heading hints (F2 §4.2). The layers themselves
# and their meanings are fixed; e.g.  L1: {{display: Behaviour, hints: ["## Behaviour"]}}
layers: {{}}
"""


@dataclass(frozen=True)
class AtomizerSettings:
    backend: str
    model: str
    pass_api_key: bool = False
    max_calls_per_run: int = 200
    timeout_s: int = 120
    thinking: bool = False


@dataclass(frozen=True)
class RetrievalSettings:
    """F5 CT-5.2."""

    max_pairs_per_node: int = 10
    min_score: float = 1.0
    min_shared_keywords: int = 2


@dataclass(frozen=True)
class ConflictSettings:
    """F6 CT-6.3."""

    judge_ambiguous: bool = True
    subsumption_conflict_only_when_differing: bool = True


@dataclass(frozen=True)
class Profile:
    spec_globs: tuple[str, ...]
    exclude_globs: tuple[str, ...]
    include_code_blocks: bool
    atomizer: AtomizerSettings
    retrieval: RetrievalSettings = field(default_factory=RetrievalSettings)
    conflicts: ConflictSettings = field(default_factory=ConflictSettings)
    weak_words: tuple[str, ...] = ()
    layers: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)


def render_default_profile() -> str:
    """The text `sddc init` writes. It must load back as DEFAULT_PROFILE."""
    return _TEMPLATE.format(
        spec_globs=DEFAULT_PROFILE["spec_globs"],
        exclude_globs=DEFAULT_PROFILE["exclude_globs"],
        include_code_blocks=str(DEFAULT_PROFILE["include_code_blocks"]).lower(),
        backend=DEFAULT_ATOMIZER["backend"],
        model=DEFAULT_ATOMIZER["model"],
        max_calls=DEFAULT_ATOMIZER["max_calls_per_run"],
        timeout=DEFAULT_ATOMIZER["timeout_s"],
        weak_words=DEFAULT_WEAK_WORDS,
        **DEFAULT_RETRIEVAL,
        **{key: str(value).lower() for key, value in DEFAULT_CONFLICTS.items()},
    )


def profile_path(root: Path) -> Path:
    return Path(root) / STORE_DIR / PROFILE_NAME


def load_profile(root: Path) -> Profile:
    """Read and validate `<root>/.sdd/profile.yaml` (AC-1.24 when it is missing)."""
    path = profile_path(root)
    if not path.exists():
        raise SddcError(
            f"no SDD Compiler store at {Path(root) / STORE_DIR} — run `sddc init` first",
            ExitCode.STORE,
        )
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise SddcError(f"{path.name} is not valid YAML: {exc}", ExitCode.INPUT) from exc
    except UnicodeDecodeError as exc:
        raise SddcError(f"{path.name} is not valid UTF-8", ExitCode.INPUT) from exc
    return parse_profile(raw, source=path.name)


def parse_profile(raw: Any, source: str = PROFILE_NAME) -> Profile:
    if not isinstance(raw, Mapping):
        raise SddcError(f"{source} must be a mapping of settings", ExitCode.INPUT)

    unknown = sorted(set(raw) - set(DEFAULT_PROFILE))
    if unknown:
        raise SddcError(
            f"{source}: unknown key(s) {', '.join(unknown)}; expected one of "
            f"{', '.join(sorted(DEFAULT_PROFILE))}",
            ExitCode.INPUT,
        )

    spec_globs = _globs(raw.get("spec_globs", DEFAULT_PROFILE["spec_globs"]), "spec_globs", source)
    exclude_globs = _globs(
        raw.get("exclude_globs", DEFAULT_PROFILE["exclude_globs"]),
        "exclude_globs",
        source,
        allow_empty=True,
    )

    include_code_blocks = raw.get("include_code_blocks", DEFAULT_PROFILE["include_code_blocks"])
    if not isinstance(include_code_blocks, bool):
        raise SddcError(
            f"{source}: include_code_blocks must be true or false, got "
            f"{include_code_blocks!r}",
            ExitCode.INPUT,
        )

    weak_words = raw.get("weak_words", DEFAULT_WEAK_WORDS)
    if not isinstance(weak_words, list) or not all(isinstance(word, str) for word in weak_words):
        raise SddcError(f"{source}: weak_words must be a list of strings", ExitCode.INPUT)

    return Profile(
        spec_globs=spec_globs,
        exclude_globs=exclude_globs,
        include_code_blocks=include_code_blocks,
        atomizer=_atomizer(raw.get("atomizer", DEFAULT_ATOMIZER), source),
        retrieval=_retrieval(raw.get("retrieval", DEFAULT_RETRIEVAL), source),
        conflicts=_conflicts(raw.get("conflicts", DEFAULT_CONFLICTS), source),
        weak_words=tuple(word.lower() for word in weak_words),
        layers=_layers(raw.get("layers", {}), source),
    )


def _retrieval(value: Any, source: str) -> RetrievalSettings:
    """F5 CT-5.2 — validated as strictly as the rest: a misspelled setting is a defect."""
    if not isinstance(value, Mapping):
        raise SddcError(f"{source}: retrieval must be a mapping", ExitCode.INPUT)
    unknown = sorted(set(value) - set(DEFAULT_RETRIEVAL))
    if unknown:
        raise SddcError(f"{source}: retrieval has unknown key(s) {', '.join(unknown)}", ExitCode.INPUT)
    settings = {**DEFAULT_RETRIEVAL, **value}
    for key in ("max_pairs_per_node", "min_shared_keywords"):
        if not isinstance(settings[key], int) or isinstance(settings[key], bool) or settings[key] < 1:
            raise SddcError(f"{source}: retrieval.{key} must be a whole number ≥ 1", ExitCode.INPUT)
    if not isinstance(settings["min_score"], (int, float)) or isinstance(settings["min_score"], bool) \
            or settings["min_score"] < 0:
        raise SddcError(f"{source}: retrieval.min_score must be a number ≥ 0", ExitCode.INPUT)
    return RetrievalSettings(max_pairs_per_node=settings["max_pairs_per_node"],
                             min_score=float(settings["min_score"]),
                             min_shared_keywords=settings["min_shared_keywords"])


def _conflicts(value: Any, source: str) -> ConflictSettings:
    """F6 CT-6.3 — two switches, both booleans."""
    if not isinstance(value, Mapping):
        raise SddcError(f"{source}: conflicts must be a mapping", ExitCode.INPUT)
    unknown = sorted(set(value) - set(DEFAULT_CONFLICTS))
    if unknown:
        raise SddcError(f"{source}: conflicts has unknown key(s) {', '.join(unknown)}", ExitCode.INPUT)
    settings = {**DEFAULT_CONFLICTS, **value}
    for key, setting in settings.items():
        if not isinstance(setting, bool):
            raise SddcError(f"{source}: conflicts.{key} must be true or false", ExitCode.INPUT)
    return ConflictSettings(**settings)


def _layers(value: Any, source: str) -> dict[str, dict[str, Any]]:
    """F2 AC-2.22 — display names and hints load; adding or redefining a layer fails."""
    from .model.layers import LAYERS, PROFILE_LAYER_KEYS

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise SddcError(f"{source}: layers must be a mapping of layer id to settings", ExitCode.INPUT)
    layers: dict[str, dict[str, Any]] = {}
    for layer, settings in value.items():
        if layer not in LAYERS:
            raise SddcError(
                f"{source}: layers: {layer!r} is not a layer; the layers are fixed "
                f"({', '.join(LAYERS)}) and a profile may only rename them",
                ExitCode.INPUT,
            )
        if not isinstance(settings, Mapping):
            raise SddcError(f"{source}: layers.{layer} must be a mapping", ExitCode.INPUT)
        extra = sorted(set(settings) - set(PROFILE_LAYER_KEYS))
        if extra:
            raise SddcError(
                f"{source}: layers.{layer}: {', '.join(extra)} cannot be set; a layer's meaning "
                f"is fixed, and a profile may set only {', '.join(PROFILE_LAYER_KEYS)}",
                ExitCode.INPUT,
            )
        display = settings.get("display")
        hints = settings.get("hints", [])
        if display is not None and not isinstance(display, str):
            raise SddcError(f"{source}: layers.{layer}.display must be a string", ExitCode.INPUT)
        if not isinstance(hints, list) or not all(isinstance(h, str) for h in hints):
            raise SddcError(f"{source}: layers.{layer}.hints must be a list of strings", ExitCode.INPUT)
        layers[layer] = {"display": display, "hints": list(hints)}
    return layers


def _globs(value: Any, field: str, source: str, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SddcError(f"{source}: {field} must be a list of glob strings", ExitCode.INPUT)
    if not value and not allow_empty:
        raise SddcError(f"{source}: {field} must name at least one glob", ExitCode.INPUT)
    return tuple(value)


def _atomizer(value: Any, source: str) -> AtomizerSettings:
    if not isinstance(value, Mapping):
        raise SddcError(f"{source}: atomizer must be a mapping", ExitCode.INPUT)
    unknown = sorted(set(value) - set(DEFAULT_ATOMIZER))
    if unknown:
        raise SddcError(
            f"{source}: atomizer has unknown key(s) {', '.join(unknown)}", ExitCode.INPUT
        )
    backend = value.get("backend", DEFAULT_ATOMIZER["backend"])
    model = value.get("model", DEFAULT_ATOMIZER["model"])
    if backend not in BACKENDS:
        raise SddcError(
            f"{source}: atomizer.backend must be one of {', '.join(BACKENDS)}, got {backend!r}",
            ExitCode.INPUT,
        )
    if not isinstance(model, str) or not model:
        raise SddcError(f"{source}: atomizer.model must be a non-empty string", ExitCode.INPUT)
    pass_api_key = value.get("pass_api_key", DEFAULT_ATOMIZER["pass_api_key"])
    if not isinstance(pass_api_key, bool):
        raise SddcError(f"{source}: atomizer.pass_api_key must be true or false", ExitCode.INPUT)
    thinking = value.get("thinking", DEFAULT_ATOMIZER["thinking"])
    if not isinstance(thinking, bool):
        raise SddcError(f"{source}: atomizer.thinking must be true or false", ExitCode.INPUT)
    numbers = {}
    for field_name in ("max_calls_per_run", "timeout_s"):
        number = value.get(field_name, DEFAULT_ATOMIZER[field_name])
        if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
            raise SddcError(
                f"{source}: atomizer.{field_name} must be a positive integer", ExitCode.INPUT
            )
        numbers[field_name] = number
    return AtomizerSettings(
        backend=backend, model=model, pass_api_key=pass_api_key, thinking=thinking, **numbers
    )
