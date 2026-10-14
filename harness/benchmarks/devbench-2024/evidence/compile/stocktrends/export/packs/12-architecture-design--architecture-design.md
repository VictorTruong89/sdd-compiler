# Pack 12 — sdd/specs/architecture_design.md · Architecture Design
blocks 22 · nodes 20 (requirement 20) · AC labels: none

## Text
# Architecture Design

Below is a text-based representation of the file tree.
↳ no node

```bash
├── acceptance_tests
│   ├── HOOLI.csv
│   ├── hooli_linebreak_3.csv
│   ├── hooli_renko_4.csv
│   ├── __init__.py
│   └── test_indicators.py
├── examples
│   ├── demo.py
│   ├── demo.sh
│   └── HDFCLIFE.csv
├── stocktrends
│   ├── indicators.py
│   └── __init__.py
├── unit_tests
│   ├── HDFCLIFE.csv
│   ├── HOOLI.csv
│   ├── test_instrument.py
│   ├── test_pnf.py
│   └── test_renko.py
```
↳ N-000047 requirement · MUST · L2

Examples:
↳ no node

To generate indicators, run `sh ./examples/demo.sh`. An example of the script `demo.sh` is shown as follows.
↳ no node

```bash
#! /bin/bash

# Run the demo
python examples/demo.py 
```
↳ N-000048 requirement · MUST · L2

`indicators.py`:
↳ no node

- class Instrument(df): initialize the model structure and parameters.
↳ N-000049 requirement · MUST · L2

    - _validate_df(): validates the DataFrame to ensure it has the required OHLC columns.
↳ N-000050 requirement · MUST · L2

- class Renko(df): initialize the model structure and parameters.
↳ N-000051 requirement · MUST · L2

    - get_ohlc_data(): retrieves the OHLC (Open, High, Low, Close) data based on the chart type.
↳ N-000052 requirement · MUST · L2

    - period_close_bricks(): calculates the period close bricks based on the given brick size.
↳ N-000053 requirement · MUST · L2

    - shift_bricks(): shifts the bricks in the indicator dataframe based on the difference between the current close price and the previous close price.
↳ N-000054 requirement · MUST · L2

- class LineBreak(df): initialize the model structure and parameters.
↳ N-000055 requirement · MUST · L2

    - uptrend_reversal(close): determines if a stock is experiencing an uptrend reversal.
↳ N-000056 requirement · MUST · L2

    - downtrend_reversa(close): determines if a downtrend reversal has occurred based on the given close price.
↳ N-000057 requirement · MUST · L2

    - get_ohlc_data(): retrieves the OHLC (Open, High, Low, Close) data from the DataFrame and performs trend analysis.
↳ N-000058 requirement · MUST · L5 ; N-000059 requirement · MUST · L5

- class PnF(df): initialize the model structure and parameters.
↳ N-000060 requirement · MUST · L5

    - brick_size(): returns the brick size used for the indicator.
↳ N-000061 requirement · MUST · L4

    - get_state(uptrend_p1, bricks): get the state of the trend based on the given parameters.
↳ N-000062 requirement · MUST · L5

    - roundit(x. base): rounds the input `x` to the nearest multiple of `base` and returns the result as an integer.
↳ N-000063 requirement · MUST · L5 ; N-000064 requirement · MUST · L4

    - get_ohlc_data(source): retrieves the PnF data in the form of an OHLC DataFrame.
↳ N-000065 requirement · MUST · L4

    - get_bar_ohlc_data(source): retrieves bar OHLC (Open, High, Low, Close) data.
↳ N-000066 requirement · MUST

## Claims to implement
- [N-000047] requirement · MUST · L2 — ├── acceptance_tests
    │   ├── HOOLI.csv
    │   ├── hooli_linebreak_3.csv
    │   ├── hooli_renko_4.csv
    │   ├── __init__.py
    │   └── test_indicators.py
    ├── examples
    │   ├── demo.py
    │   ├── demo.sh
    │   └── HDFCLIFE.csv
    ├── stocktrends
    │   ├── indicators.py
    │   └── __init__.py
    ├── unit_tests
    │   ├── HDFCLIFE.csv
    │   ├── HOOLI.csv
    │   ├── test_instrument.py
    │   ├── test_pnf.py
    │   └── test_renko.py
  needs: none
- [N-000048] requirement · MUST · L2 — #! /bin/bash
    
    # Run the demo
    python examples/demo.py
  needs: none
- [N-000049] requirement · MUST · L2 — class Instrument(df): initialize the model structure and parameters.
  needs: none
- [N-000050] requirement · MUST · L2 — _validate_df(): validates the DataFrame to ensure it has the required OHLC columns.
  needs: none
- [N-000051] requirement · MUST · L2 — class Renko(df): initialize the model structure and parameters.
  needs: none
- [N-000052] requirement · MUST · L2 — get_ohlc_data(): retrieves the OHLC (Open, High, Low, Close) data based on the chart type.
  needs: none
- [N-000053] requirement · MUST · L2 — period_close_bricks(): calculates the period close bricks based on the given brick size.
  needs: none
- [N-000054] requirement · MUST · L2 — shift_bricks(): shifts the bricks in the indicator dataframe based on the difference between the current close price and the previous close price.
  needs: none
- [N-000055] requirement · MUST · L2 — class LineBreak(df): initialize the model structure and parameters.
  needs: none
- [N-000056] requirement · MUST · L2 — uptrend_reversal(close): determines if a stock is experiencing an uptrend reversal.
  needs: none
- [N-000057] requirement · MUST · L2 — downtrend_reversa(close): determines if a downtrend reversal has occurred based on the given close price.
  needs: none
- [N-000058] requirement · MUST · L5 — retrieves the OHLC (Open, High, Low, Close) data from the DataFrame
  needs: none
- [N-000059] requirement · MUST · L5 — performs trend analysis.
  needs: none
- [N-000060] requirement · MUST · L5 — class PnF(df): initialize the model structure and parameters.
  needs: none
- [N-000061] requirement · MUST · L4 — brick_size(): returns the brick size used for the indicator.
  needs: none
- [N-000062] requirement · MUST · L5 — get_state(uptrend_p1, bricks): get the state of the trend based on the given parameters.
  needs: none
- [N-000063] requirement · MUST · L5 — rounds the input `x` to the nearest multiple of `base
  needs: none
- [N-000064] requirement · MUST · L4 — returns the result as an integer.
  needs: none
- [N-000065] requirement · MUST · L4 — get_ohlc_data(source): retrieves the PnF data in the form of an OHLC DataFrame.
  needs: none
- [N-000066] requirement · MUST · — — get_bar_ohlc_data(source): retrieves bar OHLC (Open, High, Low, Close) data.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000047 covered by N-000020 (pack 04) Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
- N-000047 covered by N-000030 (pack 04) Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
- N-000047 subsumes N-000020 (pack 04)
- N-000047 subsumes N-000030 (pack 04)
- N-000050 refines N-000046 (pack 11)
- N-000052 refines N-000008 (pack 03)
- N-000053 refines N-000006 (pack 03)

## Conflicts
None.

## Terms
None.
