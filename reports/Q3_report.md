# Apple Inc. - Financial Document Analysis

**Index Number:** S/21/513

**Project repository:** [s21513-csc3173-financial-agent](https://github.com/Sivothajan/s21513-csc3173-financial-agent)

**Question:** How did Services revenue change from 2023 to 2025, and what share of 2025 total net sales did Services represent?

## Answer

Services increased from $85.200 billion in 2023 to $109.158 billion in 2025, a change of $23.958 billion (28.12%). In 2025, Services represented 26.23% of total net sales ($416.161 billion).

## Recovered evidence (USD millions)

| Fiscal year | Financial measure | Value (USD millions) | Original source                         |
| ----------- | ----------------- | -------------------: | --------------------------------------- |
| 2023        | Services          |               85,200 | Apple 2023 Form 10-K, p. 22 (PDF p. 25) |
| 2025        | Services          |              109,158 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |
| 2025        | Total net sales   |              416,161 | Apple 2025 Form 10-K, p. 23 (PDF p. 26) |

## Python-computed results

- **Old Year:** 2023
- **New Year:** 2025
- **Old:** 85,200
- **New:** 109,158
- **Absolute Change:** 23,958
- **Percentage Change:** 28.12
- **Share Of New Year Total:** 26.23
- **New Year Total:** 416,161

## Approach and evidence policy

Financial data were extracted from the Products and Services Performance or Segment Operating Performance tables in Apple's supplied annual 10-K PDFs. LSA retrieval provides semantic context; financial-table parsing supplies verified numeric facts. Calculations use Python Decimal arithmetic, not language-model arithmetic.

Values are for Apple's **fiscal years** and are expressed in **USD millions** in source tables. Percentage comparisons use unrounded annual figures. The latest year refers to **2025 among the three supplied reports**, not a claim about the latest available filing today.

## Agent execution trace

- Step 1: planner -> RETRIEVE
- Step 2: planner -> CALCULATE
- Step 3: planner -> REPORT

## Semantic retrieval evidence (top matches)

- 2024 PDF p. 38 (LSA cosine 0.808): Accessories 37,005 39,845 41,241 Services (1) 96,169 85,200 78,129 Total net sales $ 391,035 $ 383,285 $ 394,328 (1) Services net sales include … [continued]
- 2025 PDF p. 39 (LSA cosine 0.782): The following table shows disaggregated net sales, as well as the portion of total net sales that was previously deferred, for 2025, 2024 and 2023 … [continued]
- 2023 PDF p. 38 (LSA cosine 0.760): Net sales disaggregated by significant products and services for 2023, 2022 and 2021 were as follows (in millions): 2023 2022 2021 iPhone (1) $ … [continued]
- Step 4: planner -> FINISH
