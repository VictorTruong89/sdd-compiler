# Specification conflicts

## 1. Maximum Content-Length digits
- Interface_Contract.md, "Events" (headers bullet): "A `Content-Length` value longer than 16 digits is refused."
- Full_PRD.md, FP-01 Boundary: "Every value of at most 18 digits is accepted; the maximum digit count is ... from 18 to 32 inclusive".
- A 17- or 18-digit value cannot be both refused and accepted.

## 2. Default incomplete-event size limit
- Interface_Contract.md, `Connection` signature: "When it is omitted, the limit is 8 kibibytes".
- Full_PRD.md, FP-05: the default is "at least 14 kibibytes and less than 18 kibibytes".
- 8 KiB is outside the 14–18 KiB range, so the default cannot satisfy both.

## 3. Maximum chunk-size digits
- Full_PRD.md, FP-03 chunked request framing: "A received size line may carry up to 64 hexadecimal digits."
- Full_PRD.md, FP-03 chunk-size rule: the maximum is "from 16 to 32 inclusive", and more digits than that maximum is refused (Boundary).
- A 33–64 digit size line cannot be both accepted and refused.

## 4. Whitespace after chunk size
- Full_PRD.md, FP-03 chunk-size rule: the size is "optionally followed by spaces or tabs, then the line ending".
- Full_PRD.md, FP-03 Boundary: "Whitespace after the chunk size is refused."
- Trailing whitespace after a chunk size cannot be both accepted and refused.

## 5. Both Content-Length and Transfer-Encoding: which decides framing
- Full_PRD.md, FP-01 Normal: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- Full_PRD.md, FP-03 Normal (response): "constructed with both `Transfer-Encoding: chunked` and `Content-Length`, transfer-encoding wins: Content-Length is not sent".
- The same response framing cannot be decided by both headers.

## 6. Repeated Transfer-Encoding headers
- Full_PRD.md, FP-01 Normal: "Repeated `Transfer-Encoding: chunked` headers collapse to one".
- Full_PRD.md, FP-01 Boundary and FP-05: "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- Two `chunked` headers cannot be both collapsed and refused.

## 7. Control bytes in header values
- Full_PRD.md, FP-01 Normal: values "may contain any byte other than NUL, CR, LF, form feed, and vertical tab, including other control bytes".
- Full_PRD.md, FP-01 Boundary: "Control bytes other than tab are refused in header values."
- A control byte such as 0x01 cannot be both allowed and refused.

## 8. Obsolete line folding
- Full_PRD.md, FP-02 Normal: obsolete line folding is accepted when reading headers, and continuation lines are joined.
- Full_PRD.md, FP-02 Boundary: "A continuation line (a header line that begins with a space or tab) is refused."
- A continuation line cannot be both accepted and refused.

## 9. Status line without reason phrase
- Full_PRD.md, FP-02 Normal: "A response status line that omits the reason phrase is accepted and the reason is empty."
- Interface_Contract.md, `next_event()`: "A received status line with no reason phrase after its status code is illegal" and raises `RemoteProtocolError`.
- The same received line cannot be both accepted and illegal.

## 10. Lone line feed line endings
- Full_PRD.md, FP-02 Normal: header blocks using lone LF, or a mix of CRLF and lone LF, are accepted.
- Interface_Contract.md, `receive_data`: "every received line must end with a carriage return and line feed".
- A lone-LF line cannot be both accepted and illegal.

## 11. Expect: 100-continue on HTTP/1.0 requests
- Full_PRD.md, FP-07: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- Interface_Contract.md, `client_is_waiting_for_100_continue`: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- An HTTP/1.0 request with that header cannot both set and not set the flag.

## 12. Case sensitivity of the 100-continue token
- Full_PRD.md, FP-07: the `Expect` token is "matched case-insensitively".
- Interface_Contract.md, `they_are_waiting_for_100_continue`: "The `Expect` value must be exactly the lowercase token `100-continue`."
- `Expect: 100-Continue` cannot both set and not set the flag.

## 13. When the 100-continue wait ends
- Full_PRD.md, FP-07 (first bullet): "its own body events do not end the wait."
- Full_PRD.md, FP-07 (waiting flags bullet): the flags turn off "when the client sends any data event or its end-of-message".
- Client body events cannot both end the wait and not end it.

## 14. Which 2xx statuses accept CONNECT
- Full_PRD.md, FP-07 Normal: for CONNECT, "acceptance is a final response whose status is in the 2xx range".
- Full_PRD.md, FP-07 Boundary: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- A 204 response cannot be both an acceptance and a denial.

## 15. Content-Length: 0 on a response
- Full_PRD.md, FP-03 (response Content-Length bullet): "The `Content-Length` header is kept on the wire, including when N is 0."
- Full_PRD.md, FP-03 (empty-body bullet): "A response with `Content-Length: 0` is sent without that header."
- The header cannot be both kept and omitted.

## 16. Framing headers on a response to HEAD
- Full_PRD.md, FP-02 Normal: "A response to HEAD is written with no framing headers."
- Full_PRD.md, FP-03: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1".
- A HEAD response cannot both have no framing headers and carry `Transfer-Encoding: chunked`.
