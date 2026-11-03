# Notes

Package: `src/optlyn` (pure Python, no dependencies, no build step). Behaviour follows the
Interface Contract and PRD in `spec/`; where the two disagree (28 unsettled contradictions) I chose
as follows. Where the choice is not listed the spec was consistent.

| CF | Disagreement | Built |
|---|---|---|
| 010 | omitted repeatable option: absent vs `()` | `()` |
| 016/092/100/107 | clamp with open bounds | IntRange: adjacent integer inside range; FloatRange: clamp with an open bound raises `DeclarationError` at construction |
| 034/072 | env vs default map precedence | command line > environment > default map > declared default |
| 047 | epilog position | printed last, after all other sections |
| 048 | omitted count option | `0` |
| 063 | subcommand short help | first sentence of first paragraph, cut with `...` at 45 characters |
| 087 | default max content width | 80 |
| 088 | envvar list | first name that is set wins |
| 115 | default option metavar | type name upper-cased (`--count INTEGER`) |
| 128 | pause when not interactive | does not block, prints its message |
| 129 | app dir | `$XDG_CONFIG_HOME` honoured, else `~/.config` |
| 134 | confirmation mismatch | ask the pair again (EOF aborts) |
| 136 | DateTime custom formats | replace the defaults |
| 151/157 | boolean env/text junk value | usage error (blank env value deactivates a flag) |
| 154 | isolated_filesystem | removed on exit when no `temp_dir`; kept when `temp_dir` given |
| 155 | callback for omitted parameter | callback still runs |
| 156 | form feed in help | text after it is dropped |
| 158 | DateTime several matches | first matching format wins |
| 159 | prompt conversion failure | re-ask until valid or EOF |
| 160 | `~` in Path | not expanded |
| 161 | completion options | options listed for empty token and for `-` prefixes (after subcommands) |
| 162 | show_default for False flag | hidden |
| 163 | Choice case | case-sensitive by default |

Other choices: declaration errors raise `DeclarationError` (subclass of TypeError, ValueError,
RuntimeError). A group with no args and `no_args_is_help` prints help to stderr, exit 2.
`CliRunner(capture="fd")` merges combined output as stdout then stderr.
