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
├── questions.md              question register                        (placeholder)
├── agent-workflow.md         how an AI agent turns specs into code    (placeholder)
├── specs/
│   ├── README.md             spec index                               (placeholder)
│   ├── vision.md             WHAT and WHY                             (placeholder)
│   ├── constitution.md       HOW: rules, invariants, test tiers       (placeholder)
│   ├── ownership.yaml        spec → code globs                        (placeholder)
│   └── _templates/spec.md    feature spec skeleton
├── design/
│   ├── rel01_brainstorm.md   rel01 living brainstorm and decisions    (placeholder)
│   ├── rel01_design/         rel01 design notes (core-working-principle.md: pre-rel01 input)
│   ├── releases/             one-page close-outs (+ template)
│   └── _templates/           brainstorm template
├── blueprints/               per-module as-built notes                (empty)
└── archive/                  frozen history (the pre-rel01 vision)
```

## Current release

**rel01** — opened 2026-09-14, target 2026-09-30. See [`design/rel01_brainstorm.md`](design/rel01_brainstorm.md).
