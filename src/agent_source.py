"""
Analyze Apple 10-K PDFs. CSC3173 index number: S/21/513.
Project repository: https://github.com/Sivothajan/s21513-csc3173-financial-agent
"""

import importlib.util
import subprocess
import sys
import textwrap

DEPENDENCIES = {
    "fitz": "PyMuPDF",
    "sklearn": "scikit-learn",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "reportlab": "reportlab",
    "mdformat": "mdformat>=1.0.0",
    "mdformat_gfm": "mdformat-gfm>=1.0.0",
}
missing = [
    package
    for module, package in DEPENDENCIES.items()
    if importlib.util.find_spec(module) is None
]
if missing:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])
print("Dependencies ready.")


import json
import re
from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pymupdf as fitz
import matplotlib
import mdformat
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as PDFImage,
)
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

INDEX_NUMBER = "S/21/513"
REPOSITORY_URL = "https://github.com/Sivothajan/s21513-csc3173-financial-agent"

# Support both script and notebook working directories.
START_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
ROOT = START_DIR.parent if START_DIR.name == "src" else START_DIR
DATA_DIR = ROOT / "data"
FILES = {year: f"Apple_{year}_10K.pdf" for year in (2023, 2024, 2025)}
if not all((DATA_DIR / filename).is_file() for filename in FILES.values()):
    raise FileNotFoundError(
        "Place Apple_2023_10K.pdf, Apple_2024_10K.pdf and "
        f"Apple_2025_10K.pdf in the project data folder: {DATA_DIR}"
    )
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATHS = {year: DATA_DIR / name for year, name in FILES.items()}
print("PDF input folder:", DATA_DIR.relative_to(ROOT))
print("Report output folder:", REPORT_DIR.relative_to(ROOT))


@dataclass(frozen=True)
class TextChunk:
    year: int
    pdf_page: int
    filename: str
    text: str


def page_chunks(text: str, chunk_size: int = 1300, overlap: int = 160) -> list[str]:
    """Create character-bounded chunks, preferring sentence/word boundaries."""
    if chunk_size <= overlap:
        raise ValueError("chunk_size must exceed overlap")
    text = re.sub(r"[ \t]+", " ", text).strip()
    result = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        piece = text[start:end].strip()
        if piece:
            result.append(piece)
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return result


def process_documents(pdf_paths: dict[int, Path]):
    pages: dict[tuple[int, int], str] = {}
    chunks: list[TextChunk] = []
    for year, path in sorted(pdf_paths.items()):
        with fitz.open(str(path)) as doc:
            for page_num, page in enumerate(doc, start=1):
                txt = page.get_text("text", sort=False)
                pages[(year, page_num)] = txt
                for part in page_chunks(txt):
                    chunks.append(TextChunk(year, page_num, path.name, part))
    if not chunks:
        raise RuntimeError("PDF extraction returned no text")
    return pages, chunks


PAGES, CHUNKS = process_documents(PDF_PATHS)
print(
    f"Processed {len(PAGES)} PDF pages into {len(CHUNKS)} source-attributed text chunks."
)


class SemanticRetrievalTool:
    def __init__(self, chunks: list[TextChunk], dimensions: int = 96):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=22000,
            sublinear_tf=True,
            min_df=1,
        )
        sparse_vectors = self.vectorizer.fit_transform([c.text for c in chunks])
        k = min(dimensions, *sparse_vectors.shape) - 1
        if k < 2:
            raise ValueError("Not enough document vocabulary for LSA")
        self.model = TruncatedSVD(n_components=k, n_iter=4, random_state=3173)
        self.embeddings = normalize(self.model.fit_transform(sparse_vectors))

    def search(
        self, question: str, top_k: int = 5, restrict_years: set[int] | None = None
    ) -> list[dict]:
        query_vector = normalize(
            self.model.transform(self.vectorizer.transform([question]))
        )[0]
        scores = self.embeddings @ query_vector
        order = np.argsort(scores)[::-1]
        matches = []
        for idx in order:
            chunk = self.chunks[int(idx)]
            if restrict_years is not None and chunk.year not in restrict_years:
                continue
            matches.append(
                {
                    "year": chunk.year,
                    "pdf_page": chunk.pdf_page,
                    "filename": chunk.filename,
                    "score": round(float(scores[idx]), 4),
                    "snippet": chunk.text[:350].replace("\n", " "),
                }
            )
            if len(matches) == top_k:
                break
        return matches


SEMANTIC = SemanticRetrievalTool(CHUNKS)
print("Semantic index created. Example:")
for r in SEMANTIC.search("2025 revenue by iPhone and Services", top_k=2):
    print(f"  {r['year']} PDF page {r['pdf_page']}: score={r['score']:.3f}")

PRODUCT_CATEGORIES = ("iPhone", "Mac", "iPad", "Wearables, Home and Accessories")
SALES_CATEGORIES = (*PRODUCT_CATEGORIES, "Services")
REGIONS = ("Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific")
TOTAL_LABEL = "Total net sales"
TABLE_TITLES = {
    "category": "The following table shows net sales by category",
    "region": "The following table shows net sales by reportable segment",
}


@dataclass(frozen=True)
class FinancialRecord:
    year: int
    dimension: str
    label: str
    value_usd_millions: int
    filename: str
    pdf_page: int
    report_page: int

    @property
    def citation(self):
        return f"Apple {self.year} Form 10-K, p. {self.report_page} (PDF p. {self.pdf_page})"


def extract_first_dollar_value(lines: list[str], row_label: str) -> int:
    """Read the first comma-grouped dollar figure after an exact financial row."""
    # Allow footnote markers after category names.
    pattern = re.compile(re.escape(row_label) + r"(?:\s*\(\d+\))?", re.IGNORECASE)
    for index, row in enumerate(lines):
        if pattern.fullmatch(row.strip()):
            ahead = lines[index + 1 : index + 7]
            for line in ahead:
                match = re.search(r"(?<!\d)(\d{1,3}(?:,\d{3})+)(?!\d)", line)
                if match:
                    return int(match.group(1).replace(",", ""))
            raise ValueError(f"No financial value after row {row_label!r}")
    raise ValueError(f"Missing row {row_label!r} in table")


class FinancialRetrievalTool:
    def __init__(self, pages: dict[tuple[int, int], str]):
        self.records: dict[tuple[int, str, str], FinancialRecord] = {}
        self.table_pages: dict[tuple[int, str], int] = {}
        for year in (2023, 2024, 2025):
            for dimension, title in TABLE_TITLES.items():
                matches = [
                    (page, txt)
                    for (yr, page), txt in pages.items()
                    if yr == year and title in txt
                ]
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected 1 {dimension} table in {year}, got {len(matches)}"
                    )
                page, _text = matches[0]
                self.table_pages[(year, dimension)] = page
                # Read the table row before its label repeats in the narrative.
                full_section = matches[0][1].split(title, 1)[1]
                lines = [line.strip() for line in full_section.splitlines()]
                names = SALES_CATEGORIES if dimension == "category" else REGIONS
                for name in (*names, TOTAL_LABEL):
                    val = extract_first_dollar_value(lines, name)
                    # Account for the three unnumbered front pages.
                    printed_page = page - 3
                    record = FinancialRecord(
                        year, dimension, name, val, FILES[year], page, printed_page
                    )
                    self.records[(year, dimension, name)] = record

        for year in (2023, 2024, 2025):
            for dimension, names in (
                ("category", SALES_CATEGORIES),
                ("region", REGIONS),
            ):
                total = self.get(year, dimension, TOTAL_LABEL).value_usd_millions
                calculated = sum(
                    self.get(year, dimension, n).value_usd_millions for n in names
                )
                if calculated != total:
                    raise AssertionError(
                        f"{year} {dimension}: component sum {calculated:,} != total {total:,}"
                    )
            cat_total = self.get(year, "category", TOTAL_LABEL).value_usd_millions
            region_total = self.get(year, "region", TOTAL_LABEL).value_usd_millions
            if cat_total != region_total:
                raise AssertionError(f"Category/region totals do not match for {year}")

    def get(self, year: int, dimension: str, label: str) -> FinancialRecord:
        key = (year, dimension, label)
        if key not in self.records:
            raise KeyError(f"No verified 10-K record for {key}")
        return self.records[key]

    def ranking(self, year: int, dimension: str, include_services: bool = False):
        names = (
            (SALES_CATEGORIES if include_services else PRODUCT_CATEGORIES)
            if dimension == "category"
            else REGIONS
        )
        return sorted(
            (self.get(year, dimension, name) for name in names),
            key=lambda r: r.value_usd_millions,
            reverse=True,
        )


FINANCE = FinancialRetrievalTool(PAGES)
for year in (2023, 2024, 2025):
    total = FINANCE.get(year, "category", TOTAL_LABEL)
    print(f"{year}: ${total.value_usd_millions:,} million - {total.citation}")
print(
    "Validation passed: category and regional net sales reconcile in all 3 annual reports."
)

DECIMAL_TWO = Decimal("0.01")


def decimal_percent_change(old: int, new: int) -> Decimal:
    if old == 0:
        raise ZeroDivisionError("Cannot compute percent change when baseline is zero")
    return ((Decimal(new) - Decimal(old)) / Decimal(old) * 100).quantize(
        DECIMAL_TWO, rounding=ROUND_HALF_UP
    )


def decimal_share(part: int, total: int) -> Decimal:
    if total == 0:
        raise ZeroDivisionError("Cannot calculate share with zero total")
    return (Decimal(part) / Decimal(total) * 100).quantize(
        DECIMAL_TWO, rounding=ROUND_HALF_UP
    )


def million_usd(value: int) -> str:
    return f"${value:,} million"


def billion_usd(value: int) -> str:
    return f"${Decimal(value) / 1000:,.3f} billion"


def format_excerpt(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", text.replace("\ufffd", " ")).strip()
    if len(text) <= limit:
        return text

    marker = " … [continued]"
    excerpt = textwrap.shorten(text, width=limit, placeholder=marker)
    body = excerpt.removesuffix(marker).rstrip()
    openings = []
    pairs = {")": "(", "]": "["}
    for position, character in enumerate(body):
        if character in "([":
            openings.append((position, character))
        elif character in pairs and openings and openings[-1][1] == pairs[character]:
            openings.pop()
    if openings:
        body = body[: openings[0][0]].rstrip(" ,;:")
    return body + marker


@dataclass
class AgentState:
    question: str
    intent: str = ""
    years: list[int] = field(default_factory=list)
    dimension: str = "category"
    label: str = TOTAL_LABEL
    retrieval_done: bool = False
    calculation_done: bool = False
    report_done: bool = False
    records: list[FinancialRecord] = field(default_factory=list)
    semantic_matches: list[dict] = field(default_factory=list)
    calculations: dict = field(default_factory=dict)
    answer: str = ""
    report_markdown: str = ""
    trace: list[str] = field(default_factory=list)
    error: str = ""


def interpret_question(state: AgentState):
    lower = state.question.lower()
    found_years = sorted({int(y) for y in re.findall(r"\b20(?:23|24|25)\b", lower)})
    state.years = found_years or [2025]
    for region in REGIONS:
        if region.lower() in lower:
            state.dimension, state.label = "region", region
            break
    else:
        for category in sorted(SALES_CATEGORIES, key=len, reverse=True):
            if category.lower() in lower:
                state.dimension, state.label = "category", category
                break

    is_rank = any(
        s in lower
        for s in ["which", "highest", "largest", "most revenue", "top category"]
    )
    is_change = any(
        s in lower for s in ["change", "grow", "growth", "increase", "decrease"]
    )
    is_share = any(
        s in lower for s in ["share", "contribut", "proportion", "percentage of total"]
    )
    if is_rank:
        state.intent = "ranking"
        state.years = [max(state.years)]
    elif is_change and is_share and len(state.years) >= 2:
        state.intent = "compare_and_share"
        state.years = [min(state.years), max(state.years)]
    elif is_change and len(state.years) >= 2:
        state.intent = "compare"
        state.years = [min(state.years), max(state.years)]
    elif is_share:
        state.intent = "share"
        state.years = [max(state.years)]
    elif any(s in lower for s in ["revenue", "net sales", "sales"]):
        state.intent = "single_value"
        state.years = [max(state.years)]
    else:
        state.intent = "unsupported"


def planner(state: AgentState) -> str:
    if state.error:
        return "FINISH"
    if not state.retrieval_done:
        return "RETRIEVE"
    if not state.calculation_done and state.intent != "unsupported":
        return "CALCULATE"
    if not state.report_done:
        return "REPORT"
    return "FINISH"


def retrieve_node(state: AgentState):
    interpret_question(state)
    state.semantic_matches = SEMANTIC.search(state.question, top_k=5)
    years = state.years
    dimension = state.dimension
    label = state.label
    rows = []
    if state.intent == "ranking":
        rows = FINANCE.ranking(years[-1], dimension, include_services=False)
        rows.append(FINANCE.get(years[-1], "category", TOTAL_LABEL))
    elif state.intent in {"compare", "compare_and_share"}:
        rows = [FINANCE.get(y, dimension, label) for y in years]
        if state.intent == "compare_and_share":
            rows.append(FINANCE.get(years[-1], "category", TOTAL_LABEL))
    elif state.intent == "share":
        rows = [
            FINANCE.get(years[-1], dimension, label),
            FINANCE.get(years[-1], "category", TOTAL_LABEL),
        ]
    elif state.intent == "single_value":
        rows = [FINANCE.get(years[-1], dimension, label)]
    # Deduplicate records without changing order.
    state.records = list({(r.year, r.dimension, r.label): r for r in rows}.values())
    state.retrieval_done = True


def calculate_node(state: AgentState):
    lookup = {
        (r.year, r.dimension, r.label): r.value_usd_millions for r in state.records
    }

    def value(year, dimension, label):
        return lookup[(year, dimension, label)]

    year = state.years[-1]
    dimension = state.dimension
    label = state.label
    if state.intent in {"compare", "compare_and_share"}:
        old_year, new_year = state.years
        old, new = value(old_year, dimension, label), value(new_year, dimension, label)
        state.calculations.update(
            {
                "old_year": old_year,
                "new_year": new_year,
                "old": old,
                "new": new,
                "absolute_change": new - old,
                "percentage_change": str(decimal_percent_change(old, new)),
            }
        )
        direction = (
            "increased"
            if new > old
            else "decreased"
            if new < old
            else "remained unchanged"
        )
        state.answer = (
            f"{label} {direction} from {billion_usd(old)} in {old_year} "
            f"to {billion_usd(new)} in {new_year}, a change of "
            f"{billion_usd(abs(new - old))} ({state.calculations['percentage_change']}%)."
        )
        if state.intent == "compare_and_share":
            total = value(new_year, "category", TOTAL_LABEL)
            share = decimal_share(new, total)
            state.calculations["share_of_new_year_total"] = str(share)
            state.calculations["new_year_total"] = total
            state.answer += (
                f" In {new_year}, {label} represented {share}% of "
                f"total net sales ({billion_usd(total)})."
            )
    elif state.intent == "ranking":
        candidates = [
            r
            for r in state.records
            if r.year == year and r.dimension == dimension and r.label != TOTAL_LABEL
        ]
        winner = max(candidates, key=lambda r: r.value_usd_millions)
        total = value(year, "category", TOTAL_LABEL)
        share = decimal_share(winner.value_usd_millions, total)
        state.calculations = {
            "year": year,
            "winner": winner.label,
            "winner_revenue": winner.value_usd_millions,
            "total": total,
            "share": str(share),
        }
        qualifier = (
            "product category" if dimension == "category" else "regional segment"
        )
        state.answer = (
            f"The largest {qualifier} in fiscal {year} was {winner.label}, "
            f"with {billion_usd(winner.value_usd_millions)} in net sales "
            f"({share}% of Apple's {billion_usd(total)} total net sales)."
        )
        if dimension == "category":
            state.answer += " Services is excluded from the physical-product ranking."
    elif state.intent == "share":
        part = value(year, dimension, label)
        total = value(year, "category", TOTAL_LABEL)
        share = decimal_share(part, total)
        state.calculations = {
            "year": year,
            "part": part,
            "total": total,
            "share": str(share),
        }
        state.answer = f"In {year}, {label} represented {share}% of total net sales ({billion_usd(part)} of {billion_usd(total)})."
    elif state.intent == "single_value":
        amount = value(year, dimension, label)
        state.calculations = {"year": year, "value": amount}
        state.answer = (
            f"In fiscal {year}, {label} generated {billion_usd(amount)} in net sales."
        )
    state.calculation_done = True


def report_node(state: AgentState):
    lines = [
        "# Apple Inc. - Financial Document Analysis",
        "",
        f"**Index Number:** {INDEX_NUMBER}",
        "",
        f"**Project repository:** [s21513-csc3173-financial-agent]({REPOSITORY_URL})",
        "",
        f"**Question:** {state.question}",
        "",
        "## Answer",
        "",
        state.answer
        if state.intent != "unsupported"
        else "Unable to answer this question reliably with the supported 10-K financial schema.",
        "",
        "## Recovered evidence (USD millions)",
        "",
        "| Fiscal year | Financial measure | Value (USD millions) | Original source |",
        "|---|---|---:|---|",
    ]
    if state.records:
        for r in sorted(state.records, key=lambda r: (r.year, r.dimension, r.label)):
            lines.append(
                f"| {r.year} | {r.label} | {r.value_usd_millions:,} | {r.citation} |"
            )
    else:
        lines.append("| - | - | - | No verified numeric record retrieved |")
    lines += ["", "## Python-computed results", ""]
    for key, val in state.calculations.items():
        lines.append(
            f"- **{key.replace('_', ' ').title()}:** {val:,}"
            if isinstance(val, int) and key not in {"year", "old_year", "new_year"}
            else f"- **{key.replace('_', ' ').title()}:** {val}"
        )
    lines += [
        "",
        "## Approach and evidence policy",
        "",
        (
            "Financial data were extracted from the Products and Services Performance "
            "or Segment Operating Performance tables in Apple's supplied annual 10-K PDFs. "
            "LSA retrieval provides semantic context; financial-table parsing supplies "
            "verified numeric facts. Calculations use Python Decimal arithmetic, "
            "not language-model arithmetic."
        ),
        "",
        (
            "Values are for Apple's **fiscal years** and are expressed in **USD millions** "
            "in source tables. Percentage comparisons use unrounded annual figures. "
            "The latest year refers to **2025 among the three supplied reports**, "
            "not a claim about the latest available filing today."
        ),
        "",
        "## Agent execution trace",
        "",
    ]
    lines += [f"- {step}" for step in state.trace]
    lines += ["", "## Semantic retrieval evidence (top matches)", ""]
    for item in state.semantic_matches[:3]:
        lines.append(
            f"- {item['year']} PDF p. {item['pdf_page']} (LSA cosine {item['score']:.3f}): {format_excerpt(item['snippet'])}"
        )
    state.report_markdown = "\n".join(lines) + "\n"
    state.report_done = True


def run_agent(question: str, max_iterations: int = 10) -> AgentState:
    state = AgentState(question=question)
    for n in range(max_iterations):
        action = planner(state)
        state.trace.append(f"Step {n + 1}: planner -> {action}")
        if action == "FINISH":
            if state.report_done:
                state.report_markdown += f"- {state.trace[-1]}\n"
            return state
        try:
            if action == "RETRIEVE":
                retrieve_node(state)
            elif action == "CALCULATE":
                calculate_node(state)
            elif action == "REPORT":
                report_node(state)
            else:
                raise RuntimeError(f"Planner returned unexpected action: {action}")
        except Exception as exc:
            state.error = f"{type(exc).__name__}: {exc}"
            state.trace.append("Error: " + state.error)
            raise RuntimeError(f"Agent failed during {action}: {state.error}") from exc
    raise RuntimeError(
        f"Agent exceeded {max_iterations} iterations without termination"
    )


def draw_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#56677f"))
    canvas.drawString(
        42, 24, f"CSC3173 | {INDEX_NUMBER} | Apple financial document analysis"
    )
    canvas.drawRightString(A4[0] - 42, 24, f"Page {doc.page}")
    canvas.restoreState()


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitleCustom",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#11243e"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportH2Custom",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#113b62"),
            spaceBefore=9,
            spaceAfter=4,
            fontSize=10.5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBodyCustom",
            parent=styles["BodyText"],
            fontSize=8.6,
            leading=12.5,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSmallCustom",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=10,
            spaceAfter=3,
        )
    )
    return styles


def simple_table(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11243e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f0f4fa")],
                ),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#23354b")),
                ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#ccd4e0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def make_chart(state: AgentState, path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    if state.intent == "ranking":
        data = [r for r in FINANCE.ranking(state.years[-1], "category")]
        labels = [
            r.label.replace(
                "Wearables, Home and Accessories", "Wearables / Home / Acc."
            )
            for r in data
        ]
        values = [r.value_usd_millions / 1000 for r in data]
        ax.barh(labels[::-1], values[::-1], color="#3d79a6")
        ax.set_title("Apple product sales, FY2025")
        ax.set_xlabel("USD billions")
    else:
        label = state.label
        years_for_chart = state.years if len(state.years) >= 2 else [2023, 2024, 2025]
        values = [
            FINANCE.get(y, state.dimension, label).value_usd_millions / 1000
            for y in years_for_chart
        ]
        ax.bar([str(y) for y in years_for_chart], values, color="#3d79a6")
        ax.set_title(
            f"Apple {label}, fiscal {min(years_for_chart)}-{max(years_for_chart)}"
        )
        ax.set_ylabel("USD billions")
        for i, v in enumerate(values):
            ax.text(i, v + max(values) * 0.012, f"{v:.2f}", ha="center", fontsize=9)
        ax.set_ylim(0, max(values) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def report_elements(state: AgentState, styles, chart_path: Path | None = None):
    p = lambda s: Paragraph(s, styles["ReportBodyCustom"])
    h = lambda s: Paragraph(s, styles["ReportH2Custom"])
    tiny = lambda s: Paragraph(s, styles["ReportSmallCustom"])
    from xml.sax.saxutils import escape

    content = [
        Paragraph(
            "Apple Inc. | Financial Analysis Report", styles["ReportTitleCustom"]
        ),
        Paragraph(
            f'<link href="{REPOSITORY_URL}">Project repository: s21513-csc3173-financial-agent</link>',
            styles["ReportSmallCustom"],
        ),
        p("<b>Question:</b> " + escape(state.question)),
        h("Answer"),
        p(escape(state.answer)),
        h("Verified source figures"),
    ]
    rows = [["Fiscal year", "Measure", "USD millions"]]
    for r in sorted(state.records, key=lambda x: (x.year, x.dimension, x.label)):
        rows.append([str(r.year), r.label, f"${r.value_usd_millions:,}"])
    content.append(simple_table(rows, [75, 265, 115]))
    content.append(Spacer(1, 4))
    if chart_path and chart_path.exists():
        content += [
            h("Revenue visualization"),
            PDFImage(str(chart_path), width=370, height=164),
        ]
    content.append(h("Computed results"))
    for key, value in state.calculations.items():
        val = (
            f"{value:,}"
            if isinstance(value, int) and key not in {"year", "old_year", "new_year"}
            else str(value)
        )
        content.append(
            tiny(f"<b>{escape(key.replace('_', ' ').title())}:</b> {escape(val)}")
        )
    content.append(h("Sources and verification"))
    seen = set()
    for r in state.records:
        if r.citation not in seen:
            seen.add(r.citation)
            content.append(tiny(escape(r.citation) + " - " + escape(r.filename)))
    content += [
        h("Agentic process and limitations"),
        tiny(
            "Planner -> RETRIEVE -> CALCULATE -> REPORT -> FINISH. Each action "
            "updates agent state, then the planner chooses the next node. "
            "The bounded loop terminates when the report is complete."
        ),
        tiny(
            "All reported numbers are obtained from supplied 10-K financial tables; "
            "calculations use Python Decimal. LSA semantic retrieval supplements "
            "(but does not replace) exact structured retrieval. "
            "All dollars are USD; figures in tables are USD millions. "
            "Fiscal 2025 is the latest in the assigned dataset."
        ),
        h("Execution trace"),
    ]
    actions = [
        step.rsplit(" -> ", 1)[-1] for step in state.trace if "planner ->" in step
    ]
    content.append(tiny(escape(" -> ".join(actions))))
    return content


def write_pdf(states: list[AgentState], output: Path, charts: list[Path] | None = None):
    styles = make_styles()
    story = []
    for i, state in enumerate(states):
        if i:
            story.append(PageBreak())
        chart_path = charts[i] if charts else None
        story.extend(report_elements(state, styles, chart_path))
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=42,
        rightMargin=42,
        topMargin=35,
        bottomMargin=35,
    )
    doc.build(story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)


QUESTIONS = {
    "Q1": "How did the company's total revenue change between 2023 and 2025?",
    "Q2": "Which product category contributed the most revenue in the latest year?",
    "Q3": "How did Services revenue change from 2023 to 2025, and what share of 2025 total net sales did Services represent?",
}

RESULTS = {}
CHARTS = {}
for key, question in QUESTIONS.items():
    state = run_agent(question)
    RESULTS[key] = state
    markdown_path = REPORT_DIR / f"{key}_report.md"
    markdown_path.write_text(state.report_markdown, encoding="utf-8")
    mdformat.file(markdown_path, extensions={"gfm"})
    chart_path = REPORT_DIR / f"{key}_chart.png"
    make_chart(state, chart_path)
    CHARTS[key] = chart_path
    write_pdf([state], REPORT_DIR / f"{key}_report.pdf", [chart_path])
    print(f"\n{key}: {question}\n{state.answer}")
    print("Actions:", " -> ".join(step.rsplit(" -> ", 1)[-1] for step in state.trace))
    print("Sources:", "; ".join(sorted({r.citation for r in state.records})))

write_pdf(
    list(RESULTS.values()),
    REPORT_DIR / "All_3_Financial_Analysis_Reports.pdf",
    [CHARTS[q] for q in QUESTIONS],
)

summary = {
    key: {
        "question": st.question,
        "project_repository": REPOSITORY_URL,
        "intent": st.intent,
        "answer": st.answer,
        "calculations": st.calculations,
        "retrieved_records": [asdict(r) for r in st.records],
        "semantic_matches": st.semantic_matches,
        "agent_trace": st.trace,
    }
    for key, st in RESULTS.items()
}
(REPORT_DIR / "agent_results.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)
print("\nReports exported to:", REPORT_DIR.relative_to(ROOT))

assert FINANCE.get(2023, "category", TOTAL_LABEL).value_usd_millions == 383285
assert FINANCE.get(2024, "category", TOTAL_LABEL).value_usd_millions == 391035
assert FINANCE.get(2025, "category", TOTAL_LABEL).value_usd_millions == 416161
assert FINANCE.get(2025, "category", "iPhone").value_usd_millions == 209586
assert FINANCE.get(2023, "category", "Services").value_usd_millions == 85200
assert FINANCE.get(2025, "category", "Services").value_usd_millions == 109158
assert decimal_percent_change(383285, 416161) == Decimal("8.58")
assert decimal_percent_change(85200, 109158) == Decimal("28.12")
assert RESULTS["Q2"].calculations["winner"] == "iPhone"
assert RESULTS["Q3"].calculations["share_of_new_year_total"] == "26.23"
for result in RESULTS.values():
    actions = [item.split(" -> ")[-1] for item in result.trace if "planner ->" in item]
    assert actions == ["RETRIEVE", "CALCULATE", "REPORT", "FINISH"]
    assert result.report_done and not result.error
    assert result.records and all(r.filename.endswith(".pdf") for r in result.records)
print("All financial, provenance, and agent-loop tests passed.")

extra = run_agent("How did Europe's net sales change between 2023 and 2025?")
print(extra.answer)
extra = run_agent("What share of total net sales did iPad represent in 2024?")
print(extra.answer)
