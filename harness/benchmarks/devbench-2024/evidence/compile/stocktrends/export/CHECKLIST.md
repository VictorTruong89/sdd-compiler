# Checklist

Every id below must end implemented, tested, or listed as not done with a reason.

## Pack 01 — 01-prd--introduction.md

- [ ] N-000001 · requirement · MUST · L2 · — · This program will include functionalities for processing financial data, calcula…

## Pack 02 — 02-prd--goals.md

- [ ] N-000002 · requirement · MUST · L1 · — · create a robust and efficient Python program that enables users to analyze finan…
- [ ] N-000003 · requirement · — · L0 · — · aiding in better understanding of market trends and investment opportunities

## Pack 03 — 03-prd--features-and-functionalities.md

- [ ] N-000004 · requirement · MUST · L1 · — · Load and preprocess financial data from various formats, including CSV.
- [ ] N-000005 · requirement · MUST · L1 · — · Normalize data fields to ensure consistency (e.g., lowercasing column names).
- [ ] N-000006 · requirement · MUST · L1 · — · Calculate Renko charts with customizable brick sizes.
- [ ] N-000007 · requirement · MUST · L1 · — · Provide options for different Renko chart types, such as 'PERIOD_CLOSE'.
- [ ] N-000008 · requirement · MUST · L1 · — · Ensure the method returns the correct data shape based on given parameters.
- [ ] N-000009 · requirement · MUST · L1 · — · Implement Line Break chart calculations with specified line numbers.
- [ ] N-000010 · requirement · MUST · L1 · — · Ensure accuracy in the calculation of closing prices in the Line Break chart.
- [ ] N-000011 · requirement · MUST · L1 · — · Develop functionality for calculating PnF charts.
- [ ] N-000012 · requirement · SHOULD · L1 · — · Focus on accuracy and consistency in PnF chart generation.
- [ ] N-000013 · requirement · MUST · L1 · — · Implement features for analyzing financial instruments, including stocks and com…
- [ ] N-000014 · requirement · MUST · L1 · — · Include functionality to handle specific instrument-related data processing and …
- [ ] N-000015 · requirement · MUST · L1 · — · Provide reporting capabilities to summarize the analysis results.
- [ ] N-000016 · requirement · MUST · L5 · — · Include comprehensive unit tests to validate the correctness of financial indica…
- [ ] N-000017 · requirement · MUST · L4 · — · Implement tests to check data shape and size after processing, ensuring data int…

## Pack 04 — 04-prd--supporting-data-description.md

- [ ] N-000018 · assumption · — · — · — · The project utilizes specific datasets stored in two folders, `./acceptance_samp…
- [ ] N-000019 · assumption · — · L1 · — · Contains CSV files for acceptance testing of the financial indicators.
- [ ] N-000020 · assumption · — · L1 · — · Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
- [ ] N-000021 · requirement · MUST · L1 · — · These files are used to validate the calculation models of Renko and Line Break …
- [ ] N-000022 · assumption · — · L1 · — · The file includes columns for date, open, high, low, and close prices.
- [ ] N-000023 · assumption · — · L1 · — · This file has columns for index, date, open, high, low, close, and uptrend statu…
- [ ] N-000024 · assumption · — · L1 · — · Includes date, open, high, low, close, and uptrend status columns.
- [ ] N-000025 · assumption · — · — · — · This folder is dedicated to unit testing, a key step in verifying the accuracy a…
- [ ] N-000026 · assumption · — · L1 · — · It contains specifically designed CSV files, such as `HDFCLIFE.csv` and `HOOLI.c…
- [ ] N-000027 · assumption · — · L1 · — · This file includes columns for DATE, SERIES, OPEN, HIGH, LOW, PREV. CLOSE, LTP, …
- [ ] N-000028 · assumption · — · L1 · — · The file includes columns for date, open, high, low, and close prices.
- [ ] N-000029 · assumption · — · L1 · — · Contains CSV files for acceptance testing of the financial indicators.
- [ ] N-000030 · assumption · — · L1 · — · Files include `HOOLI.csv`, `hooli_linebreak_3.csv`, and `hooli_renko_4.csv`.
- [ ] N-000031 · assumption · — · L1 · — · These files are used to validate the calculation models of Renko and Line Break …
- [ ] N-000032 · assumption · — · — · — · Used for unit testing to ensure the accuracy of financial indicators' calculatio…
- [ ] N-000033 · assumption · — · L2 · — · Contains `HOOLI.csv` and `HDFCLIFE.csv`, which are instrumental in testing the f…

## Pack 05 — 05-prd--technical-constraints.md

- [ ] N-000034 · constraint · SHOULD · C · — · The program should be developed in Python 3.x.
- [ ] N-000035 · constraint · SHOULD · C · — · Emphasis on using native Python libraries and minimal external dependencies.

## Pack 06 — 06-prd--dependencies.md

- [ ] N-000036 · requirement · MUST · — · — · Pytest library
- [ ] N-000037 · requirement · MUST · L2 · — · Pandas library
- [ ] N-000038 · requirement · MUST · L2 · — · Numpy library
- [ ] N-000039 · requirement · MUST · L2 · — · Matplotlib library

## Pack 07 — 07-prd--usage.md

None.

## Pack 08 — 08-prd--acceptance-criteria.md

- [ ] N-000040 · requirement · SHOULD · L1 · — · The repository should include acceptance testing for both the renko and line bre…
- [ ] N-000041 · requirement · MUST · L1 · — · For the Renko indicator calculation model, the program is required to precisely …
- [ ] N-000042 · verification · — · V · — · This will be evaluated by comparing the closing prices of the Renko chart genera…
- [ ] N-000043 · requirement · SHOULD · L1 · — · For the line break indicator calculation model, the program should correctly cal…
- [ ] N-000044 · verification · — · V · — · This will involve comparing the close prices of the Line Break chart generated f…

## Pack 09 — 09-prd--terms-concepts-explanation.md

None.

## Pack 10 — 10-uml-class--uml-class.md

- [ ] N-000045 · requirement · MUST · L2 · — · classDiagram class Instrument { -DataFrame odf -DataFrame df +__init__(df: DataF…

## Pack 11 — 11-uml-sequence--uml-sequence.md

- [ ] N-000046 · requirement · MUST · L2 · — · sequenceDiagram participant Client participant Instrument participant Renko part…

## Pack 12 — 12-architecture-design--architecture-design.md

- [ ] N-000047 · requirement · MUST · L2 · — · ├── acceptance_tests │ ├── HOOLI.csv │ ├── hooli_linebreak_3.csv │ ├── hooli_ren…
- [ ] N-000048 · requirement · MUST · L2 · — · #! /bin/bash # Run the demo python examples/demo.py
- [ ] N-000049 · requirement · MUST · L2 · — · class Instrument(df): initialize the model structure and parameters.
- [ ] N-000050 · requirement · MUST · L2 · — · _validate_df(): validates the DataFrame to ensure it has the required OHLC colum…
- [ ] N-000051 · requirement · MUST · L2 · — · class Renko(df): initialize the model structure and parameters.
- [ ] N-000052 · requirement · MUST · L2 · — · get_ohlc_data(): retrieves the OHLC (Open, High, Low, Close) data based on the c…
- [ ] N-000053 · requirement · MUST · L2 · — · period_close_bricks(): calculates the period close bricks based on the given bri…
- [ ] N-000054 · requirement · MUST · L2 · — · shift_bricks(): shifts the bricks in the indicator dataframe based on the differ…
- [ ] N-000055 · requirement · MUST · L2 · — · class LineBreak(df): initialize the model structure and parameters.
- [ ] N-000056 · requirement · MUST · L2 · — · uptrend_reversal(close): determines if a stock is experiencing an uptrend revers…
- [ ] N-000057 · requirement · MUST · L2 · — · downtrend_reversa(close): determines if a downtrend reversal has occurred based …
- [ ] N-000058 · requirement · MUST · L5 · — · retrieves the OHLC (Open, High, Low, Close) data from the DataFrame
- [ ] N-000059 · requirement · MUST · L5 · — · performs trend analysis.
- [ ] N-000060 · requirement · MUST · L5 · — · class PnF(df): initialize the model structure and parameters.
- [ ] N-000061 · requirement · MUST · L4 · — · brick_size(): returns the brick size used for the indicator.
- [ ] N-000062 · requirement · MUST · L5 · — · get_state(uptrend_p1, bricks): get the state of the trend based on the given par…
- [ ] N-000063 · requirement · MUST · L5 · — · rounds the input `x` to the nearest multiple of `base
- [ ] N-000064 · requirement · MUST · L4 · — · returns the result as an integer.
- [ ] N-000065 · requirement · MUST · L4 · — · get_ohlc_data(source): retrieves the PnF data in the form of an OHLC DataFrame.
- [ ] N-000066 · requirement · MUST · — · — · get_bar_ohlc_data(source): retrieves bar OHLC (Open, High, Low, Close) data.
