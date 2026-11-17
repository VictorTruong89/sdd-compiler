# Specification conflicts

Files: PRD = spec/Full_PRD.md, IC = spec/Interface_Contract.md.

## 1. Content-Length maximum digits
- IC, Events: "A `Content-Length` value longer than 16 digits is refused."
- PRD, FP-01 Boundary: "Every value of at most 18 digits is accepted"; the maximum is 18 to 32.
- A 17- or 18-digit value cannot be both refused and accepted.

## 2. Default incomplete-event size limit
- IC, Connection signature: "When it is omitted, the limit is 8 kibibytes".
- PRD, FP-05: the default is "at least 14 kibibytes and less than 18 kibibytes".
- The default cannot be 8 KiB and also at least 14 KiB.

## 3. Maximum chunk-size digits
- PRD, FP-03 Normal (chunked bullet): "A received size line may carry up to 64 hexadecimal digits."
- PRD, FP-03 Normal (chunk-size line bullet) and Boundary: at most a fixed number from 16 to 32 digits; more is refused.
- A 33 to 64 digit size line cannot be both accepted and refused.

## 4. `Expect: 100-continue` on HTTP/1.0 requests
- IC, `client_is_waiting_for_100_continue`: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- PRD, FP-07: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- For an HTTP/1.0 request the flag cannot be both set and not set.

## 5. Case of the `100-continue` token
- IC, `they_are_waiting_for_100_continue`: "The `Expect` value must be exactly the lowercase token `100-continue`."
- PRD, FP-07: the token is "matched case-insensitively".
- `Expect: 100-Continue` cannot both set and not set the flag.

## 6. Status line with no reason phrase
- IC, `next_event`: "A received status line with no reason phrase after its status code is illegal."
- PRD, FP-02 Normal: "A response status line that omits the reason phrase is accepted and the reason is empty."
- The same received line cannot be both illegal and accepted.

## 7. Lone LF line endings
- IC, `receive_data`: "every received line must end with a carriage return and line feed".
- PRD, FP-02 Normal: header blocks that use a lone line feed, or a mix, "are accepted".
- A lone-LF line cannot be both refused and accepted.

## 8. Obsolete line folding
- PRD, FP-02 Normal: obsolete line folding is accepted when reading headers; continuation lines are joined.
- PRD, FP-02 Boundary: "A continuation line (a header line that begins with a space or tab) is refused."
- A continuation line cannot be both joined and refused.

## 9. Which 2xx status accepts CONNECT
- PRD, FP-07 Normal: for CONNECT, "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT".
- PRD, FP-07 Boundary: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- A 2xx other than 200, such as 204, cannot be both acceptance and denial.

## 10. Do the client's body events end the 100-continue wait?
- PRD, FP-07 Normal, first bullet: the client stays waiting "until the server answers; its own body events do not end the wait."
- PRD, FP-07 Normal, third bullet: the flags turn off "when the client sends any data event or its end-of-message."
- Client body events cannot both end the wait and not end it.

## 11. `Content-Length: 0` on a response
- PRD, FP-03 Normal: "The `Content-Length` header is kept on the wire, including when N is 0."
- PRD, FP-03 Normal (empty-body bullet): "A response with `Content-Length: 0` is sent without that header."
- The header cannot be both kept and dropped.

## 12. Response to HEAD: framing headers
- PRD, FP-02 Normal: "A response to HEAD is written with no framing headers."
- PRD, FP-03 Normal: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1".
- A HEAD response cannot have no framing headers and also `Transfer-Encoding: chunked`.

## 13. Both framing headers: which one decides
- PRD, FP-01 Normal: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- PRD, FP-03 Normal: for a response with both, "transfer-encoding wins: Content-Length is not sent".
- Framing cannot be decided by both headers for a response carrying both.

## 14. Repeated `Transfer-Encoding: chunked`
- PRD, FP-01 Normal: "Repeated `Transfer-Encoding: chunked` headers collapse to one".
- PRD, FP-01 Boundary (also FP-05): "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- Two `Transfer-Encoding: chunked` headers cannot both collapse to one and be refused.

## 15. Control bytes in header values
- PRD, FP-01 Normal: values may contain any byte except NUL, CR, LF, FF and VT, "including other control bytes".
- PRD, FP-01 Boundary: "Control bytes other than tab are refused in header values."
- A value with a control byte such as 0x01 cannot be both allowed and refused.

## 16. Whitespace after a chunk size
- PRD, FP-03 Normal: a chunk-size line is optionally followed by a chunk extension, "optionally followed by spaces or tabs, then the line ending".
- PRD, FP-03 Boundary: "Whitespace after the chunk size is refused."
- A chunk-size line with trailing spaces cannot be both valid and refused.
