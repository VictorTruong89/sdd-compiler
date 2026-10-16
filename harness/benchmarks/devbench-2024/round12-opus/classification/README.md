# Round 12: classifying the hidden tests of six more projects

Done 2026-10-14, **before any Opus run of round 12**, by one reader (the assistant), not checked by a
second reader. Same method and classes as round 9 (`../../TRIAL.md` §10.1): each hidden test read
against the four Markdown documents in the task's `spec/` and the seed files.

| Class | Meaning |
|---|---|
| S | names and expected behaviour stated in the specification or seed data |
| U | names stated; the expected value or behaviour is not (a fair reading may differ) |
| R | needs a name, default, key or exact string the specification does not give |
| C | expects a value that contradicts the specification |

The classes are in `../../test-classification.json`; the files here are the per-project inputs added
with `add_classes.py <project> <project>.json`. Each project was checked with
`score_by_class.py --check <project> <r6 reference run verifier>`: no id missing, none extra.

| Project | S | U | R | C | All |
|---|---|---|---|---|---|
| chakin | 0 | 0 | 2 | 0 | 2 |
| particle-swarm-optimization | 6 | 0 | 0 | 0 | 6 |
| readtime | 2 | 0 | 10 | 0 | 12 |
| geotext | 5 | 3 | 1 | 0 | 9 |
| hone | 11 | 1 | 0 | 0 | 12 |
| hybrid-images | 3 | 14 | 1 | 2 | **20** |
| **six projects** | **27** | **18** | **14** | **2** | **61** |
| with lice, arxiv-digest, stocktrends (round 9) | 60 | 33 | 47 | 3 | 143 |

## `hybrid-images` has 20 hidden tests, not 19

The reference run (`r6-oracle-hybrid-images`) collects 20 tests and passes 12, so it fails **8**, not
7. The builder counted 19 because it matched `def test_`, and the acceptance test is named `test`
(`acceptance_tests/acceptance_test.py`). The handover and `clean-tasks-check.json` (`tests_total: 19`)
carry the miscount; `build_clean_task.py` is fixed in round 12 to count `def test`.

The 8 tests the reference fails (all with `ValueError: setting an array element with a sequence`
under today's NumPy, TRIAL §8):

| Test | Class |
|---|---|
| `TestCrossCorrelation2D::test_identity_filter_grey` | S |
| `TestCrossCorrelation2D::test_mean_filter_grey` | U |
| `TestCrossCorrelation2D::test_mean_filter_rect_grey` | U |
| `TestCrossCorrelation2D::test_big_filter_grey` | U |
| `TestConvolve2D::test_identity_filter_grey` | S |
| `TestConvolve2D::test_mean_filter_grey` | U |
| `TestConvolve2D::test_mean_filter_rect_grey` | U |
| `TestConvolve2D::test_big_filter_grey` | U |

The reference passes S 1 / 3, U 8 / 14, R 1 / 1, C 2 / 2, so the 12-test basis (the tests the
reference passes) holds S 1, U 8, R 1, C 2.

## Doubtful calls (judgement, stated so they can be re-read)

- **`particle-swarm-optimization`, all S.** `test_sphere` relies on the standard sphere function
  (sum of squares), named but not written out. `test_evaluate` relies on PSO's personal-best update,
  which the specification implies through the attributes `pos_best_i` and `err_best_i` but does not
  state. Both could be argued U.
- **`readtime`: `test_custom_wpm_html` and `test_custom_wpm_markdown` are S** because they check only
  `result.wpm` (a constructor parameter, default 265 stated). The other ten all need the strings
  `N min` / `N min read`, the rounding rule, the per-image time or the error message, none given.
  Also noted: the architecture lists `seconds()` as a method, the UML class lists `+seconds` as a
  member; the tests read it as an attribute.
- **`geotext`: nationalities kept as written in the text** (`'Japanese'`, data file is lower case)
  read as stated by "nationality terms found in the text"; S. `test_data_loading` needs the instance
  attribute `index`, not named anywhere: R.
- **`hone`: the conversion tests are S** because the expected outputs are the seed files and Python's
  `csv` module reproduces their odd quoted keys exactly (checked by running `csv.reader` on the three
  seed CSVs). The nesting rule ("birth day" → `birth.day`) is shown by the schema example, not written
  as a rule. `test_error_handling` (any exception on a missing file) is U: not stated, though a plain
  `open()` raises.
- **`hybrid-images`: two C calls.** `gaussian_blur_kernel_2d(1, 7, 3)` is expected as 7 rows by 3
  columns, so the tests take `width` as the number of rows. The specification never states the array
  order; C rests on the plain meaning of width and height ("Note that width and height are
  different" could be read either way). The identity-kernel tests are S because they hold for any
  same-size output whatever border rule is used; the other filter tests are U because the comparison
  is with `cv2.filter2D(..., BORDER_CONSTANT)` (zero padding), which is not stated.
- **`chakin`: both R.** Both tests patch `chakin.downloader.urlretrieve`; the specification never
  names it (it lists `six` as a dependency, a hint at most) and does not say `download()` returns the
  saved path.
