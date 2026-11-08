# prosecheck 0.9.3: build notes

What was built, where the specification disagrees with itself, and what it leaves unstated.
Paths are relative to `/app`. `spec/` was not modified.

## Layout

- `scripts/detect.py`: the detector (Python 3, standard library only). Extraction, masking,
  the 62 machine-checked patterns, scoring, `--clean`, `--ci`, errors.
- `hooks/prosecheck-activate.js` (session start), `hooks/prosecheck-tracker.js` (prompt submit and
  `/prosecheck` router), `hooks/prosecheck-subagent.js`, `hooks/prosecheck-guard.js` (post tool use),
  `hooks/prosecheck-stats.js` (stats; also used by the router).
- `hooks/lib/prosecheck.js`: shared config, ledger, detector runner, contract text.
- `hooks/hooks.json`: hook registration for the plugin. Not named by the spec; added so the plugin loads.
- `commands/prosecheck.md`: slash-command menu document, body `/prosecheck $ARGUMENTS`.
- `.cursor/rules/prosecheck.mdc`: shipped Cursor rule (prose globs only, no detector step).
- `.claude-plugin/plugin.json`: manifest (name, version 0.9.3). Not named by the spec; added.
- `skills/prosecheck/SKILL.md`: short rewrite skill for "prosecheck this" / "humanize this".

No detector copy exists under `skills/`. The detector lookup falls back to that path only if
`scripts/detect.py` is missing.

## Where the specification disagrees, and what was built

1. **Which operand is scanned when several are given.** The Interface Contract's `scripts/detect.py`
   signature says "the last one is the file scanned". Its "Several file operands" section and the PRD
   (FP-01) say the first. **Built: the first.** A notice naming the first operand goes to stderr.

2. **Decisive-finding floor at low confidence.** PRD FP-01 says a decisive finding "always lifts the
   score to at least 45, whatever the confidence", then says a single decisive family at `none` or `low`
   confidence does not take the 45 floor. **Built: the second, more specific rule.** One decisive family
   gets the floor 45 only at `moderate` or `high` confidence. Two or more decisive families get 65 at any
   confidence.

3. **Stop phrases.** FP-04 says a prompt that "contains `stop prosecheck` anywhere" switches the tool off.
   FP-06 and the Interface say the whole prompt must be that phrase. **Built: whole prompt only** (case
   ignored, surrounding whitespace ignored). The same words with other text are ordinary prompts.

4. **No-break spaces in cleanup.** The Terms table says "every no-break space becomes an ordinary space".
   FP-03 keeps U+00A0 and U+202F in the positions it lists (next to a digit, before `: ; ! ? » › % €`,
   after `« ‹`). **Built: the FP-03 rule.** The same rule is used for counting finding 67, so a kept
   no-break space is not counted.

5. **Trailing spaces that mark a hard break.** FP-03 says two trailing spaces "are kept", then says the
   collapse "is required, not optional". **Built: removed.**

6. **Ledger size.** The Interface says each ledger keeps its newest 50 records, but defers "what a ledger
   records and how long it is kept" to the PRD. The PRD says 20. **Built: 20.**

7. **Ledger retention.** The Interface's config-filenames rule deletes ledgers untouched for more than one
   day at session start. The PRD says a ledger seven days old or younger is kept and listed by `show`.
   **Built: seven days**, for both deletion (at session start) and listing. A one-day deletion would
   contradict the PRD's `show` rule.

8. **Which transcript `stats` reads.** The Interface says a newer transcript in the projects folder is
   read even when the host named one. The PRD says "a named transcript wins over a newer one". **Built:
   the named transcript wins.**

9. **Session-prose score threshold.** The PRD says the score is printed when the slice is longer than
   200 characters. The Interface says 500 in its reply section. **Built: 500**, because the Interface
   governs reply shapes.

10. **Guard path cap.** The PRD says up to 16 distinct paths per `apply_patch`. The Interface says "at
    most ten paths of one payload are scored". **Built: 10.**

11. **`PROSECHECK_DEFAULT_MODE`.** The Interface says the variable "takes precedence over the stored
    level". The PRD says it is used only when nothing valid is stored. **Built: precedence over the stored
    level**, as the Interface says. The env word also governs what `status` reports.

12. **Model-dialect family (2).** FP-04 says these words "need two hits". **Built: family 2 fires only at
    two or more total hits.** Single occurrences do not count.

13. **Catalogue 7 (rule of three).** The PRD's "no detector" list includes 7, so 7 is not machine-checked.
    The Terms table says 62 machine-checked numbers, which matches only if 7 is excluded. **Built: no
    detector for 7.**

14. **Stats: duplicate assistant rows.** The Interface says "a message's identifier is its `id`" without
    stating the rule. **Built: assistant rows sharing a `message.id` (or `uuid`) are counted once**, both for
    turns, tokens, and prose text.

## Choices the specification leaves open

- **Scoring formula.** The PRD fixes the caps and floors but not per-family points. Built: a score-moving
  family adds 8 points, plus 1.5 for each extra hit up to four extra hits, plus 6 for a decisive family.
  Then the caps apply (one family: at most 40; only sentence-length monotony: at most 20; only rhythm
  kinds 40 and 44: at most 40), then the floors apply.
- **Confidence reasons.** Free text, as the spec allows. High confidence reports an empty reason.
- **Word count.** Runs of letters, digits, apostrophes (straight or curly), and hyphens, counted only on
  the masked scan window and only when the run starts with a letter or digit (so bare punctuation lists do
  not count).
- **Masking for findings.** Front matter, fenced code, inline code, blockquote runs of two or more lines,
  table rows, and badge lines are masked for pattern findings. Character-layer findings (62, 66, 67, 68)
  are computed on the unmasked window, except 68 skips lines inside masked regions.
- **Sentence and paragraph splitting.** Heuristic. Headings and list items are their own units. Sentences
  end at `.`, `!`, or `?` followed by whitespace. Paragraphs are separated by blank lines.
- **Family rules left to judgement.** Adjective chains (6): four comma- or `and`-joined words with at least
  one adjective-like word and no function word. Notability (11): a fixed outlet list. Synonym cycling (8):
  three or more members of one cluster. Hyphenated pairs (4), marketing phrases (69), and the
  "marketing imperative" sentences in family 3 use fixed lists. Mixed-script homoglyphs (66) use a partial
  Cyrillic, Greek, and Armenian map. Arabic-presentation lookalikes are not in the map. Emoji (57) is a
  pictographic range set, not the full emoji database. Degenerate repetition (71) needs 20% of six-word
  runs to repeat, with no minimum length.
- **Title case (59).** Minor words: articles, conjunctions, and prepositions of four letters or fewer, plus a
  small set of longer ones (`into`, `onto`, `upon`, `than`, `like`, `with`, `from`, `over`).
- **Contraction absence (55).** Fires when first-person words are at least 3% of words in a text of 50 or
  more words, and at least three expanded forms appear while contractions are at most a quarter of them.
- **Opener repetition (42), alternation (41), uniform paragraphs (44), monotony (40).** Thresholds for
  alternation: six sentences, four of five steps alternating, each step at least 4 words and 35% of the mean.
- **`--ci`.** Sentence-level bootstrap: 40 resamples, seed 1729, 5th and 95th percentiles. Sentence-local
  families are resampled. Document-level families (34, 35, 40, 41, 42, 44, 46, 70, 71) stay fixed at their
  full-document value. The point score is unchanged. Fewer than four sentences gives `score_ci: null` with a
  note.
- **Cleanup.** CR line endings are kept (the CR is not treated as a trailing space). Lines are trimmed of
  trailing spaces and tabs. Leading blank lines are dropped. One trailing newline is restored only when the
  input ended with a line feed. Line and paragraph separators (U+2028, U+2029) become line feeds.
- **Invisible characters.** Kept in the positions FP-03 lists. For a tag character, the emoji chain is
  detected by walking back to a black-flag base. For a zero-width joiner, the joining-script and symbol
  neighbours are checked. The Mongolian and Khmer selectors and the bidi controls follow the listed rules.
- **Decoding.** Invalid UTF-8 is replaced with U+FFFD. UTF-16 with a BOM is decoded. A leading BOM is removed
  and not counted.
- **Extraction.** `.docx`/`.pptx`: paragraphs or slides joined by line feeds. `.xlsx`: one line per non-empty
  cell in sheet order, shared strings resolved, non-whole indices dropped. `.odt`/`.odp`/`.ods`: text with
  `text:s` expanded to spaces, tabs and line breaks kept. `.epub`: spine order from the OPF, nav documents
  skipped, `script`/`style`/`head` skipped, parsed leniently as HTML. `.ipynb`: markdown cells only, joined by
  line feeds, invalid structure yields empty input. Zip members over 64 MB are skipped.
- **`.pdf`/`.rtf`.** Empty extracted prose, so the detector exits 1 with `empty input`.
- **Unsupported extensions in `check` and the detector.** Read as plain text, with the plain-text cap in
  `check`.
- **Size caps.** Plain text 524,288 bytes (512 KB). Zip-based documents and notebooks 4,194,304 bytes
  (4 MB, shown as 4096 KB in `check` and `show`). The detector itself does not enforce caps, as the PRD says.
- **Failure reasons in the ledger.** Five distinct user-readable reasons: `Python not found`,
  `detector timed out`, `detector produced no usable result` (non-zero exit, or exit 0 with no output),
  `detector output was not a report`, `report has no numeric score`. An unreadable file is `file could not
  be read`.
- **Timeouts.** 8 seconds for plain text, 15 seconds for archives and notebooks, both in the guard and `check`.
- **Ledger file.** `.prosecheck-ledger-<session id, sanitised>.json` in the config directory. Entries carry
  the base name, kind, score, band, phrase, up to five labels, flagged and truncated bits, and a timestamp.
  No document text and no full path are stored.
- **Level flag.** `.prosecheck-active` holds the bare word with no trailing newline. It is written on the first
  session start when no valid word is stored. The welcome is shown on the first session start when the flag
  file does not exist.
- **Doctor.** The Python probe runs the bundled detector on one short sentence. The settings probe writes and
  deletes a temporary file in the config directory.
- **`init` export.** Written to `./AGENTS.md` between `<!-- prosecheck:contract:start -->` and
  `<!-- prosecheck:contract:end -->` markers, under the heading `## Prose writing contract (prosecheck)`.
  The second `init` detects the heading or the start marker and leaves the file unchanged. The export names
  no path and no user name. At full and strict, the one line that names `CLAUDE_PLUGIN_ROOT` also names
  `skills` and `plugins`.
- **Cursor rule globs.** Written as one quoted comma-separated string, `globs: "*.md,*.mdx,..."`.
- **`init` working directory.** Uses the hook process's current working directory, not the payload `cwd`.
- **Guard skip rule.** Files under the plugin root are skipped. In this checkout the plugin root is `/app`,
  so prose files saved under `/app` are not scored. This is the spec's rule ("files that live inside the
  plugin's own install tree are skipped"), but it matters when testing from `/app`.
- **Check replies.** Unknown extensions are scored as plain text. The "no report" wording is used for an
  exit-0 run with no output, and for exit-0 output that is not a report or has no numeric score. A
  non-zero exit names the file and says "failed", with the stderr last line.
- **`check` over-cap message.** `over 512 KB` for plain text. `over 4096 KB` for archives and notebooks.

## Verification done

Manual runs on this machine (Linux, Python 3.13, Node 22) against a scratch config directory:

- Detector: clean and AI-style prose; error exits 1 and 2 with JSON on stderr and no traceback; help exits 0
  with the exact usage first line; the first operand scanned with a notice when several are given;
  `--clean` output and a rescan that reports zero invisible characters, non-standard spaces, and homoglyphs;
  fenced code, front matter, and inline code produce no findings; the 262,144-character window (both 262,144
  and 262,145 characters); extraction of `.docx`, `.pptx`, `.xlsx`, `.odt`, `.epub`, `.ipynb`; `--ci` output;
  timing (1 second for a 200 KB single-line input after fixing a quadratic regex).
- Hooks: session start (welcome once, then contract only), subagent contract, ordinary prompt reminder,
  `status`, `lite`, `strict`, `off`, `on`, unknown word, `help`, `check` (scored, missing, directory, `.pdf`,
  no path), `show` (scored, flagged, binary, failed, skipped, empty), `init` (write, then "already" on the
  second run; export contains no path and one `CLAUDE_PLUGIN_ROOT` line), guard on `Write` and `apply_patch`
  (flagged nudge, silence for clean files, instruction files skipped, binary and failed ledger records),
  `stats` (token totals with deduplication, missing transcript), `doctor` in full, off, and Python-missing
  states.
- Contract text: each level checked for the banned-vocabulary words, the "source code" rule, the targets, and
  the absence of `light tells` and `40` at lite.

Not verified: Windows and macOS (the code uses `path` and `spawnSync` but was run only on Linux). Python
3.9 is the documented floor and was not tested; the code avoids 3.10+ syntax. There is no test suite in the
repository. The hidden acceptance tests were not seen and were not used.
