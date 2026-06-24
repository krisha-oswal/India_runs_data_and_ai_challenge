## 1. System Architecture

The pipeline is implemented as a single, highly-optimized script, `rank.py`, using only standard library modules to keep memory low and prevent dependencies.

### Pipeline Architecture Screenshot

<img width="433" height="757" alt="Pipeline Architecture" src="https://github.com/user-attachments/assets/ebbe9538-6e8d-4bb3-8ce8-be819e0e1ca1" />

### Processing Flow

```mermaid
flowchart TD
    A[Raw Candidate Dataset] --> B[Candidate Parsing]

    B --> C{Disqualification Gates}

    C -->|Pass| D[Composite Scoring Engine]
    C -->|Fail| X[Discard Candidate]

    D --> D1[Title Alignment Score]
    D --> D2[Skill Quality Score]
    D --> D3[YOE Score]
    D --> D4[Keyword Match Score]

    D1 --> E[Behavioral Multiplier]
    D2 --> E
    D3 --> E
    D4 --> E

    E --> F[Location Multiplier]

    F --> G[Honeypot Detection]
    G --> G1[Skill Duration Checks]
    G --> G2[Expertise Consistency Checks]
    G --> G3[Timeline Validation]

    G1 --> H[Final Candidate Score]
    G2 --> H
    G3 --> H

    H --> I[Reasoning Generation]
    I --> J[Candidate Ranking]
    J --> K[Top 100 Candidates]
    K --> L[submission.csv]
```

### Disqualification Gates

1. **Services-Only Gate**: Filters out candidates who have only worked at services companies (`Infosys`, `Wipro`, `TCS`, `Capgemini`, `HCL`, `Accenture`, `Cognizant`, `Tech Mahindra`, `Mphasis`, `Genpact`).

2. **CV/Speech-Only Gate**: Filters out candidates whose skill set is entirely Computer Vision, Speech, or Robotics with zero NLP, Information Retrieval, or Search skills.

### Composite Scoring Model

\[
\text{Score} =
\text{Base Score}
\times
\text{Behavioral Multiplier}
\times
\text{Location Multiplier}
\times
(1.0 - \text{Honeypot Severity})
\]

- **Base Score**: Aligned titles (40%), skill quality matching (30%), YOE (20%), and summary keyword count (10%).
- **Behavioral Multiplier**: Factored from profile activity recency, recruiter response rate, response time, and notice period.
- **Location Multiplier**: Anchored to Pune/Noida, Delhi NCR, and willingness to relocate.
- **Honeypot Discount**: Computes severity based on skill duration excess, zero-duration expert skills, and calendar mismatches.
- **Plain-Language Tier 5 Boost**: Adds a flat boost (`+0.4`) for candidates with rare paraphrased skills (`Search Backend`, `Vector Representations`, `Ranking Systems`, etc.).
