"""F7 §4.2, §4.9 — `sddc export`: check, resolve, render in memory, check coverage, write whole."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import ExitCode, SddcError
from ..profile import STORE_DIR, load_profile
from ..store.graph import check_store
from . import packs as packs_module
from .files import build_meta, checklist, map_md, pending_blocks
from .gate import blocking
from .model import Model, load_model
from .packs import Packs
from .sources import check_sources

META_NAME = "export.meta.json"


@dataclass
class ExportResult:
    out: Path
    meta: dict[str, Any]


def export(root: Path, out: Path | None = None, allow_open: bool = False) -> ExportResult:
    root = Path(root).resolve()
    store = root / STORE_DIR
    profile = load_profile(root)
    problems = check_store(store)
    if problems:
        raise SddcError("the store failed its checks:\n  " + "\n  ".join(problems), ExitCode.STORE)
    check_sources(root, profile, raise_on_problem=True)
    model = load_model(root)

    stuck = blocking(model)
    if stuck and not allow_open:
        shown = [f"{c['id']}: {' vs '.join(c['members'])}" for c in stuck[:20]]
        more = f"\n  … and {len(stuck) - 20} more" if len(stuck) > 20 else ""
        raise SddcError(f"{len(stuck)} contradiction(s) have no current human verdict; judge them with "
                        f"`sddc conflicts judge CF-… --verdict real|false`, or export with "
                        f"--allow-open:\n  " + "\n  ".join(shown) + more, ExitCode.CONFLICTS)

    out = Path(out).resolve() if out else store / "export"
    _check_out(out)

    packs = packs_module.build_packs(model, allow_open=allow_open)
    _check_coverage(model, packs)
    checklist_text, checklist_items = checklist(model, packs)
    pending, no_node = pending_blocks(model, packs)
    meta = build_meta(model, packs, checklist_items, allow_open, pending, no_node)
    files = {**packs.files, "CHECKLIST.md": checklist_text,
             "MAP.md": map_md(model, packs, meta, pending, allow_open),
             META_NAME: json.dumps(meta, ensure_ascii=False, indent=1) + "\n"}
    try:
        _write_whole(out, files)
    except OSError as error:
        raise SddcError(f"cannot write the export to {out}: {error}; the previous export, if any, "
                        f"is untouched", ExitCode.STORE) from error
    return ExportResult(out, meta)


def _check_out(out: Path) -> None:
    """D10 — never delete a directory the export did not write."""
    if out.exists() and (not out.is_dir() or (any(out.iterdir()) and not (out / META_NAME).exists())):
        raise SddcError(f"{out} exists and is not an export (no {META_NAME}); the export replaces its "
                        f"output whole, so it will not touch it — choose another --out", ExitCode.USAGE)


def _check_coverage(model: Model, packs: Packs) -> None:
    """§4.9 step 2 — every kept block's text is in its home pack, in source order."""
    assert model.units is not None
    units = [model.units.foundation] if model.units.foundation else []
    units += model.units.units
    missing = []
    for unit in units:
        text = packs.files[f"packs/{packs.names[unit.key]}"]
        start = text.find("\n## Text\n")
        end = text.find("\n## Claims to implement\n")
        section, at = text[start:end] if 0 <= start < end else "", 0      # the lists echo node text
        for block_id in unit.block_ids:
            found = section.find(model.blocks[block_id]["text"], at)
            if found < 0:
                missing.append(block_id)
            else:
                at = found + 1
    expected = {i for unit in units for i in unit.block_ids}
    missing += sorted(expected - set(packs.rendered_blocks))
    if missing:
        raise SddcError("coverage check failed: no home pack holds " + ", ".join(sorted(set(missing)))
                        + " verbatim — a defect in the export, nothing was written", ExitCode.STORE)


def _write_whole(out: Path, files: dict[str, str]) -> None:
    """§4.9 step 3 — write a sibling directory, then replace `out`; a failure leaves the old one."""
    new = out.with_name(out.name + ".new")
    old = out.with_name(out.name + ".old")
    for leftover in (new, old):
        if leftover.exists():
            shutil.rmtree(leftover)
    try:
        for name, text in files.items():
            path = new / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        if out.exists():
            out.rename(old)
        try:
            new.rename(out)
        except BaseException:
            if old.exists():
                old.rename(out)
            raise
    except BaseException:
        shutil.rmtree(new, ignore_errors=True)
        raise
    if old.exists():
        shutil.rmtree(old)
