# Specification conflicts

Files: PRD = `spec/Full_PRD.md`, IC = `spec/Interface_Contract.md`.

## 1. Content-Length maximum digit count
- IC, Events: "A `Content-Length` value longer than 16 digits is refused."
- PRD, FP-01 Boundary: "Every value of at most 18 digits is accepted"; the limit is between 18 and 32.
- A 17- or 18-digit Content-Length would be both refused and accepted.

## 2. Default incomplete-event size limit
- IC, Connection signature: "When it is omitted, the limit is 8 kibibytes".
- PRD, FP-05: the default is "at least 14 kibibytes and less than 18 kibibytes".
- The default cannot be 8 KiB and also at least 14 KiB.

## 3. Lone line feed line endings
- IC, `receive_data`: "every received line must end with a carriage return and line feed".
- PRD, FP-02 Normal: "Received header blocks that use a lone line feed, or a mix ... are accepted."
- A header block with bare-LF endings is both illegal and accepted.

## 4. Status line without reason phrase
- IC, `next_event`: "A received status line with no reason phrase after its status code is illegal."
- PRD, FP-02 Normal: "A response status line that omits the reason phrase is accepted and the reason is empty."
- The same received status line cannot be both illegal and accepted.

## 5. Obsolete line folding / continuation lines
- PRD, FP-02 Normal: obs-fold is "accepted when reading headers".
- PRD, FP-02 Boundary: "A continuation line (a header line that begins with a space or tab) is refused."
- A received continuation line cannot be both accepted and refused.

## 6. Control bytes in header values
- PRD, FP-01 Normal: header values may contain any byte except NUL, CR, LF, FF, VT, "including other control bytes".
- PRD, FP-01 Boundary: "Control bytes other than tab are refused in header values."
- A value containing, e.g., byte 0x01 is both allowed and refused.

## 7. Repeated Transfer-Encoding headers
- PRD, FP-01 Normal: "Repeated `Transfer-Encoding: chunked` headers collapse to one".
- PRD, FP-01 Boundary and FP-05: "A second `Transfer-Encoding` header is refused with suggested status 501, even when both values are `chunked`."
- Two `chunked` headers cannot both collapse to one and be refused.

## 8. Which framing header wins when both are present
- PRD, FP-01 Normal: "When an event carries both framing headers, the `Content-Length` decides how the body is framed."
- PRD, FP-03 (response): "transfer-encoding wins: Content-Length is not sent".
- A response with both headers cannot be framed by Content-Length and by chunked encoding.

## 9. Content-Length: 0 on a response
- PRD, FP-03: "The `Content-Length` header is kept on the wire, including when N is 0."
- PRD, FP-03: "A response with `Content-Length: 0` is sent without that header".
- The header is both kept and omitted for the same response.

## 10. Framing headers on a response to HEAD
- PRD, FP-02: "A response to HEAD is written with no framing headers."
- PRD, FP-03: "A server answering HEAD writes the same framing headers it would have used for GET: chunked when the peer is HTTP/1.1".
- A HEAD response cannot both have no framing headers and have `Transfer-Encoding: chunked`.

## 11. Maximum chunk-size digits
- PRD, FP-03 (chunked request framing): "A received size line may carry up to 64 hexadecimal digits."
- PRD, FP-03 (chunk-size line rule): at most a fixed number of digits "from 16 to 32 inclusive".
- A 33–64 digit size line is both accepted and refused.

## 12. Whitespace after chunk size
- PRD, FP-03: chunk-size line is the number, optional extension, "optionally followed by spaces or tabs, then the line ending".
- PRD, FP-03 Boundary: "Whitespace after the chunk size is refused."
- Trailing whitespace after the size is both allowed and refused.

## 13. Which statuses accept CONNECT
- PRD, FP-07 Normal: for CONNECT, "acceptance is a final response whose status is in the 2xx range"; "a 2xx response accepts CONNECT".
- PRD, FP-07 Boundary: "Only status 200 accepts a CONNECT proposal; other 2xx statuses deny it."
- A 204 response to CONNECT would be both an acceptance and a denial.

## 14. Expect: 100-continue on HTTP/1.0 requests
- IC, `client_is_waiting_for_100_continue`: "any request with `Expect: 100-continue` sets it, whatever its HTTP version."
- PRD, FP-07: "An `Expect: 100-continue` header on an HTTP/1.0 request does not set either flag."
- An HTTP/1.0 request with that header both sets and does not set the flag.

## 15. Case sensitivity of the Expect token
- IC, `they_are_waiting_for_100_continue`: "The `Expect` value must be exactly the lowercase token `100-continue`."
- PRD, FP-07: the token `100-continue` is "matched case-insensitively".
- `Expect: 100-Continue` both sets and does not set the flag.
