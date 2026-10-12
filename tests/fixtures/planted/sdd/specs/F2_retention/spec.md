# F2 — Retention: how long we keep things

> **Spec-ID:** F2 · **Status:** 🟢 approved · **Drafted:** 2026-03-04 · **Approved:** 2026-03-09

## 1. Goal & why

Keeping data for ever is a liability, and deleting it too early is a support incident. This spec sets
one retention rule per kind of object, so nobody has to guess.

## 2. Behaviour

### 2.1 Export archives

An export archive is kept for 30 days after it is created, then deleted with its download link.

Retention is counted from creation, not from the last download: a member who downloads an archive on
day 29 does not extend its life.

### 2.2 Audit events

An audit event is kept for one year. Audit events are never deleted by a member, only by the
retention job.

### 2.3 Deleted projects

A deleted project is recoverable for 14 days. After that its files, its exports and its audit events
are removed by the retention job in one pass.

### 2.4 The retention job

The retention job runs nightly. It removes an export archive 7 days after it was created, an audit
event after one year, and a deleted project's files after the recovery window.

A workspace export must be at most 5 GiB, measured on the compressed archive.

## 3. Acceptance criteria

- **AC-2.1** *(archive retention)* — **Given** an archive created on day 0, **when** the retention job
  runs on day 31, **then** the archive and its link are gone. → *integration.*
- **AC-2.2** *(recovery window)* — **Given** a project deleted on day 0, **when** a member restores it
  on day 13, **then** the project and its files come back. → *integration.*
