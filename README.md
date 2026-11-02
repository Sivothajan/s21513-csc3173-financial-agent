# s21513-csc3173-financial-agent

## CSC3173: Artificial Intelligence (2024/25)

## Programming Assignment 02: Financial Document Analysis Agent

**Index Number:** S/21/513

**Project repository:** [s21513-csc3173-financial-agent](https://github.com/Sivothajan/s21513-csc3173-financial-agent)

This project implements a financial document analysis agent that answers questions using **Apple Inc.'s annual Form 10-K reports for fiscal 2023, 2024 and 2025**.

The agent extracts financial data from the supplied PDFs, retrieves relevant evidence, performs calculations, and generates reports with source citations.

Main components include:

- PDF document processing with PyMuPDF
- Semantic retrieval using TF-IDF and latent semantic analysis (LSA)
- Financial-table extraction and validation
- Financial calculations using Python's `decimal.Decimal`
- Markdown, PDF, chart and JSON report generation

## Dataset

**Dataset:** Apple Inc. Form 10-K annual reports

**Source:** The three audited annual reports supplied with the assignment, stored in [`data/`](data/).

| Fiscal year | File                                            | Products and Services Performance table |
| ----------- | ----------------------------------------------- | --------------------------------------- |
| 2023        | [`Apple_2023_10K.pdf`](data/Apple_2023_10K.pdf) | Printed p. 22 / PDF p. 25               |
| 2024        | [`Apple_2024_10K.pdf`](data/Apple_2024_10K.pdf) | Printed p. 23 / PDF p. 26               |
| 2025        | [`Apple_2025_10K.pdf`](data/Apple_2025_10K.pdf) | Printed p. 23 / PDF p. 26               |

Financial-table values are in **USD millions**. Years refer to Apple's fiscal years; 2025 is the latest year in the supplied dataset.

## Project Structure

```text
s21513-csc3173-financial-agent/
├── data/
│   ├── Apple_2023_10K.pdf
│   ├── Apple_2024_10K.pdf
│   └── Apple_2025_10K.pdf
├── src/
│   ├── CSC3173_Financial_Document_Agent.ipynb
│   └── agent_source.py
├── reports/                         # Generated reports, charts and JSON results
├── CSC3173_202425_PA02.pdf
├── README.md
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

## Environment

The project requires **Python 3.13 or newer** and uses [`uv`](https://docs.astral.sh/uv/) for dependency and virtual-environment management.

Main libraries include:

- PyMuPDF
- scikit-learn
- NumPy
- Matplotlib
- ReportLab
- mdformat and mdformat-gfm

JupyterLab, IPython kernel support and Ruff are included in the development dependencies.

## Setup

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) if it is not already available. Open a terminal in the project folder containing `pyproject.toml` and `uv.lock`.

Install the locked project and development dependencies:

```bash
uv sync --locked
```

Confirm that the three source PDFs are present in `data/` with the filenames shown above.

### Run the Jupyter Notebook

Start JupyterLab:

```bash
uv run jupyter lab
```

Then open:

```text
src/CSC3173_Financial_Document_Agent.ipynb
```

Run the notebook cells sequentially from the beginning. The notebook reads the PDFs from the project-root `data/` folder and writes its output to the project-root `reports/` folder.

### Run the Python Script

Run the same workflow from the project root:

```bash
uv run python src/agent_source.py
```

The commands above work in PowerShell, Command Prompt, Bash and Zsh without manually activating the virtual environment. Both entry points also resolve the project folders when launched from `src/`.

### Google Colab

Upload the notebook and the three PDFs, placing the PDFs in a `data/` folder under the runtime's working directory, or upload the project with its existing folder layout. Run all cells in order; the dependency cell installs missing libraries. Download the generated files from `reports/` before the runtime ends.

## Notebook Workflow

The notebook covers:

1. Dependency checks and input-file discovery
2. PDF text extraction and page-attributed chunking
3. TF-IDF and LSA semantic indexing
4. Financial-table extraction and validation
5. Agent state, intent parsing and planning
6. Evidence retrieval and financial calculations
7. Markdown reports, PDF reports and chart generation
8. Execution of the three assignment questions
9. Financial, source-traceability and agent-workflow assertions
10. Additional example questions

The agent follows a bounded execution loop:

```text
Question → Planner → RETRIEVE → Planner → CALCULATE → Planner → REPORT → Planner → FINISH
```

## Generated Reports

Each run writes the following files to [`reports/`](reports/) and replaces previous files with the same names:

- `Q1_report.md`, `Q2_report.md`, `Q3_report.md`: answers, source evidence and execution traces.
- `Q1_report.pdf`, `Q2_report.pdf`, `Q3_report.pdf`: formatted reports with charts.
- `Q1_chart.png`, `Q2_chart.png`, `Q3_chart.png`: revenue visualizations.
- `All_3_Financial_Analysis_Reports.pdf`: combined report for all three questions.
- `agent_results.json`: machine-readable answers, calculations, retrieved records and traces.

Each Markdown report is automatically formatted with [mdformat](https://mdformat.readthedocs.io/en/stable/users/installation_and_usage.html) and GitHub-flavored Markdown support immediately after it is written. This keeps table alignment and Markdown spacing consistent on every run, in both the notebook and the Python script.

## Expected Results

| Question                                      | Expected result                                                                                                                                    |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1: Total revenue change, 2023–2025           | $383.285 billion to $416.161 billion; an increase of $32.876 billion (**8.58%**).                                                                  |
| Q2: Largest physical product category in 2025 | **iPhone**, with $209.586 billion, representing **50.36%** of total net sales. Services is excluded from this ranking.                             |
| Q3: Services growth and share                 | $85.200 billion in 2023 to $109.158 billion in 2025; an increase of $23.958 billion (**28.12%**), with a **26.23%** share of 2025 total net sales. |

The workflow extracts the financial figures from the PDFs at runtime and checks the resulting values and planner transitions with assertions.

## Scope and Limitations

- No remote LLM or paid API key is required. Intent parsing and planning are deterministic and support the configured financial comparisons, rankings and revenue-share questions.
- LSA retrieval supplies semantic context; validated financial tables supply the numeric evidence.
- The Medical Document Agent source code shown in class was not available. The component mapping in the notebook is based on the assignment's illustrative architecture diagram.
- The assignment brief is included as [`CSC3173_202425_PA02.pdf`](CSC3173_202425_PA02.pdf). The original assignment lists a deadline of **15 November 2026, 11:59 PM**.
