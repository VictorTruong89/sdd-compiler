# Planted conflicts — the answer key for M1 (recall)

> **Corpus:** 3 files, 2 "specs", ~725 words, written 2026-09-21 for the M4 gate (G4 §3 corpus 2).
> **Rule followed:** the conflicts are written in the same voice as their neighbours, with ordinary
> prose around them, so the model cannot spot a seam (G4 §3's warning). Nothing in the files marks a
> planted pair, and the two files were written as if by two authors who had not read each other.
>
> **This file is the denominator.** M1 recall = how many of these the compiler reports. It is *not*
> the numerator's judge: anything else the compiler reports is judged separately (M2 precision), and
> may be a real conflict this key missed — the fixture's prose was not audited for accidents.

| # | Kind | Claim A | Claim B | Why it is a conflict |
|---|---|---|---|---|
| **P1** | contradiction | `F2 §2.1` "An export archive is kept for **30 days** after it is created" | `F2 §2.4` "It removes an export archive **7 days** after it was created" | The same object, two retentions, in one spec. The kind of thing a reader skims past |
| **P2** | contradiction (unit boundary) | `F1 §3.1` "An export archive must be at most **5 GB**" | `F2 §2.4` "A workspace export must be at most **5 GiB**" | Same limit, two units: 5 GiB is ~7 % larger, so an archive between them is both legal and illegal |
| **P3** | contradiction (negative constraint) | `F1 §3.3` "An export **must never contain the owner's email address**" | `F1 §3.3` "`manifest.json` lists … the **email address of the member who uploaded** it" | The manifest is inside the archive. Two paragraphs apart, both sound reasonable alone |
| **P4** | subsumption, differing modality | `F1 §3.2` "**Every** export **must** be encrypted with the workspace key" | `F1 §3.2` "The nightly backup export **should** be encrypted" | The second is a weaker rule about a subset of the first — F6 D2's case exactly |
| **P5** | duplication | `F1 §3.1` "An export archive must be at most 5 GB" | `F2 §2.4` "A workspace export must be at most 5 GiB" | The same rule stated in two specs. Reported as duplication **or** contradiction is a hit (it is both; P2 counts the unit clash) |
| **P6** | contradiction through an alias | `F1/sharing.md` "A **shared link** expires 30 days after it is created" | `F2 §2.1` "An export archive is kept for 30 days … then deleted with its download link" + `F2 §2.4` "removes an export archive 7 days after" | The link outlives the thing it points at, and only if "share link" and "download link" are recognised as the same thing |

**Six planted pairs.** P2 and P5 are the same two claims judged under two kinds; a report naming that
pair once counts for both, and the write-up must say so rather than counting it twice.

## What is deliberately *not* planted

- No conflict spans more than two claims.
- No conflict depends on arithmetic beyond the unit boundary in P2.
- The rest of the prose was written to be consistent, but **not audited**: if the compiler reports
  something else, judge it on its merits before calling it a false positive.
