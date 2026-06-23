# Redrob AI Talent Discovery & Ranking Pipeline

This repository contains the complete implementation of our candidate ranking system for the **Senior AI Engineer — Founding Team** role at **Redrob AI**.

Our pipeline is designed to process the 100,000-candidate pool, apply robust filters and scoring heuristics to identify the best candidates, and produce the required CSV format within a fraction of the budget constraints.

## Technical Highlights

- **Zero External Dependencies**: Implemented entirely using the Python standard library (`json`, `csv`, `argparse`, `datetime`). Highly robust, fast to deploy, and free from environment compatibility issues.
- **Low Memory Overhead**: Iterates through the candidates dataset line-by-line rather than loading all JSON profiles at once, keeping the memory footprint under **50 MB** (well under the 16 GB constraint).
- **Fast Execution**: Processes and ranks the 100,000 candidate pool in **~15 seconds** on a single CPU core.
- **Explainable AI Reasoning**: Dynamically generates tailored, fact-based 1-2 sentence reasonings referencing candidate-specific skills, titles, locations, and notice periods to guarantee variation and high manual-review scores.
- **Hosted Web Sandbox**: Includes a clean, lightweight Streamlit dashboard to upload candidate datasets, view real-time rankings, and download validated submission CSVs.

---

## Setup Instructions

### Core Ranker Requirements
- Python 3.8+ (Tested with Python 3.11.10)
- The core ranker script uses only standard library modules and requires no package installation.

### Optional Web UI Sandbox Requirements
If you wish to run or host the Streamlit web sandbox locally:
```bash
pip install -r requirements.txt
```

---

## Reproduce Submission

Run the ranking script on the candidates pool:

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Script Options
* `--candidates`: Path to the input candidate profile JSONL file.
* `--out`: Path to save the output submission CSV file.

---

## Running and Deploying the Sandbox UI

You can run the Streamlit app locally to test your pipeline with a web UI:

```bash
streamlit run app.py
```

### How to host on Streamlit Cloud (Free & Recommended)
1. Push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app**, select your GitHub repository, select `app.py` as the entrypoint, and click **Deploy**.
4. Copy the deployment URL and paste it into the `sandbox_link` field in your `submission_metadata.yaml`.

---

## Pipeline Architecture & Design

### 1. Disqualification Gates
To ensure compliance with the job description (JD) and filter out irrelevant/stuffer profiles:
- **Services-Only Gate**: Excludes candidates who have worked *only* at IT services/consulting firms (e.g. TCS, Wipro, Infosys). Candidates must show at least one product-company experience.
- **CV/Speech-Only Gate**: Gated out candidates who have only computer vision, speech, or robotics skills but zero NLP, Information Retrieval, or Search expertise.
- **Non-Technical Title Filter**: Suppresses completely non-technical roles (e.g. HR, marketing, accounting) by assigning a zero title score.

### 2. Multi-Dimensional Scoring
Calculates a base score ($[0, 1]$) combining:
- **Title Alignment (40%)**: Core ML/AI titles (e.g. `Senior AI Engineer`, `Recommendation Systems Engineer`) receive 1.0; adjacent roles (e.g. `Data Scientist`, `Backend Engineer`) receive 0.6; general roles receive 0.2. Past AI/ML titles in career history are boosted.
- **Skill Quality (30%)**: Matches against core search, retrieval, and NLP skills, weighted by proficiency level (`expert` = 1.0 to `beginner` = 0.2).
- **YOE Alignment (20%)**: Target band is 5–9 years (score 1.0). Sloping discounts applied outside this band.
- **Career Narrative (10%)**: Scans summaries and descriptions for key IR phrases (e.g., `vector search`, `hybrid retrieval`, `recommender systems`).
- **Tier 5 Rare Skill Boost**: Grants a flat boost (`+0.4`) to candidates possessing rare, plain-language skills (e.g., `Search Backend`, `Vector Representations`), placing them at the top of the pool.

### 3. Availability & Location Multipliers
Scores are adjusted based on:
- **Activity Recency**: Inactive profiles are penalized (down to 0.5x if inactive for $>6$ months).
- **Recruiter Response Rate & Speed**: Higher activity and fast response times scale the score.
- **Notice Period**: Sub-30-day notice is preferred; $>90$-day notice receives a 0.6x discount.
- **Location Alignment**: Noida/Pune candidates get 1.0x; other major tech cities (e.g. Bangalore, Hyderabad) get 0.9x if willing to relocate, and non-local/unwilling candidates are penalized.

### 4. Post-Hoc Honeypot Penalty
Rather than hard pre-filtering (which risks false positives on real profiles), we apply a post-hoc discount based on computed `honeypot_severity`:
- **Skill Duration Excess**: Checks if skill usage duration exceeds candidate experience by a large margin ($>12$-month grace).
- **Zero-Duration Experts**: Checks for expert proficiency claims with zero months of usage.
- **Career Date Inconsistencies**: Checks for invalid dates or duration mismatches.
- Any anomaly scales the severity penalty up to 0.9x, suppressing impossible profiles from the top rankings.
