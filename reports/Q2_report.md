# Apple Inc. - Financial Document Analysis

**Index Number:** S/21/513

**Project repository:** [s21513-csc3173-financial-agent](https://github.com/Sivothajan/s21513-csc3173-financial-agent)

**Question:** Which product category contributed the most revenue in the latest year?

## Answer

The largest product category in fiscal 2025 was iPhone, with $209.586 billion in net sales (50.36% of Apple's $416.161 billion total net sales). Services is excluded from the physical-product ranking.

## Recovered evidence (USD millions)

| Fiscal year | Financial measure               | Value (USD millions) | Original source                         |
| ----------- | ------------------------------- | -------------------: | --------------------------------------- |
| 2025        | Mac                             |               33,708 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |
| 2025        | Total net sales                 |              416,161 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |
| 2025        | Wearables, Home and Accessories |               35,686 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |
| 2025        | iPad                            |               28,023 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |
| 2025        | iPhone                          |              209,586 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |

## Python-computed results

- **Year:** 2025
- **Winner:** iPhone
- **Winner Revenue:** 209,586
- **Total:** 416,161
- **Share:** 50.36

## Approach and evidence policy

Financial data were extracted from the Products and Services Performance or Segment Operating Performance tables in Apple's supplied annual 10-K PDFs. LSA retrieval provides semantic context; financial-table parsing supplies verified numeric facts. Calculations use Python Decimal arithmetic, not language-model arithmetic.

Values are for Apple's **fiscal years** and are expressed in **USD millions** in source tables. Percentage comparisons use unrounded annual figures. The latest year refers to **2025 among the three supplied reports**, not a claim about the latest available filing today.

## Agent execution trace

- Step 1: planner -> RETRIEVE
- Step 2: planner -> CALCULATE
- Step 3: planner -> REPORT

## Semantic retrieval evidence (top matches)

- 2025 PDF p. 38 (LSA cosine 0.605): timated period they are expected to be provided. For certain long-term service arrangements, the Company has performance obligations for services … [continued]
- 2023 PDF p. 37 (LSA cosine 0.587): have a right to bill for the undelivered services. The Company has determined that any unbilled consideration relates entirely to the value of the … [continued]
- 2024 PDF p. 38 (LSA cosine 0.586): d does not disclose amounts, related to these undelivered services. For the sale of third-party products where the Company obtains control of the … [continued]
- Step 4: planner -> FINISH
