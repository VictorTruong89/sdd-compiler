# F<n> — <Feature name>

> **Spec-ID:** F<n> · **Status:** 🔵 idea | 🟡 draft | 🟢 approved · **Adopted:** YYYY-MM-DD
> **Source discussion:** `sdd/design/rel<NN>_brainstorm.md` <session refs>
> **Governs:** `constitution.md` (enforces <ids>)

<!--
HOW TO USE (delete this block in a real spec):
- Copy to sdd/specs/F<n>_<slug>/spec.md. Keep every heading, even if empty (write "None yet"),
  so section numbers mean the same thing in every spec.
- A feature is ready to become a spec only when its acceptance criteria can be written.
- Every AC maps to exactly one test tier (constitution §4) and appears in §9.
- Status: 🔵 idea → 🟡 draft (has ACs) → 🟢 approved (coding may start).
-->

---

## 1. Goal & why

<One paragraph: what this feature does and why it matters.>

## 2. Scope / non-goals

**In scope:** <…>
**Non-goals:** <what is deferred, and to where>

## 3. Users & triggers

| ID | Trigger | Input | Entry point (code) |
|---|---|---|---|
| T1 | <when/how invoked> | <…> | `<module::function>` |

## 4. Behaviour

- **<Step / concern>:** <what happens; which invariant it enforces>

## 5. Contracts

**CT-<n>.1 — <name>:**
```json
{ "field": "type / enum / rule" }
```

## 6. Acceptance criteria

- **AC-<n>.1** *(<label>)* — **Given** <precondition>, **when** <action>, **then** <observable
  outcome>. → *<test tier>.* (<refs>)

## 7. Decisions

> Resolved questions, kept with the options rejected and why. *None yet.*

## 8. Open questions

- **Q1 — <question>:** <context; which AC it blocks>

## 9. Traceability

| AC | Test (file::test) | Code |
|---|---|---|
| AC-<n>.1 | *(to be written)* | `<module>` |
