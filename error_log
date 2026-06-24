# Error & Anomaly Resolution Log

This document tracks all errors, edge cases, and unexpected behaviors encountered during the pipeline implementation, along with their root causes, proposed solutions, and outcomes.

| Ref | Issue Description | Root Cause | Proposed Solution | Outcome / Status |
|---|---|---|---|---|
| ERR-01 | Converting `.docx` files to read them. | Standard `docx` library not installed on the system. | Wrote python zipfile/xml parser script to extract word paragraphs. | Successful. Converted README, JD, signals doc, and submission spec to plain text. |
| ERR-02 | `NameError: name 'datetime' is not defined` when running verification query. | Python shell command script was missing `from datetime import datetime` import. | Added the import statement. | Successful. Verified top 100 anomalies without further issues. |
| ERR-03 | `JSONDecodeError: Expecting value: line 1 column 2` in Streamlit UI when uploading `sample_candidates.json`. | The upload parsing logic assumed a JSON Lines (`.jsonl`) format, but the user uploaded a standard JSON array file (`.json`). | Added format detection: if the file starts with `[`, parse it as a standard JSON list, otherwise parse it line-by-line as JSON Lines. | Successful. Both `.jsonl` and standard `.json` formats now load and rank perfectly in the sandbox UI. |


