# Pack 04 — sdd/specs/PRD.md · Supporting Data Description
blocks 33 · nodes 16 (assumption 15, requirement 1) · AC labels: none

## Text
# Supporting Data Description

The project utilizes specific datasets stored in two folders, `./acceptance_samples` and `./unit_samples`, which are essential for testing and validation:
↳ N-000018 assumption · —

<<<<<<< HEAD
↳ no node

1. **`acceptance_samples` Folder:**
↳ no node

   - **Purpose:** Contains CSV files for acceptance testing of the financial indicators.
↳ N-000019 assumption · — · L1

   - **Contents:** Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.These files are used to validate the calculation models of Renko and Line Break indicators, particularly in comparing the generated chart's closing prices with expected values.
↳ N-000020 assumption · — · L1 ; N-000021 requirement · MUST · L1

   - **Specific File Details:**
↳ no node

     - **`HOOLI.csv`**
↳ no node

      - **Content Structure:** The file includes columns for date, open, high, low, and close prices.
↳ N-000022 assumption · — · L1

      - **Example Entry:** `2015/1/1, 143.15, 146, 141.825, 143.95`
↳ no node

     - **`hooli_linebreak_3.csv`**
↳ no node

      - **Content Structure:** This file has columns for index, date, open, high, low, close, and uptrend status.
↳ N-000023 assumption · — · L1

      - **Example Entry:** `0, 2015/1/1, 143.15, 146, 141.825, 143.95, TRUE`
↳ no node

     - **`hooli_renko_4.csv`**
↳ no node

      - **Content Structure:** Includes date, open, high, low, close, and uptrend status columns.
↳ N-000024 assumption · — · L1

      - **Example Entry:** `0, 2015/1/1, 136, 140, 136, 140, TRUE`
↳ no node

2. **`unit_samples` Folder:**
↳ no node

   - **Purpose:** This folder is dedicated to unit testing, a key step in verifying the accuracy and functionality of financial indicators used in the project.
↳ N-000025 assumption · —

   - **Contents:** It contains specifically designed CSV files, such as `HDFCLIFE.csv` and `HOOLI.csv`, which are essential for conducting detailed and precise unit tests on the financial indicators.
↳ N-000026 assumption · — · L1

   - **Specific File Details:**
↳ no node

     - **`HDFCLIFE.csv`**
↳ no node

       - **Content Structure:** This file includes columns for DATE, SERIES, OPEN, HIGH, LOW, PREV. CLOSE, LTP, CLOSE, VWAP, 52W H, 52W L, VOLUME, VALUE, NO OF TRADES, SYMBOL.
↳ N-000027 assumption · — · L1

       - **Example Entry:** `2021/6/8, EQ, 684.05, 692, 681, 680.1, 691.5, 689.7, 687.22, 746, 486.25, 3425861, 2354315273, 76891, HDFCLIFE`
↳ no node

     - **`HOOLI.csv`**
↳ no node

       - **Content Structure:** The file includes columns for date, open, high, low, and close prices.
↳ N-000028 assumption · — · L1

       - **Example Entry:** `2015/1/1, 143.15, 146, 141.825, 143.95`
=======
↳ no node

1. **`./acceptance_samples` Folder:**
↳ no node

   - Contains CSV files for acceptance testing of the financial indicators.
↳ N-000029 assumption · — · L1

   - Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
↳ N-000030 assumption · — · L1

   - These files are used to validate the calculation models of Renko and Line Break indicators, particularly in comparing the generated chart's closing prices with expected values.
↳ N-000031 assumption · — · L1

2. **`./unit_samples` Folder:**
↳ no node

   - Used for unit testing to ensure the accuracy of financial indicators' calculations.
↳ N-000032 assumption · —

   - Contains `HOOLI.csv` and `HDFCLIFE.csv`, which are instrumental in testing the functionality and correctness of the indicators.
↳ N-000033 assumption · — · L2

>>>>>>> 7f3d422e388a78991eabaa5185d2e9f62500e124
↳ no node

## Claims to implement
- [N-000018] assumption · — · — — The project utilizes specific datasets stored in two folders, `./acceptance_samples` and `./unit_samples`, which are essential for testing and validation:
  needs: none
- [N-000019] assumption · — · L1 — Contains CSV files for acceptance testing of the financial indicators.
  needs: none
- [N-000020] assumption · — · L1 — Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
  needs: none
- [N-000021] requirement · MUST · L1 — These files are used to validate the calculation models of Renko and Line Break indicators, particularly in comparing the generated chart's closing prices with expected values.
  needs: none
- [N-000022] assumption · — · L1 — The file includes columns for date, open, high, low, and close prices.
  needs: none
- [N-000023] assumption · — · L1 — This file has columns for index, date, open, high, low, close, and uptrend status.
  needs: none
- [N-000024] assumption · — · L1 — Includes date, open, high, low, close, and uptrend status columns.
  needs: none
- [N-000025] assumption · — · — — This folder is dedicated to unit testing, a key step in verifying the accuracy and functionality of financial indicators used in the project.
  needs: none
- [N-000026] assumption · — · L1 — It contains specifically designed CSV files, such as `HDFCLIFE.csv` and `HOOLI.csv`, which are essential for conducting detailed and precise unit tests on the financial indicators.
  needs: none
- [N-000027] assumption · — · L1 — This file includes columns for DATE, SERIES, OPEN, HIGH, LOW, PREV. CLOSE, LTP, CLOSE, VWAP, 52W H, 52W L, VOLUME, VALUE, NO OF TRADES, SYMBOL.
  needs: none
- [N-000028] assumption · — · L1 — The file includes columns for date, open, high, low, and close prices.
  needs: none
- [N-000029] assumption · — · L1 — Contains CSV files for acceptance testing of the financial indicators.
  needs: none
- [N-000030] assumption · — · L1 — Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
  needs: none
- [N-000031] assumption · — · L1 — These files are used to validate the calculation models of Renko and Line Break indicators, particularly in comparing the generated chart's closing prices with expected values.
  needs: none
- [N-000032] assumption · — · — — Used for unit testing to ensure the accuracy of financial indicators' calculations.
  needs: none
- [N-000033] assumption · — · L2 — Contains `HOOLI.csv` and `HDFCLIFE.csv`, which are instrumental in testing the functionality and correctness of the indicators.
  needs: none

## Acceptance criteria
None.

## Constraints in scope
plus the broad constraints in pack 01

## Related elsewhere
- N-000016 duplicates N-000032 (pack 03) Include comprehensive unit tests to validate the correctness of financial indicators' calculations.
- N-000019 same as N-000029 (this pack) Contains CSV files for acceptance testing of the financial indicators.
- N-000020 covered by N-000047 (pack 12) ├── acceptance_tests
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
- N-000020 same as N-000030 (this pack) Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
- N-000021 refines N-000040 (pack 08)
- N-000021 same as N-000031 (this pack) These files are used to validate the calculation models of Renko and Line Break indicators, particularly in comparing the generated chart's closing prices with expected values.
- N-000022 same as N-000028 (this pack) The file includes columns for date, open, high, low, and close prices.
- N-000025 same as N-000032 (this pack) Used for unit testing to ensure the accuracy of financial indicators' calculations.
- N-000026 same as N-000033 (this pack) Contains `HOOLI.csv` and `HDFCLIFE.csv`, which are instrumental in testing the functionality and correctness of the indicators.
- N-000028 same as N-000022 (this pack) The file includes columns for date, open, high, low, and close prices.
- N-000029 same as N-000019 (this pack) Contains CSV files for acceptance testing of the financial indicators.
- N-000030 covered by N-000047 (pack 12) ├── acceptance_tests
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
- N-000030 same as N-000020 (this pack) Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
- N-000031 same as N-000021 (this pack) These files are used to validate the calculation models of Renko and Line Break indicators, particularly in comparing the generated chart's closing prices with expected values.
- N-000032 same as N-000016 (pack 03) Include comprehensive unit tests to validate the correctness of financial indicators' calculations.
- N-000032 same as N-000025 (this pack) This folder is dedicated to unit testing, a key step in verifying the accuracy and functionality of financial indicators used in the project.
- N-000033 same as N-000026 (this pack) It contains specifically designed CSV files, such as `HDFCLIFE.csv` and `HOOLI.csv`, which are essential for conducting detailed and precise unit tests on the financial indicators.
- N-000042 refines N-000021 (pack 08)
- N-000042 refines N-000031 (pack 08)
- N-000044 refines N-000021 (pack 08)
- N-000044 refines N-000031 (pack 08)
- N-000047 subsumes N-000020 (pack 12)
- N-000047 subsumes N-000030 (pack 12)

## Conflicts
None.

## Terms
None.
