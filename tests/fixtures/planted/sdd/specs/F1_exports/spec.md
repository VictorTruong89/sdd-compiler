# F1 — Exports: getting data out of the workspace

> **Spec-ID:** F1 · **Status:** 🟢 approved · **Drafted:** 2026-03-02 · **Approved:** 2026-03-09

## 1. Goal & why

People leave, audits happen, and a workspace that cannot be exported is a workspace nobody will
trust with anything important. An export is a single archive a member can download and open without
this product.

## 2. Scope / non-goals

**In scope:** a full workspace export, a per-project export, and the nightly backup export.
**Non-goals:** importing an archive back — that is F4, and it is not in this release.

## 3. Behaviour

### 3.1 Requesting an export

Any member of a workspace may request an export of a project they can already read. The request is
queued; the member is emailed when the archive is ready.

An export archive must be at most 5 GB. A request whose archive would be larger is rejected when it
is queued, and the member is told to export one project at a time.

The archive is a ZIP file containing one folder per project, plus a `manifest.json` naming every file
and its checksum.

### 3.2 Encryption

Every export must be encrypted with the workspace key before it leaves the storage layer.

The nightly backup export should be encrypted, and the operations runbook explains how to check that
it was.

### 3.3 Delivery

The download link is valid for 24 hours. After that the member requests the export again; archives
are never re-sent by email.

An export must never contain the owner's email address, because archives are routinely shared with
people outside the workspace.

The `manifest.json` lists, for each file, its path, size, checksum, and the email address of the
member who uploaded it, so an auditor can trace provenance without opening the files.

## 4. Acceptance criteria

- **AC-1.1** *(size limit)* — **Given** a project whose archive would exceed the limit, **when** an
  export is requested, **then** the request is rejected at queue time. → *unit.*
- **AC-1.2** *(link expiry)* — **Given** a finished export, **then** its download link stops working
  24 hours after it was issued. → *unit.*
