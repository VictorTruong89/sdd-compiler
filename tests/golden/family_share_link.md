## Family: share_link

**Also called:** shared link

### L1 (4)
- N-000001 ✓ Owners can create a share link for a file they own.
- N-000002 ✓ A share link expires 30 days after it is created.
- N-000003 ✗ Visitors who open an expired share link see a "link expired" page.
- N-000005 ✗ When a file is deleted, its share links must stop working.

### L2 (1)
- N-000007 ✓ LinkService owns share links.

### L3 (2)
- N-000009 ✓ GET /s/{token} returns 200 with the file stream when the token is valid
- N-000010 ✓ and 404 when it is expired or unknown.

### L4 (1)
- N-000011 ✓ A share link record stores token, file_id, created_at and expires_at.

### L5 (1)
- N-000012 ✓ expires_at is set to created_at plus 30 days when the link is created.

### C (1)
- N-000004 ✓ Share links must never reveal the owner's email address.

### V (1)
- N-000013 ✓ Test: a link created 31 days ago returns 404.

### In scope from elsewhere (1)
- N-000014 ✓ Every public endpoint must respond within 300 ms.

**Related families:** file
