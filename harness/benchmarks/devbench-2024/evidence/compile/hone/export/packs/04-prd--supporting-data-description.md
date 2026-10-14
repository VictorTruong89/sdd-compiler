# Pack 04 — sdd/specs/PRD.md · Supporting Data Description
blocks 62 · nodes 9 (assumption 2, requirement 7) · AC labels: none

## Text
# Supporting Data Description

The Hone project, focusing on converting CSV files into nested JSON formats, utilizes datasets stored in three folders: `data_file/comma_test`, `./data_file/quotes_test`, and `./data_file/small_cats_dataset`. These datasets are critical for testing and validation:
↳ N-000015 assumption · —

- **`data_file/comma_test` Folder:**
↳ no node

  - Contains files such as `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `nested_dataset.json`.These files are used to test the extraction of column names and data rows from CSVs and their conversion into a nested JSON structure.
↳ N-000016 assumption · — · L1

    - **`column_names.csv`:**
↳ no node

      - **Purpose:** Tests the parsing of column names within a CSV file.
↳ N-000017 requirement · — · L1

      - **Example Entries:** `"""test"",""ing"""," ""beep""""""`
↳ no node

    - **`data_rows.csv`:**
↳ no node

      - **Purpose:** Used for testing the extraction of data rows from CSV files.
↳ no node

      - **Example Entries:** `"""1","""2"`
↳ no node

    - **`dataset.csv`:**
↳ no node

      - **Purpose:** Combines the testing of both column names and data rows, serving as a comprehensive test file for CSV parsing.
↳ no node

      - **Example Entries:** `"""test"",""ing"""," ""beep""""""\n"""1","""2"`
↳ no node

    - **`nested_dataset.json`:**
↳ no node

      - **Purpose:** Demonstrates the expected JSON output format after the conversion of CSV data, particularly focusing on nested structures.
↳ no node

      - **Example Entries:** `[{" \"beep\"\"\"": "\"2", "\"test\",\"ing\"": "\"1"}]`
↳ no node

- **`./data_file/quotes_test` Folder:**
↳ no node

  - Includes similar files: `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `nested_dataset.json`.
↳ N-000018 requirement · — · L1

  - Essential for validating the CSV to JSON conversion process, ensuring the accuracy of the nested JSON structure based on various CSV formats.
↳ no node

  - **`column_names.csv`:**
↳ no node

    - **Purpose:** Tests the parsing of column names within a CSV file.
↳ no node

    - **Example Entries:**
↳ no node

      - `name,age (years),weight (kg),birth day,birth month,birth year,adopted,adopted_since,"some '"quoted"' field"`
↳ no node

  - **`data_rows.csv`:**
↳ no node

    - **Purpose:** Used for testing the extraction of data rows from CSV files.
↳ no node

    - **Example Entries:**
↳ no node

      - `Tommy,5,3.6,11,April,2011,TRUE,2012,no quotes`
↳ no node

      - `Clara,2,8.2,6,May,2015,FALSE,N/A,one double " and one single ' quote`
↳ no node

  - **`dataset.csv`:**
↳ no node

    - **Purpose:** Combines the testing of both column names and data rows, serving as a comprehensive test file for CSV parsing.
↳ no node

    - **Example Entries:**
↳ no node

      - `name,age (years),weight (kg),birth day,birth month,birth year,adopted,adopted_since,"some '"quoted"' field"`
↳ no node

      - `Tommy,5,3.6,11,April,2011,TRUE,2012,no quotes`
↳ no node

  - **`nested_dataset.json`:**
↳ no node

    - **Purpose:** Demonstrates the expected JSON output format after the conversion of CSV data, particularly focusing on nested structures.
↳ no node

    - **Example Entries:**
↳ no node

      ```json
      [
        {
          "some 'quoted\"' field\"": "no quotes",
          "adopted_since": "2012",
          "adopted": "TRUE",
          "birth": {
            "year": "2011",
            "month": "April",
            "day": "11"
          },
          "weight (kg)": "3.6",
          "age (years)": "5",
          "name": "Tommy"
        },
        // ... (other entries)
      ]
      ```
↳ N-000019 requirement · — · L4

- **`./data_file/small_cats_dataset` Folder:**
↳ no node

  - Houses `column_names.csv`, `data_rows.csv`, `dataset.csv`, `nested_dataset.json`, and `nested_schema.json`.
↳ N-000020 requirement · — · L2

  - Used for comprehensive testing of the conversion functionality, including adherence to a specified JSON schema.
↳ no node

  - **`column_names.csv`:**
↳ no node

    - **Purpose:** Tests the parsing of column names within a CSV file.
↳ no node

    - **Example Entries:**
↳ no node

      - `name,age (years),weight (kg),birth day,birth month,birth year,adopted,adopted_since`
↳ no node

  - **`data_rows.csv`:**
↳ no node

    - **Purpose:** Used for testing the extraction of data rows from CSV files.
↳ no node

    - **Example Entries:**
↳ no node

      - `Tommy,5,3.6,11,April,2011,TRUE,2012`
↳ no node

      - `Clara,2,8.2,6,May,2015,FALSE,N/A`
↳ no node

  - **`dataset.csv`:**
↳ no node

    - **Purpose:** Combines the testing of both column names and data rows, serving as a comprehensive test file for CSV parsing.
↳ no node

    - **Example Entries:**
↳ no node

      - `name,age (years),weight (kg),birth day,birth month,birth year,adopted,adopted_since`
↳ no node

      - `Tommy,5,3.6,11,April,2011,TRUE,2012`
↳ no node

      - `Clara,2,8.2,6,May,2015,FALSE,N/A`
↳ no node

  - **`nested_dataset.json`:**
↳ no node

    - **Purpose:** Demonstrates the expected JSON output format after the conversion of CSV data, particularly focusing on nested structures.
↳ no node

    - **Example Entries:**
↳ no node

      ```json
      [
        {
          "adopted": "TRUE",
          "adopted_since": "2012",
          "age (years)": "5",
          "birth": {
              "day": "11",
              "month": "April",
              "year": "2011"
          },
          "name": "Tommy",
          "weight (kg)": "3.6"
        },
        // ... (other entries)
      ]
      ```
↳ N-000021 requirement · — · L4

  - **`nested_schema.json`:**
↳ no node

    - **Purpose:** Specifies the expected mapping of CSV columns to JSON fields.
↳ N-000022 requirement · MUST · L4

    - **Example Entries:**
↳ no node

      ```json
      {
        "adopted_since": "adopted_since",
        "adopted": "adopted",
        "birth": {
          "year": "birth year",
          "month": "birth month",
          "day": "birth day"
        },
        "weight (kg)": "weight (kg)",
        "age (years)": "age (years)",
        "name": "name"
      }
      ```
↳ N-000023 requirement · — · L4

## Claims to implement
- [N-000015] assumption · — · — — utilizes datasets stored in three folders: `data_file/comma_test`, `./data_file/quotes_test`, and `./data_file/small_cats_dataset`.
  needs: none
- [N-000016] assumption · — · L1 — Contains files such as `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `nested_dataset.json`.
  needs: none
- [N-000017] requirement · — · L1 — Tests the parsing of column names within a CSV file.
  needs: N-000006 (pack 03)
- [N-000018] requirement · — · L1 — Includes similar files: `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `nested_dataset.json`.
  needs: none
- [N-000019] requirement · — · L4 —       [
            {
              "some 'quoted\"' field\"": "no quotes",
              "adopted_since": "2012",
              "adopted": "TRUE",
              "birth": {
                "year": "2011",
                "month": "April",
                "day": "11"
              },
              "weight (kg)": "3.6",
              "age (years)": "5",
              "name": "Tommy"
            },
            // ... (other entries)
          ]
  needs: none
- [N-000020] requirement · — · L2 — Houses `column_names.csv`, `data_rows.csv`, `dataset.csv`, `nested_dataset.json`, and `nested_schema.json`.
  needs: none
- [N-000021] requirement · — · L4 —       [
            {
              "adopted": "TRUE",
              "adopted_since": "2012",
              "age (years)": "5",
              "birth": {
                  "day": "11",
                  "month": "April",
                  "year": "2011"
              },
              "name": "Tommy",
              "weight (kg)": "3.6"
            },
            // ... (other entries)
          ]
  needs: none
- [N-000022] requirement · MUST · L4 — Specifies the expected mapping of CSV columns to JSON fields.
  needs: none
- [N-000023] requirement · — · L4 —       {
            "adopted_since": "adopted_since",
            "adopted": "adopted",
            "birth": {
              "year": "birth year",
              "month": "birth month",
              "day": "birth day"
            },
            "weight (kg)": "weight (kg)",
            "age (years)": "age (years)",
            "name": "name"
          }
  needs: none

## Acceptance criteria
None.

## Constraints in scope
- [N-000025] (pack 05) utilize built-in libraries for CSV and JSON processing.
plus the broad constraints in pack 01

## Related elsewhere
- N-000016 same as N-000018 (this pack) Includes similar files: `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `nested_dataset.json`.
- N-000018 same as N-000016 (this pack) Contains files such as `column_names.csv`, `data_rows.csv`, `dataset.csv`, and `nested_dataset.json`.

## Conflicts
None.

## Terms
None.
