R-000002: compiled 1 file(s) · 4 new · 0 changed · 0 removed
atomized 37 of 37 pending block(s) · 0 failed · 2 formed no node · 52 node(s) formed, 0 deleted
checked 44 pair(s) (31 judged, 13 replayed) · 6 model call(s) · $0.1234 · 13 answer(s) replayed from the lock
CONFLICTS: 3 open (2 contradiction, 1 duplication) in 1 group(s)
  CF-000001 contradiction  N-000017 specs/sharing.md:5 ↔ N-000042 specs/sharing.md:22
    "quote from N-000017" ↔ "quote from N-000042"
    rationale: both set the lifetime of a share link
  CF-000002 contradiction  N-000042 specs/sharing.md:22 ↔ N-000051 specs/api.md:9
    "quote from N-000042" ↔ "quote from N-000051"
    rationale: both set the lifetime of a share link
  CF-000003 duplication  N-000017 specs/sharing.md:5 ↔ N-000063 specs/api.md:14
    "quote from N-000017" ↔ "quote from N-000063"
    rationale: the same rule, written twice
closed this run: 1 re-judged, 0 by a deleted member
ATTENTION: 2 item(s) — see .sdd/review.jsonl
exit 3
