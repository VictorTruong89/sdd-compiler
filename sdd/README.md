# `sdd/` — Spec-Driven Development workspace

This project is built spec-first. **The specs are the source of truth; the code is downstream.**

## Tiers

| Tier | Path | Authority | Lifetime |
|---|---|---|---|
| **Specs** | [`specs/`](specs/README.md) | **Authoritative.** Code is built from here | Permanent; amended in place |
| **Design** | `design/` | Non-authoritative: brainstorm, rationale, decision log. Never code from it | Release-scoped; frozen at close |
| **Blueprints** | [`blueprints/`](blueprints/README.md) | What the built code does and why this construction | Amended with the code |
| **Archive** | [`archive/`](archive/README.md) | Superseded, read-only | Frozen |
| **Questions** | [`questions.md`](questions.md) | Register of decisions and rejected options. Records reasoning, never rules | Permanent |

> **Specs are release-independent. Designs are release-scoped.**

## Layout

```text
sdd/
├── README.md                 this file
├── questions.md              question register
├── agent-workflow.md         how an AI agent turns specs into code    (placeholder)
├── specs/
│   ├── README.md             spec index
│   ├── vision.md             WHAT and WHY
│   ├── constitution.md       HOW: rules, invariants, test tiers
│   ├── ownership.yaml        spec → code globs
│   ├── F<n>_<slug>/spec.md   one feature = one spec (F1–F7)
│   └── _templates/spec.md    feature spec skeleton
├── design/
│   ├── releases/             one-page close-outs (+ template)
│   └── _templates/           brainstorm template
├── blueprints/               per-module as-built notes                (empty)
└── archive/
    ├── rel-01/               release 01, frozen: brainstorm, design notes, measurements,
    │                         a snapshot of the specs at the close, the first full compile
    ├── chat_history/         pre-rel01 brainstorm exports
    └── 2026-09-13_vision_pre-rel01.md
```

## Releases

| Release | State | Where |
|---|---|---|
| **rel01** | Closed 2026-10-01 | [close-out](design/releases/rel01_closeout.md) · [archive](archive/rel-01/README.md) |

No release is open. The next one starts by copying `design/_templates/brainstorm.md` into `design/`.

## Closing a release

1. Write the close-out in `design/releases/` and mark the brainstorm FROZEN.
2. Move the release's brainstorm and design notes to `archive/rel-<NN>/design/`, and copy `specs/`
   to `archive/rel-<NN>/specs/` as a snapshot. The live specs stay in `specs/`.
3. Re-point links in the live files; add the release to the table above and to `archive/README.md`.
