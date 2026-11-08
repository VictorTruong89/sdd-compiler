"""Make one alternative copy of a built prosecheck per candidate, for the footprint runs and the probe check.

    python3 notes/sides.py work/base-app work/sides [C01 ...]        (from the trial folder)

Round 21 (new for case016; the method of ../r20-zero2repo-case010-gaps/notes/sides.py and of round 19's).
Two kinds of candidate share one list:
  - C.. **conflict** candidates: the original spec states side A (the upstream behaviour); a planted
    sentence will state side B. The copy builds side B.
  - G.. **gap** candidates: a stated fact that may be removed from the spec. The copy builds a plausible
    alternative an agent could invent once the fact is gone.
The base build (round 13c `sonnet-case016-export-2`, 388 / 388 on round 13c's task) takes the upstream
value on every candidate; each patch is the smallest change that moves that one behaviour. Every
anchor must occur exactly once, so a patch never applies silently to the wrong place. Writes
work/sides/<id>/ (a full copy) and work/sides/<id>.tgz, plus work/sides/BASE.tgz. Written from the
spec and the base code only, never from the hidden tests (only their names were read).
"""
import shutil
import sys
import tarfile
from pathlib import Path

D = "scripts/detect.py"
COM, GUARD, TRK, STATS, ACT = ("hooks/prosecheck-common.js", "hooks/prosecheck-guard.js", "hooks/prosecheck-tracker.js",
                               "hooks/prosecheck-stats.js", "hooks/prosecheck-activate.js")

PATCHES = {
    # ---- conflicts: side B built
    # C01 hedge stacking (54) is writing advice (A) -> moves the score (B)
    "C01": [(D, 'col.add("54_hedging", 54, c54, s54, moving=False)', 'col.add("54_hedging", 54, c54, s54)')],
    # C02 opener repetition (42) advice (A) -> moves the score (B)
    "C02": [(D, 'col.add("42_opener_repetition", 42, c42, s42, moving=False)', 'col.add("42_opener_repetition", 42, c42, s42)')],
    # C03 trailing whitespace (68) advice (A) -> moves the score (B)
    "C03": [(D, 'col.add("68_trailing_whitespace", 68, c68, ["stray whitespace"] if c68 else [], moving=False)',
             'col.add("68_trailing_whitespace", 68, c68, ["stray whitespace"] if c68 else [])')],
    # C04 confidence high at 300 words (A) -> at 250 words (B)
    "C04": [(D, 'elif nwords < 120 or (nwords < 300 and nfam == 1):', 'elif nwords < 120 or (nwords < 250 and nfam == 1):'),
            (D, '    elif nwords < 300:\n        conf, reason = "moderate"', '    elif nwords < 250:\n        conf, reason = "moderate"')],
    # C05 interval needs at least four sentences (A) -> three (B)
    "C05": [(D, "        if len(sents) >= 4:\n            lo, hi = bootstrap", "        if len(sents) >= 3:\n            lo, hi = bootstrap")],
    # C06 single decisive family takes the 45 floor only above low confidence (A) -> at any confidence (B)
    "C06": [(D, '    elif len(dec) == 1 and nfam == 1 and conf in ("moderate", "high"):', '    elif len(dec) == 1:')],
    # C07 unknown option exits 2 (A) -> 1, the same as the other failures (B)
    "C07": [(D, 'return err_exit("unknown option: %s (try --help)" % a, 2)', 'return err_exit("unknown option: %s (try --help)" % a, 1)')],
    # C08 two file operands: the first is scanned (A) -> the last (B)
    "C08": [(D, 'sys.stderr.write("prosecheck: only the first file was scanned: %s\\n" % operands[0])\n            text, line_paras = extract_file(operands[0])',
             'sys.stderr.write("prosecheck: only the last file was scanned: %s\\n" % operands[-1])\n            text, line_paras = extract_file(operands[-1])')],
    # C09 help prints usage on standard output (A) -> on standard error (B)
    "C09": [(D, '            sys.stdout.buffer.write(USAGE.encode("utf-8"))\n            sys.stdout.flush()\n            return 0',
             '            sys.stderr.write(USAGE)\n            sys.stderr.flush()\n            return 0')],
    # C10 runs of two or more blockquote lines generate no findings (A) -> blockquotes are scanned (B)
    "C10": [(D, "            if j - i >= 2:\n                for k in range(i, j):", "            if False:\n                for k in range(i, j):")],
    # C11 transition clusters need two or more opening transitions in a paragraph (A) -> one is enough (B)
    "C11": [(D, "        if len(lst) >= 2:\n            c37 += len(lst)", "        if len(lst) >= 1:\n            c37 += len(lst)")],
    # C12 false ranges only the rhetorical sweep (A) -> a numeric "from N to M" span too (B)
    "C12": [(D, "FALSE_RANGE = [\n", "FALSE_RANGE = [\n    P(r\"\\bfrom \\d+ to \\d+\\b\"),\n")],
    # C13 utm_source fires only for the seven AI hosts (A) -> any value (B)
    "C13": [(D, "        if host in UTM_HOSTS:", "        if host:")],
    # C14 tailing negation only the stock "no ..." tails (A) -> any short "no <word>" tail (B)
    "C14": [(D, 'TAIL_NEG = P(r",\\s*no (?:wasted motion|guessing|waste|hassle|fluff|stress|jargon)\\b")',
             'TAIL_NEG = P(r",\\s*no \\w+")')],
    # C15 load-bearing no-break spaces are kept (A) -> every no-break space is normalized (B)
    "C15": [(D, '    if c not in "\u00a0\u202f":\n        return False', '    if True:\n        return False')],
    # C16 hard-break spaces are collapsed (A) -> two trailing spaces of a markdown hard break are kept (B)
    "C16": [(D, '    lines = [ln.rstrip(" \\t") if not ln.endswith("\\r") else ln[:-1].rstrip(" \\t") + "\\r" for ln in lines]',
             '    lines = [ln if (ln.endswith("  ") and not ln.endswith("   ") and ln.strip()) else '
             '(ln.rstrip(" \\t") if not ln.endswith("\\r") else ln[:-1].rstrip(" \\t") + "\\r") for ln in lines]')],
    # C17 apply_patch scores at most 16 distinct paths (A) -> at most 10 (B)
    "C17": [(GUARD, "return patchPaths(body).slice(0, 16);", "return patchPaths(body).slice(0, 10);"),
            (GUARD, "for (const p of extractPaths(ev).slice(0, 16)) {", "for (const p of extractPaths(ev).slice(0, 10)) {")],
    # C18 ledger keeps the newest 20 records (A) -> 50 (B)
    "C18": [(COM, "const keep = rows.slice(-20);", "const keep = rows.slice(-50);")],
    # C19 ledger kept up to seven days (A) -> one day (B)
    "C19": [(COM, "const LEDGER_MAX_AGE_MS = 7 * 24 * 3600 * 1000;", "const LEDGER_MAX_AGE_MS = 1 * 24 * 3600 * 1000;")],
    # C20 environment level applies only when nothing valid is stored (A) -> overrides the stored level (B)
    "C20": [(COM, "  return readFlag() || envDefault() || 'full';", "  return envDefault() || readFlag() || 'full';")],
    # C21 stop phrases only as the entire prompt (A) -> anywhere in the prompt (B)
    "C21": [(TRK, "if (/^(stop prosecheck|prosecheck off)$/i.test(trimmed)) {", "if (/(stop prosecheck|prosecheck off)/i.test(trimmed)) {")],
    # C22 session-prose score when the slice is longer than 200 characters (A) -> 500 (B)
    "C22": [(STATS, "if (trimmed.length > 200) {", "if (trimmed.length > 500) {")],
    # C23 a named transcript wins over a newer one (A) -> stats always reads the newest (B)
    "C23": [(STATS, "let file = typeof transcriptPath === 'string' && transcriptPath ? transcriptPath : newestTranscript();",
             "let file = newestTranscript() || (typeof transcriptPath === 'string' && transcriptPath ? transcriptPath : null);")],
    # C25 tailing-negation form of 17 moves the score (A) -> writing advice (B)
    "C25": [(D, 'col.add("17_tailing_negation", 17, c, s, label="tailing negations (no fluff, no waste)")',
             'col.add("17_tailing_negation", 17, c, s, moving=False, label="tailing negations (no fluff, no waste)")')],
    # C26 em-dash overuse (58) advice (A) -> moves the score (B)
    "C26": [(D, 'col.add("58_em_dashes", 58, c58, ["em dashes: %d" % c58] if c58 else [], moving=False)',
             'col.add("58_em_dashes", 58, c58, ["em dashes: %d" % c58] if c58 else [])')],

    # ---- gaps: an alternative an agent could invent once the fact is removed
    # G01 model-dialect needs two hits (upstream) -> one hit fires (alternative)
    "G01": [(D, "    if c2 >= 2:\n        col.add(\"2_model_dialect\"", "    if c2 >= 1:\n        col.add(\"2_model_dialect\"")],
    # G02 a banned word split by zero-width characters still fires (upstream) -> does not (alternative)
    "G02": [(D, "    for m in RX1.finditer(A):",
             "    for m in RX1.finditer(A if not re.search(\"[\\u200b\\u200c\\u200d\\u2060\\ufeff]\", M) else M):")],
    # G03 a homoglyph inside a Latin word still matches the vocabulary (upstream) -> does not (alternative)
    "G03": [(D, "    for m in RX1.finditer(A):", "    for m in RX1.finditer(M if ch[\"tokens\"] else A):")],
    # G04 a NUL byte without a UTF-16 mark is not text: empty input (upstream) -> decoded as text (alternative)
    "G04": [(D, '    if b"\\x00" in data:\n        return ""\n', "")],
    # G05 indented code blocks generate no findings (upstream) -> are scanned (alternative)
    "G05": [(D, "        if expanded >= 4 and not in_para and not in_list:", "        if False:")],
    # G06 cleanup keeps the first line's indentation (upstream) -> strips it (alternative)
    "G06": [(D, "    text = text[k:]\n    text = text.rstrip", "    text = text[k:].lstrip(\" \\t\")\n    text = text.rstrip")],
    # G07 cleanup keeps the CRLF convention (upstream) -> writes LF (alternative)
    "G07": [(D, "    # trim\n    ended_lf = text.endswith(\"\\n\")", "    # trim\n    text = text.replace(\"\\r\\n\", \"\\n\")\n    ended_lf = text.endswith(\"\\n\")")],
    # G08 epub chapters in natural order, digits as numbers (upstream) -> plain name order (alternative)
    "G08": [(D, "    names = sorted([n for n in zf.namelist() if re.search(r\"\\.(x?html?)$\", n, re.I)], key=natkey)",
             "    names = sorted([n for n in zf.namelist() if re.search(r\"\\.(x?html?)$\", n, re.I)])")],
    # G09 the guard never nudges at confidence none (upstream) -> nudges on score alone (alternative)
    "G09": [(GUARD, "const flagged = score_ > threshold && m.confidence !== 'none';", "const flagged = score_ > threshold;")],
    # G10 instruction-file names skipped in any case (upstream) -> only lower case (alternative)
    "G10": [(GUARD, "const base = path.basename(abs).toLowerCase();", "const base = path.basename(abs);")],
    # G11 paths under a memory directory are skipped (upstream) -> scored (alternative)
    "G11": [(GUARD, "if (d === 'node_modules' || d === '.git' || d === 'memory') return true;",
             "if (d === 'node_modules' || d === '.git') return true;")],
    # G12 ledger files owner-only (upstream) -> default permissions (alternative)
    "G12": [(COM, "    fs.writeFileSync(p, JSON.stringify(keep), { mode: 0o600 });\n    try { fs.chmodSync(p, 0o600); } catch (e) { /* ignore */ }",
             "    fs.writeFileSync(p, JSON.stringify(keep), { mode: 0o644 });\n    try { fs.chmodSync(p, 0o644); } catch (e) { /* ignore */ }")],
    # G13 assistant entries sharing a message id are one turn (upstream) -> each entry a turn (alternative)
    "G13": [(STATS, "      if (seen.has(id)) continue;\n      seen.add(id);\n", "")],
    # G14 an apply_patch path line must begin with three asterisks (upstream) -> found anywhere in a line (alternative)
    "G14": [(GUARD, "const re = /^\\*\\*\\* (?:Add File|Update File|Move to):(.*)$/;", "const re = /\\*\\*\\* (?:Add File|Update File|Move to):(.*)$/;")],
    # G19 two decisive families raise the score to at least 65 (upstream) -> no such floor (alternative)
    "G19": [(D, "    if len(dec) >= 2:\n        score = max(score, 65)", "    if False:\n        score = max(score, 65)")],
    # G21 a no-break space is never an invisible character (upstream) -> counted as both (alternative)
    "G21": [(D, "            if not nbsp_kept(text, i, c):\n                spc += 1\n",
             "            if not nbsp_kept(text, i, c):\n                spc += 1\n                inv += c in \"\\u00a0\\u202f\"\n")],
    # G24 catalogue numbers that did not fire are omitted (upstream) -> listed with count 0 (alternative)
    "G24": [(D, '    rep["_metrics"] = met\n    return rep',
             '    for num in sorted(LABELS):\n        if not any(k.split("_", 1)[0] == str(num) for k in rep):\n'
             '            rep["%d_%s" % (num, SLUGS.get(num, "pattern"))] = {"label": LABELS[num], "count": 0, "samples": []}\n'
             '    rep["_metrics"] = met\n    return rep')],
    # G25 at most three samples per finding (upstream) -> up to five (alternative)
    "G25": [(D, "        if len(samples) < 3:\n            samples.append(excerpt_sample(A, W, m))",
             "        if len(samples) < 5:\n            samples.append(excerpt_sample(A, W, m))"),
            (D, '"samples": [clip(s) for s in samples[:3] if s]', '"samples": [clip(s) for s in samples[:5] if s]')],
    # G30 doctor's detector line stays successful when Python is missing (upstream) -> fails too (alternative)
    "G30": [(TRK, "      lines.push('[!!] python not found: saved files are not re-scored until Python is available; prose is still shaped by the contract.');",
             "      lines[2] = '[!!] detector: bundled script found but cannot be run';\n"
             "      lines.push('[!!] python not found: saved files are not re-scored until Python is available; prose is still shaped by the contract.');")],
    # G33 no welcome when the flag cannot be written (upstream) -> welcome whenever no flag existed (alternative)
    "G33": [(ACT, "    fresh = wrote && !exists;", "    fresh = !exists;")],
    # G60 empty show names the .docx and .pdf deliverables (upstream) -> does not (alternative)
    "G60": [(TRK, "    return 'nothing scored yet in this session. Rows appear after prose files, including .docx and .pdf deliverables, are saved.';",
             "    return 'nothing scored yet in this session.';")],
    # G67 a source-code extension given to the detector is read as plain text (upstream) -> refused (alternative)
    "G67": [(D, "    return decode_bytes(data), False\n\n\n# ----",
             "    if ext and ext not in PLAIN_EXTS:\n        raise Fail(\"cannot read input: unsupported file type %s\" % ext)\n"
             "    return decode_bytes(data), False\n\n\n# ----")],
}


def make(base, out, item):
    d = out / item
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(base, d, ignore=shutil.ignore_patterns("__pycache__"))
    for rel, old, new in PATCHES[item]:
        p = d / rel
        s = p.read_text(encoding="utf-8")
        n = s.count(old)
        assert n == 1, f"{item}: anchor found {n} times in {rel}: {old!r}"
        p.write_text(s.replace(old, new), encoding="utf-8")
    with tarfile.open(out / f"{item}.tgz", "w:gz") as t:
        for f in sorted(d.rglob("*")):
            if "__pycache__" not in f.parts:
                t.add(f, arcname="./" + str(f.relative_to(d)), recursive=False)


if __name__ == "__main__":
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    items = sys.argv[3:] or list(PATCHES)
    for it in items:
        make(base, out, it)
    with tarfile.open(out / "BASE.tgz", "w:gz") as t:
        for f in sorted(base.rglob("*")):
            if "__pycache__" not in f.parts:
                t.add(f, arcname="./" + str(f.relative_to(base)), recursive=False)
    print("made", len(items), "alternative copies and BASE.tgz in", out)
