# Apple Inc. - Financial Document Analysis

**Index Number:** S/21/513

**Project repository:** [s21513-csc3173-financial-agent](https://github.com/Sivothajan/s21513-csc3173-financial-agent)

**Question:** How did the company's total revenue change between 2023 and 2025?

## Answer

Total net sales increased from $383.285 billion in 2023 to $416.161 billion in 2025, a change of $32.876 billion (8.58%).

## Recovered evidence (USD millions)

| Fiscal year | Financial measure | Value (USD millions) | Original source                         |
| ----------- | ----------------- | -------------------: | --------------------------------------- |
| 2023        | Total net sales   |              383,285 | Apple 2023 Form 10-K, p. 22 (PDF p. 25) |
| 2025        | Total net sales   |              416,161 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |

## Python-computed results

- **Old Year:** 2023
- **New Year:** 2025
- **Old:** 383,285
- **New:** 416,161
- **Absolute Change:** 32,876
- **Percentage Change:** 8.58

## Approach and evidence policy

Financial data were extracted from the Products and Services Performance or Segment Operating Performance tables in Apple's supplied annual 10-K PDFs. LSA retrieval provides semantic context; financial-table parsing supplies verified numeric facts. Calculations use Python Decimal arithmetic, not language-model arithmetic.

Values are for Apple's **fiscal years** and are expressed in **USD millions** in source tables. Percentage comparisons use unrounded annual figures. The latest year refers to **2025 among the three supplied reports**, not a claim about the latest available filing today.

## Agent execution trace

- Step 1: planner -> RETRIEVE
- Step 2: planner -> CALCULATE
- Step 3: planner -> REPORT

## Semantic retrieval evidence (top matches)

- 2025 PDF p. 39 (LSA cosine 0.678): The following table shows disaggregated net sales, as well as the portion of total net sales that was previously deferred, for 2025, 2024 and 2023 … [continued]
- 2024 PDF p. 38 (LSA cosine 0.674): Accessories 37,005 39,845 41,241 Services (1) 96,169 85,200 78,129 Total net sales $ 391,035 $ 383,285 $ 394,328 (1) Services net sales include … [continued]
- 2025 PDF p. 51 (LSA cosine 0.633): The following tables show net sales for 2025, 2024 and 2023 and long-lived assets as of September 27, 2025 and September 28, 2024 for countries … [continued]
- Step 4: planner -> FINISH
