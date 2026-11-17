"""Make round 28's case005 spec: plant the kept conflicts and remove the kept gaps in a copy of case005's public spec.
No model call.

    python3 notes/plant.py work/spec-planted C01 ... G01 ...       (from the trial folder)

Round 28, case005 (copied from ../r21-zero2repo-case016-conflicts-gaps/notes/plant.py; method unchanged,
new anchors for case005):
  - **Conflict** C..: one edit adds side B in **one** place, in the spec's own voice and with no marker,
    so the other place still states side A. `PHRASES[item] = (A phrase, B phrase)`; after planting each
    must occur exactly once.
  - **Gap** G..: every place that states the fact is edited once, the smallest span that removes it and
    keeps the sentence readable; no marker and no "unspecified" wording is added. `KEY[item]` lists
    phrases that must occur nowhere after removal.
Every `old` string must occur exactly once in its file, so an edit never applies silently to the wrong
place. A bullet left empty by removals is dropped. Zero2Repo has no licence file: the output stays in
git-ignored `work/`; this script holds only the short anchors and planted sentences.
"""
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLIC = HERE.parents[2] / "benchmarks/zero2repo/download/Zero2Repo/benchmark/cases/case005/public"
PRD, IC = "Full_PRD.md", "Interface_Contract.md"

# item -> list of (file, old, new)
EDITS = {
    # ---------------- conflicts: side B added in one place
    "C01": [(IC, "- `headers` accepts a sequence of `(name, value)` pairs.",
             "- `headers` accepts a sequence of `(name, value)` pairs. A `Content-Length` value longer than 16 digits is refused.")],
    "C02": [(PRD, "Each non-empty data event is encoded as one HTTP/1.1 chunk (hexadecimal size line, the payload, then CRLF).",
             "Each non-empty data event is encoded as one HTTP/1.1 chunk (hexadecimal size line, the payload, then CRLF). "
             "A received size line may carry up to 64 hexadecimal digits.")],
    "C03": [(IC, "When it is omitted, the PRD default applies; when it is given, that value is used.",
             "When it is omitted, the limit is 8 kibibytes; when it is given, that value is used.")],
    "C04": [(PRD, "or when header names, header values, or request targets break the FP-01 rules.",
             "or when header names, header values, or request targets break the FP-01 rules. A continuation line "
             "(a header line that begins with a space or tab) is refused.")],
    "C05": [(IC, "It does not raise for illegal peer bytes (those are reported by `next_event`);",
             "It does not raise for illegal peer bytes (those are reported by `next_event`; every received line must "
             "end with a carriage return and line feed);")],
    "C06": [(IC, "Illegal peer bytes raise `RemoteProtocolError`.",
             "Illegal peer bytes raise `RemoteProtocolError`. A received status line with no reason phrase after its "
             "status code is illegal.")],
    "C07": [(IC, "Returns the bytes to transmit as a bytes-like object (`bytes`, `bytearray`, or `memoryview`).",
             "Returns the bytes to transmit as a bytes-like object (`bytes`, `bytearray`, or `memoryview`). Headers "
             "are written in the order of the event’s header list.")],
    "C08": [(PRD, "recovers, for each header in order, the name exactly as the caller spelled it, paired with the value.",
             "recovers, for each header in order, the name exactly as the caller spelled it, paired with the value. "
             "The raw-items view is for the caller only; header names are sent in lowercase.")],
    "C09": [(PRD, "The bytes after each chunk’s data must be exactly CRLF; anything else is refused.",
             "Whitespace after the chunk size is refused. The bytes after each chunk’s data must be exactly CRLF; "
             "anything else is refused.")],
    "C10": [(PRD, "is stored as `transfer-encoding` with the lowercase value `chunked`.",
             "is stored as `transfer-encoding` with the lowercase value `chunked`. When an event carries both "
             "framing headers, the `Content-Length` decides how the body is framed.")],
    "C11": [(PRD, "No data is sent and end-of-message completes an empty body.",
             "No data is sent and end-of-message completes an empty body. A response with `Content-Length: 0` is "
             "sent without that header, since its body is empty.")],
    "C12": [(PRD, "| **Keep-alive** | Reusing one connection for another request/response cycle after both sides reach DONE. Specified in FP-04. |",
             "| **Keep-alive** | Reusing one connection for another request/response cycle after both sides reach DONE. "
             "Any `Connection` value that contains `close` turns it off. Specified in FP-04. |")],
    "C13": [(IC, "| `client_is_waiting_for_100_continue` | Exactly `bool`: whether the client of this conversation is waiting for 100-continue (PRD FP-07). |",
             "| `client_is_waiting_for_100_continue` | Exactly `bool`: whether the client of this conversation is waiting "
             "for 100-continue (PRD FP-07); any request with `Expect: 100-continue` sets it, whatever its HTTP version. |")],
    "C14": [(IC, "| `they_are_waiting_for_100_continue` | Exactly `bool`: whether the peer is a client waiting for 100-continue (PRD FP-07). |",
             "| `they_are_waiting_for_100_continue` | Exactly `bool`: whether the peer is a client waiting for 100-continue "
             "(PRD FP-07). The `Expect` value must be exactly the lowercase token `100-continue`. |")],
    "C15": [(PRD, "pulls those informational-response events in order and remains able to send the request body.",
             "pulls those informational-response events in order and remains able to send the request body. The client "
             "stays waiting for 100-continue until the server answers; its own body events do not end the wait.")],
    "C16": [(PRD, "A 2xx on CONNECT is a final response event.",
             "A 2xx on CONNECT is a final response event. Only status 200 accepts a CONNECT proposal; other 2xx "
             "statuses deny it.")],
    "C17": [(IC, "- `error_status_hint` — attribute, exactly of type `int`: the suggested status (PRD FP-05).",
             "- `error_status_hint` — attribute, exactly of type `int`: the suggested status (PRD FP-05). An incomplete "
             "event over the size limit suggests 413.")],
    "C18": [(PRD, "Repeated `Content-Length` values, whether given as separate headers",
             "Repeated `Transfer-Encoding: chunked` headers collapse to one, like repeated equal `Content-Length` "
             "values. Repeated `Content-Length` values, whether given as separate headers")],
    "C19": [(PRD, "A server that tries to send a request event is refused as a local protocol error.",
             "A server that tries to send a request event is refused as a local protocol error. A server that has not "
             "received a request cannot send a response.")],
    "C20": [(PRD, "A header value that breaks the value rule above is refused.",
             "A header value that breaks the value rule above is refused. Control bytes other than tab are refused in "
             "header values.")],
    "C21": [(PRD, "then the headers and a blank line. An informational response other than",
             "then the headers and a blank line. A response to HEAD is written with no framing headers. An "
             "informational response other than")],
    # ---------------- gaps: every statement of the fact removed
    "G01": [(PRD, "for that violation. The default is 400. |", "for that violation. |"),
            (PRD, "Every protocol error carries a suggested status. The default is 400. Three specified exceptions:",
             "Every protocol error carries a suggested status. Three specified values:")],
    "G05": [(PRD, "- When the first stored byte where a request line (server role) or status line (client role, after sending a request) "
                  "is expected is a space or a control byte (byte value below 33), the pull fails at once as a remote protocol error. "
                  "It does not wait for a line ending.\n", "")],
    "G06": [(PRD, " Bytes held while a pull is paused (FP-04, FP-07) are not counted against the limit until a later cycle starts parsing them.", "")],
    "G09": [(PRD, " An empty data event encodes as no bytes.", "")],
    "G14": [(PRD, " Feeding an empty chunk never fails.", ""),
            (PRD, "further pulls also yield a connection-closed event, and feeding further empty chunks remains allowed.",
             "further pulls also yield a connection-closed event.")],
    "G16": [(PRD, "the peer HTTP version is retained for the rest of this connection; later sends on the same cycle do not change it, "
                  "and it stays after the next cycle is started (FP-04).",
             "the peer HTTP version is retained; later sends on the same cycle do not change it."),
            (PRD, " The peer HTTP version recorded in FP-02 is still present after the cycle starts.", "")],
    "G21": [(PRD, "- Generating a table of reason phrases. A caller who wants a reason phrase supplies one; the product does not look one up.\n", ""),
            (PRD, " The product never invents a reason phrase.", ""),
            (PRD, "followed by the reason the caller supplied, or an empty reason when none was supplied,",
             "followed by the reason the caller supplied,")],
    "G22": [(PRD, "- Bytes received from a peer that is in MUST_CLOSE are a remote protocol error.\n", "")],
    "G31": [(PRD, " (and drops any `keep-alive` token from it)", "")],
    "G33": [(PRD, " It produces no bytes and doing it twice in a row has the same result.", " It produces no bytes.")],
    "G34": [(PRD, "when it is in IDLE, DONE, MUST_CLOSE, or CLOSED; that side becomes CLOSED. Sending it again when already CLOSED is allowed (idempotent).",
             "when it is in IDLE, DONE, or MUST_CLOSE; that side becomes CLOSED.")],
    "G47": [(PRD, " Header order is preserved as the caller gave it (sending applies the Host-first rule in FP-02).", "")],
    "G48": [(PRD, " (whitespace around the commas is allowed)", "")],
    "G49": [(PRD, " A status that is an integer-valued enumeration member is stored as a plain integer.", ""),
            (IC, " The stored value is exactly of type `int`.", "")],
}

# conflict item: (A phrase, B phrase); each must occur exactly once after planting
PHRASES = {
    "C01": ("Every value of at most 18 digits is accepted", "longer than 16 digits is refused"),
    "C02": ("from 16 to 32 inclusive", "up to 64 hexadecimal digits"),
    "C03": ("at least 14 kibibytes and less than 18 kibibytes", "the limit is 8 kibibytes"),
    "C04": ("Obsolete line folding (RFC 7230 §3.2.4) is accepted", "A continuation line (a header line that begins with a space or tab) is refused"),
    "C05": ("use a lone line feed", "every received line must end with a carriage return and line feed"),
    "C06": ("omits the reason phrase is accepted", "with no reason phrase after its status code is illegal"),
    "C07": ("the Host header is written before every other header", "Headers are written in the order of the event’s header list"),
    "C08": ("the original name casing from construction", "header names are sent in lowercase"),
    "C09": ("optionally followed by spaces or tabs", "Whitespace after the chunk size is refused"),
    "C10": ("transfer-encoding wins", "the `Content-Length` decides how the body is framed"),
    "C11": ("including when N is 0", "is sent without that header, since its body is empty"),
    "C12": ("as a whole element of the comma-separated `Connection` value", "Any `Connection` value that contains `close` turns it off"),
    "C13": ("on an HTTP/1.0 request does not set either flag", "`Expect: 100-continue` sets it, whatever its HTTP version"),
    "C14": ("contains the token `100-continue` (matched case-insensitively)", "must be exactly the lowercase token `100-continue`"),
    "C15": ("when the client sends any data event or its end-of-message", "its own body events do not end the wait"),
    "C16": ("whose status is in the 2xx range", "Only status 200 accepts a CONNECT proposal"),
    "C17": ("with suggested status 431", "over the size limit suggests 413"),
    "C18": ("is refused with suggested status 501, even when both values are `chunked`", "Repeated `Transfer-Encoding: chunked` headers collapse to one"),
    "C19": ("A server in IDLE may send a final response event", "A server that has not received a request cannot send a response"),
    "C20": ("including other control bytes and non-ASCII bytes", "Control bytes other than tab are refused in header values"),
    "C21": ("writes the same framing headers it would have used for GET", "A response to HEAD is written with no framing headers"),
}

# gap item: phrases that must occur nowhere in the gapped spec (also checked over the export)
KEY = {
    "G01": ["default is 400", "is 400"], "G05": ["does not wait for a line ending", "byte value below 33"],
    "G06": ["are not counted against the limit"], "G09": ["empty data event encodes as no bytes"],
    "G14": ["never fails", "further empty chunks remains allowed"],
    "G16": ["still present after the cycle starts", "stays after the next cycle", "for the rest of this connection"],
    "G21": ["never invents", "empty reason when none", "table of reason phrases", "does not look one up"],
    "G22": ["peer that is in MUST_CLOSE"], "G31": ["drops any `keep-alive` token"],
    "G33": ["twice in a row"], "G34": ["(idempotent)", "already CLOSED is allowed"],
    "G47": ["preserved as the caller gave it"], "G48": ["whitespace around the commas"],
    "G49": ["enumeration member is stored as a plain integer", "The stored value is exactly of type `int`"],
}

# The items kept after step 1 (ANSWER_KEY.md), for the scripts that score them. Filled after selection.
KEPT_C: list[str] = "C01 C02 C03 C04 C05 C06 C09 C10 C11 C12 C13 C14 C15 C16 C18 C20 C21".split()
KEPT_G: list[str] = "G06 G09 G14 G16 G21 G22 G33 G34 G47 G48 G49".split()
KEPT = KEPT_C + KEPT_G
FIND: dict[str, tuple[str | None, str | None]] = {"C11": (None, "is sent without that header")}   # node text where the atomizer reworded a side (step 3, recall)


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
    for f in out.glob("*.md"):   # a bullet emptied by removals is dropped
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
