"""Tabular gene expression conversion and quality-control functions."""
from io import BytesIO
import numpy as np
import pandas as pd

SUPPORTED_EXTENSIONS = ("csv", "tsv", "txt", "xlsx")


def read_expression_file(source, filename: str) -> pd.DataFrame:
    """Load a gene-by-sample expression table. First column contains gene IDs."""
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError("Upload a CSV, TSV, TXT (tab-delimited), or XLSX file.")
    if ext == 'xlsx':
        df = pd.read_excel(source)
    else:
        df = pd.read_csv(source, sep='\t' if ext in ('tsv', 'txt') else ',')
    if df.shape[1] < 2:
        raise ValueError('File needs a gene ID column and at least one sample column.')
    if not isinstance(df.columns[0], str):
        df.columns = df.columns.map(str)
    return df


def analyze_expression(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Return cleaned numeric matrix, QC metrics and per-sample statistics.

    Missing / nonnumeric entries are *not* imputed: they remain NaN. Duplicate
    gene IDs remain visible for QC until user explicitly chooses aggregation.
    """
    if df.shape[1] < 2:
        raise ValueError('At least one sample column is required.')
    raw = df.copy()
    genes = raw.iloc[:, 0].astype('string').str.strip()
    expression = raw.iloc[:, 1:].copy()
    expression.columns = expression.columns.map(str)
    non_numeric = 0
    for col in expression:
        converted = pd.to_numeric(expression[col], errors='coerce')
        non_numeric += int((expression[col].notna() & converted.isna()).sum())
        expression[col] = converted
    expression.index = pd.Index(genes, name='gene_id')
    invalid_gene_ids = int(genes.isna().sum() + genes.eq('').fillna(False).sum())
    values = expression.to_numpy(dtype=float)
    qc = {
        'genes': int(len(expression)),
        'samples': int(len(expression.columns)),
        'missing_values': int(np.isnan(values).sum()),
        'non_numeric_values': int(non_numeric),
        'duplicate_gene_ids': int(genes.dropna().duplicated(keep='first').sum()),
        'blank_gene_ids': invalid_gene_ids,
        'negative_values': int(np.sum(values < 0)),
        'infinite_values': int(np.isinf(values).sum()),
    }
    sample_stats = pd.DataFrame({
        'sample': expression.columns,
        'missing': expression.isna().sum().to_numpy(),
        'min': expression.min().to_numpy(),
        'max': expression.max().to_numpy(),
        'mean': expression.mean().to_numpy(),
        'total': expression.sum().to_numpy(),
    })
    return expression, qc, sample_stats


def prepare_matrix(expression: pd.DataFrame, aggregate_duplicates: bool = False) -> pd.DataFrame:
    """Reject invalid IDs; optionally sum duplicate IDs for count data."""
    if expression.index.isna().any() or (expression.index.astype('string').str.strip() == '').any():
        raise ValueError('Fix blank or missing gene IDs before processing.')
    if expression.index.has_duplicates:
        if not aggregate_duplicates:
            raise ValueError('Duplicate gene IDs found. Enable aggregation to sum duplicate rows.')
        expression = expression.groupby(level=0, sort=False).sum(min_count=1)
    return expression


def normalize_cpm(matrix: pd.DataFrame) -> pd.DataFrame:
    """CPM for valid, nonnegative raw count matrices."""
    _validate_counts(matrix)
    totals = matrix.sum(axis=0)
    if (totals <= 0).any():
        raise ValueError('Each sample must have a positive total count for CPM.')
    return matrix.div(totals, axis=1) * 1_000_000


def normalize_tpm(matrix: pd.DataFrame, lengths: pd.Series) -> pd.DataFrame:
    """TPM using gene lengths in base pairs; all matrix genes must have lengths."""
    _validate_counts(matrix)
    lengths = pd.to_numeric(lengths.reindex(matrix.index), errors='coerce')
    if lengths.isna().any() or (~np.isfinite(lengths)).any() or (lengths <= 0).any():
        raise ValueError('TPM needs a positive gene length (bp) for every gene.')
    rpk = matrix.div(lengths / 1000, axis=0)
    totals = rpk.sum(axis=0)
    if (totals <= 0).any():
        raise ValueError('Each sample must have a positive RPK total for TPM.')
    return rpk.div(totals, axis=1) * 1_000_000


def _validate_counts(matrix: pd.DataFrame) -> None:
    vals = matrix.to_numpy(dtype=float)
    if not np.isfinite(vals).all() or (vals < 0).any():
        raise ValueError('Normalization requires finite, nonnegative numbers without missing values.')


def to_bytes(matrix: pd.DataFrame, target: str) -> bytes:
    """Export gene IDs as the first column; never silently drop index."""
    df = matrix.copy()
    df.index.name = 'gene_id'
    if target == 'CSV':
        return df.to_csv(index=True).encode('utf-8')
    if target == 'TSV':
        return df.to_csv(sep='\t', index=True).encode('utf-8')
    if target == 'Excel':
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Expression')
        return buffer.getvalue()
    raise ValueError('Choose CSV, TSV, or Excel.')
