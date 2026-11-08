"""Make round 21's spec: plant the kept conflicts and remove the kept gaps in a copy of case016's public spec.
No model call.

    python3 notes/plant.py work/spec-planted C01 ... G01 ...       (from the trial folder)

Round 21 (new; joins round 19's notes/plant.py and round 20's notes/remove.py in one script, because this
round puts both kinds of item in one spec, owner 2026-11-05: "One spec").
  - **Conflict** C..: one edit adds side B in **one** place, in the spec's own voice and with no marker,
    so the other place still states side A. `PHRASES[item] = (A phrase, B phrase)`; after planting each
    must occur exactly once.
  - **Gap** G..: every place that states the fact is edited once, the smallest span that removes it and
    keeps the sentence readable; no marker and no "unspecified" wording is added. `KEY[item]` lists
    phrases that must occur nowhere after removal.
Every `old` string must occur exactly once in its file, so an edit never applies silently to the wrong
place. A bullet left empty by two removals is dropped. Zero2Repo has no licence file: the output stays
in git-ignored `work/`; this script holds only the short anchors and planted sentences.
"""
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case016/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

# item -> list of (file, old, new)
EDITS = {
    # ---------------- conflicts: side B added in one place
    "C01": [(PRD, "“seem(s) (to / like)”, “appear(s) to”, somewhat, relatively, fairly, “kind of”, “sort of”.",
             "“seem(s) (to / like)”, “appear(s) to”, somewhat, relatively, fairly, “kind of”, “sort of”. "
             "Each sentence with stacked hedges adds to the score.")],
    "C02": [(PRD, "three or more sentences open with the same first two words.",
             "three or more sentences open with the same first two words. Opener repetition raises the score like "
             "the other rhetorical families.")],
    "C03": [(PRD, "or any whitespace before the first character. A single final newline does not fire it.",
             "or any whitespace before the first character. A single final newline does not fire it. Stray "
             "whitespace counts toward the score, since it is a common residue of pasted model output.")],
    "C04": [(IC, "When confidence is not `high`, metrics carry a reason a caller can read (`confidence_reason`, under `scripts/detect.py`).",
             "When confidence is not `high`, metrics carry a reason a caller can read (`confidence_reason`, under "
             "`scripts/detect.py`). Confidence is `high` from 250 words on.")],
    "C05": [(IC, "when the document has enough sentences for an interval (the PRD's minimum)",
             "when the document has enough sentences for an interval (at least three sentences)")],
    "C06": [(PRD, "however many hits it has, scores at most 40 (`clean` or `light tells`), unless the single-decisive floor below applies.",
             "however many hits it has, scores at most 40 (`clean` or `light tells`), unless the single-decisive "
             "floor below applies. A decisive finding always lifts the score to at least 45, whatever the confidence.")],
    "C07": [(PRD, "- An unknown option fails with a distinct failing status and a structured error that identifies the unknown option and points at help.",
             "- An unknown option fails with a structured error that identifies the unknown option and points at "
             "help. Its exit status is 1, as for every other detector failure.")],
    "C08": [(IC, "Any other argument that begins with `-` before `--` is an unknown option. Switch order is free.",
             "Any other argument that begins with `-` before `--` is an unknown option. Switch order is free. When "
             "several operands are given, the last one is the file scanned.")],
    "C09": [(PRD, "and a double-dash that stops option parsing so a file name may begin with a dash.",
             "and a double-dash that stops option parsing so a file name may begin with a dash. The usage message "
             "goes to the error stream, so that standard output carries only reports.")],
    "C10": [(PRD, "- **Family rules.** Lexical families match whole words and phrases without regard to letter case unless a rule says otherwise,",
             "- **Family rules.** Blockquoted lines are prose like any other and are scanned. Lexical families match "
             "whole words and phrases without regard to letter case unless a rule says otherwise,")],
    "C11": [(PRD, "“continues to thrive”, “typical of emerging / urban / modern”, “faces several / many / numerous challenges”.",
             "“continues to thrive”, “typical of emerging / urban / modern”, “faces several / many / numerous "
             "challenges”. A single sentence that opens with one of the transition words of 37 already fires "
             "transition clusters.")],
    "C12": [(PRD, "a range between two years written with a hyphen: an earlier year, a hyphen, and a later year.",
             "a range between two years written with a hyphen: an earlier year, a hyphen, and a later year. A "
             "numeric span written in words, such as from 9 to 5, is a false range (15).")],
    "C13": [(PRD, "words beginning oai_citation; contentReference; navlist; and bracketed 【number†…】 markers.",
             "words beginning oai_citation; contentReference; navlist; and bracketed 【number†…】 markers. Any "
             "`utm_source` parameter left in a link is an AI tracking parameter (65).")],
    "C14": [(PRD, "A sentence of the second shape may also carry the parallelism form of 17 under the rule above.",
             "A sentence of the second shape may also carry the parallelism form of 17 under the rule above. Any "
             "clause closed by a comma and a short “no” phrase is the tailing-negation form of 17.")],
    "C15": [(PRD, "fold mixed-script lookalikes inside Latin runs to ASCII, and trim stray whitespace. Visible text is left alone.",
             "fold mixed-script lookalikes inside Latin runs to ASCII, and trim stray whitespace. Every no-break "
             "space becomes an ordinary space. Visible text is left alone.")],
    "C16": [(PRD, "then, when the input ended in a line feed, exactly one line ending is restored.",
             "then, when the input ended in a line feed, exactly one line ending is restored. Two trailing spaces "
             "that end a line of prose are a markdown hard break and are kept.")],
    "C17": [(IC, "When an `apply_patch` payload flags several files, their lines are joined by a newline, in any order.",
             "When an `apply_patch` payload flags several files, their lines are joined by a newline, in any "
             "order. At most ten paths of one payload are scored.")],
    "C18": [(IC, "- Session ledgers are files under `CLAUDE_CONFIG_DIR` named as stated under Config filenames.",
             "- Session ledgers are files under `CLAUDE_CONFIG_DIR` named as stated under Config filenames. Each "
             "ledger keeps its newest 50 records.")],
    "C19": [(IC, "session ledger files whose names are `.prosecheck-ledger` or start with that prefix followed by a hyphen.",
             "session ledger files whose names are `.prosecheck-ledger` or start with that prefix followed by a "
             "hyphen. A ledger untouched for more than one day is deleted at the next session start.")],
    "C20": [(IC, "the environment may supply; when it applies is the PRD’s rule (FP-04).",
             "the environment may supply; when it is set, it takes precedence over the stored level.")],
    "C21": [(PRD, "When the level is `off`, the hook emits nothing.\n- When a subagent starts",
             "When the level is `off`, the hook emits nothing. A prompt that contains `stop prosecheck` anywhere "
             "switches the tool off.\n- When a subagent starts")],
    "C22": [(IC, "When the scored slice is longer than the PRD's threshold,",
             "When the scored slice is longer than 500 characters,")],
    "C23": [(IC, "Text is taken from `content` entries whose `type` is `text`.",
             "Text is taken from `content` entries whose `type` is `text`. When the `projects` folder holds a "
             "transcript newer than the named one, the newer transcript is read.")],
    "C25": [(IC, "keyed exactly `17_negative_parallelism` (the parallelism form) and `17_tailing_negation` (the tailing-negation form).",
             "keyed exactly `17_negative_parallelism` (the parallelism form) and `17_tailing_negation` (the "
             "tailing-negation form). Both forms of catalogue 17 are writing advice and carry weight zero.")],
    "C26": [(PRD, "- **Em-dash overuse (58):** two or more em dashes in one paragraph.",
             "- **Em-dash overuse (58):** two or more em dashes in one paragraph. Each such paragraph raises the score.")],

    # ---------------- gaps: the fact removed at every place it is stated
    "G01": [(PRD, " It fires only when a document has two or more of these hits combined.", "")],
    "G02": [(PRD, "A banned word that is split only by in-word zero-width characters still fires the same finding as the unsplit word. ", "")],
    "G03": [(PRD, "A mixed-script lookalike inside a Latin word both fires mixed-script homoglyphs (66) and still matches the same vocabulary finding as the ASCII spelling.", "")],
    "G04": [(PRD, "- A binary-looking buffer that is not UTF-16 and contains a NUL byte is treated as not text: it yields empty input (failure), not a report full of invented invisible-character hits. UTF-16 with a byte-order mark is decoded as text.",
             "- UTF-16 with a byte-order mark is decoded as text."),
            (PRD, "PDF, RTF, and a buffer that is not text)", "PDF, and RTF)"),
            (IC, " A buffer that is not UTF-16 and contains a NUL byte is not text.", "")],
    "G05": [(PRD, "fenced and indented code blocks as CommonMark defines them (including how a fence closes and how an indented line that continues a paragraph stays paragraph text)",
             "fenced code blocks as CommonMark defines them (including how a fence closes)")],
    "G06": [(PRD, " The first line’s own indentation is kept.", "")],
    "G07": [(PRD, " Cleanup (FP-03) preserves the input’s newline convention on output so a file that arrived with carriage-return/line-feed still has it.", "")],
    "G08": [(PRD, "chapter HTML/XHTML documents are read in the natural order of their member names in the archive (runs of digits compare as numbers).",
             "chapter HTML/XHTML documents are read.")],
    "G09": [(PRD, " The saved-file guard (FP-05) treats `none` as “do not nudge,” even if the point score is above the threshold.", ""),
            (PRD, "A file is flagged only when the score is **strictly above** the threshold **and** confidence is not `none`. Zero-confidence results never nudge.",
             "A file is flagged only when the score is **strictly above** the threshold.")],
    "G10": [(PRD, "`skill.md`, or `memory.md` (any case) are skipped", "`skill.md`, or `memory.md` are skipped")],
    "G11": [(PRD, "Paths under `node_modules`, under `.git`, or under a `memory` directory are skipped", "Paths under `node_modules` or under `.git` are skipped")],
    "G12": [(PRD, " Ledger files are written with owner-only permissions.", ""),
            (IC, "What a ledger records, how long it is kept, and its file permissions are the PRD’s rules",
             "What a ledger records and how long it is kept are the PRD’s rules")],
    "G13": [(PRD, " Assistant entries that share one message identifier contribute one turn and one copy of their token totals, while the text of every one of them enters the prose slice; entries with no identifier are each counted.", "")],
    "G14": [(PRD, " A line that only contains those words and does not begin with three asterisks does not name a path.", "")],
    "G19": [(PRD, " Two distinct decisive families in one scan raise the score to **at least 65**.", "")],
    "G21": [(PRD, "; a no-break space that cleanup keeps is not counted, and a no-break space is never an invisible character (62).",
             "; a no-break space that cleanup keeps is not counted.")],
    "G25": [(PRD, "It carries a human-readable label, a hit count, and up to three short samples drawn from the text.",
             "It carries a human-readable label, a hit count, and short samples drawn from the text."),
            (IC, "`samples` is an array of at most three short strings.", "`samples` is an array of short strings.")],
    "G30": [(PRD, " The detector-present check stays successful when Python cannot be launched and says nothing about Python.", ""),
            (IC, " This line never contains `python`, and it stays successful when Python cannot be launched.", "")],
    "G33": [(PRD, "— when no mode flag exists yet and the flag can actually be written —", "— when no mode flag exists yet —"),
            (PRD, "A later start on the same config directory, and a start whose flag cannot be written, carry no welcome.",
             "A later start on the same config directory carries no welcome."),
            (IC, "On the first start of an install whose level flag can be written, the welcome block comes first",
             "On the first start of an install, the welcome block comes first"),
            (IC, "A later start, or a start whose flag cannot be written, prints only the writing contract.",
             "A later start prints only the writing contract.")],
    "G60": [(PRD, "An empty ledger says that no file has been scored in this session and that rows appear after prose files, including `.docx` and `.pdf` deliverables, are saved.",
             "An empty ledger says that no file has been scored in this session."),
            (IC, "The reply contains the phrase `nothing scored yet`, and contains `.docx` and `.pdf`.",
             "The reply contains the phrase `nothing scored yet`.")],
    "G67": [(PRD, " If the detector command is aimed at such a file anyway, it is read as plain text; that is not a plugin obligation.", "")],
}

# conflict item: (side-A phrase, side-B phrase); each must occur exactly once in the planted spec
PHRASES = {
    "C01": ("54 (hedge stacking)", "Each sentence with stacked hedges adds to the score"),
    "C02": ("42 (opener repetition)", "Opener repetition raises the score like the other rhetorical families"),
    "C03": ("68 (trailing / stray whitespace)", "Stray whitespace counts toward the score"),
    "C04": ("`high` at 300 words or more", "Confidence is `high` from 250 words on"),
    "C05": ("the document has at least four sentences", "(at least three sentences)"),
    "C06": ("A single decisive family raises it to **at least 45** only when confidence is above `low`",
            "A decisive finding always lifts the score to at least 45, whatever the confidence"),
    "C07": ("An unknown option: exit 2", "Its exit status is 1, as for every other detector failure"),
    "C08": ("the first file is scanned, and the error stream notes", "the last one is the file scanned"),
    "C09": ("write the usage message to standard output and exit 0", "The usage message goes to the error stream"),
    "C10": ("runs of two or more consecutive blockquote lines", "Blockquoted lines are prose like any other and are scanned"),
    "C11": ("two or more sentence-opening transitions", "already fires transition clusters"),
    "C12": ("only the rhetorical sweep between a beginning and a grand or present-day end", "is a false range (15)"),
    "C13": ("it fires only when that whole host name is one of those domains", "parameter left in a link is an AI tracking parameter"),
    "C14": ("a short “no …” tail of the stock kind", "Any clause closed by a comma and a short “no” phrase"),
    "C15": ("that holds something together", "Every no-break space becomes an ordinary space"),
    "C16": ("even when two spaces were meant as a markdown hard break", "are a markdown hard break and are kept"),
    "C17": ("at most **16** distinct paths", "At most ten paths of one payload are scored"),
    "C18": ("At most the newest 20 records are kept", "Each ledger keeps its newest 50 records"),
    "C19": ("more than seven days old is gone", "A ledger untouched for more than one day is deleted"),
    "C20": ("When nothing valid is stored, the level is `full`, unless the environment supplies one of those four words",
            "it takes precedence over the stored level"),
    "C21": ("the same words with anything else before or after them are an ordinary prompt",
            "contains `stop prosecheck` anywhere switches the tool off"),
    "C22": ("is longer than 200 characters", "longer than 500 characters"),
    "C23": ("a named transcript wins over a newer one", "the newer transcript is read"),
    "C25": ("The **tailing-negation form** is score-moving", "Both forms of catalogue 17 are writing advice"),
    "C26": ("58 (em-dash overuse)", "Each such paragraph raises the score"),
}

# gap item: phrases that must occur nowhere in the gapped spec (also checked over the export)
KEY = {
    "G01": ["two or more of these hits"], "G02": ["zero-width characters still fires"],
    "G03": ["still matches the same vocabulary finding"], "G04": ["NUL"],
    "G05": ["indented code blocks"], "G06": ["own indentation"], "G07": ["newline convention"],
    "G08": ["runs of digits compare as numbers", "natural order"], "G09": ["do not nudge", "Zero-confidence", "confidence is not `none`"],
    "G10": ["(any case)"], "G11": ["`memory` directory"], "G12": ["owner-only", "file permissions"],
    "G13": ["share one message identifier"], "G14": ["does not begin with three asterisks"],
    "G19": ["at least 65"], "G21": ["never an invisible character"],
    "G25": ["up to three short samples", "at most three short strings"],
    "G30": ["stays successful when Python"], "G33": ["flag cannot be written", "can actually be written", "flag can be written"],
    "G60": ["`.docx` and `.pdf` deliverables", "contains `.docx` and `.pdf`"],
    "G67": ["it is read as plain text"],
}

# The items kept after step 1 (ANSWER_KEY.md), for the scripts that score them. Filled after selection.
KEPT_C: list[str] = ["C01", "C06", "C08", "C09", "C11", "C12", "C13", "C15", "C16", "C17", "C18", "C19", "C20",
                      "C21", "C22", "C23", "C25"]
KEPT_G: list[str] = ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10", "G11", "G12", "G13",
                      "G21", "G30", "G33"]
KEPT = KEPT_C + KEPT_G
# Found after the check run (2026-11-06), before the other 23 runs: G01's removal missed one sentence
# (PRD 236, FP-04: model-dialect vocabulary "needs two hits"), so G01 is still stated. It stays planted
# and scored (the spec is the same in all arms; a second compile is not approved) but is reported apart,
# never counted in set 2b.
STATED_G = ["G01"]
# conflict item: (A substring, B substring) where the atomizer cut a phrase (filled after the compile, if needed)
# Round 21, after the compile: C08 and C20's side A were cut into two nodes each; C12's side A is in no node
# (block B-000074, PRD line 110, atomized with no node carrying the false-range rule; the same in round
# 13c's case016 store: an atomizer omission, recorded in TRIAL.md, not fixed). The export's packs still
# print the block's source text, so the agent sees C12's side A; only the conflict check cannot reach it.
FIND: dict[str, tuple[str | None, str | None]] = {
    "C08": ("the first file is scanned", None),
    "C20": ("When nothing valid is stored, the level is `full", None),
}


def words(folder):
    return sum(len(f.read_text(encoding="utf-8").split()) for f in folder.glob("*.md"))


if __name__ == "__main__":
    out, items = Path(sys.argv[1]), sys.argv[2:]
    assert items and all(i in EDITS for i in items), items
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in PUBLIC.glob("*.md"):
        shutil.copy(f, out / f.name)
    n_edits = 0
    for item in items:
        for name, old, new in EDITS[item]:
            text = (out / name).read_text(encoding="utf-8")
            assert text.count(old) == 1, (item, name, text.count(old), old[:60])
            (out / name).write_text(text.replace(old, new), encoding="utf-8")
            n_edits += 1
    for f in out.glob("*.md"):   # a bullet emptied by two removals is dropped
        t = f.read_text(encoding="utf-8")
        f.write_text(re.sub(r"(?m)^- *\n", "", t), encoding="utf-8")
    spec = "\n".join(f.read_text(encoding="utf-8") for f in sorted(out.glob("*.md")))
    for item in items:
        if item in PHRASES:
            for side, phrase in zip("AB", PHRASES[item]):
                assert spec.count(phrase) == 1, (item, side, phrase, spec.count(phrase))
        for k in KEY.get(item, []):
            assert k not in spec, (item, "key phrase left", k)
    print(f"{n_edits} edits for {len(items)} items; phrases and keys ok; words {words(PUBLIC)} -> {words(out)}")
