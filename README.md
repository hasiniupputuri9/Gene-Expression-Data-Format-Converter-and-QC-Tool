# Gene Expression Data Format Converter and QC Tool

**Python course project** | Hasini Upputuri & Nainika Medarametla

A small Streamlit web app that accepts gene-by-sample expression tables, checks data quality, and lets you download converted files. The first column must contain gene IDs; remaining columns are sample measurements.

## Features
- Upload CSV, TSV, tab-separated TXT, or XLSX expression matrices.
- Preview the uploaded table.
- Report missing/non-numeric values, duplicate/blank gene IDs, negative/infinite values, and per-sample summary statistics.
- Download a JSON QC report and CSV sample statistics.
- Convert expression matrices to CSV, TSV, or XLSX.
- Optionally normalize nonnegative raw counts to CPM or TPM (TPM requires a gene-length file).
- Optionally sum duplicate gene IDs for raw counts only.

**Scope:** This prototype handles tabular expression matrices only. It does not process raw sequence files (FASTQ/BAM), convert H5AD, perform biological validation, or automatically clean missing/non-numeric values.

## Files
| File | Purpose |
| --- | --- |
| `app.py` | Streamlit web interface; use as the deployment entrypoint |
| `processor.py` | QC, conversion, and normalization functions |
| `requirements.txt` | Python dependencies needed for deployment |
| `.streamlit/config.toml` | Basic app appearance and upload limit |
| `example_expression.csv` | Sample expression matrix for a demo |
| `example_gene_lengths.csv` | Gene lengths in bp to demonstrate TPM |
| `tests/test_processor.py` | Automated processing tests |
| `.gitignore` | Exclude temporary/local files from GitHub |
| `DEPLOYMENT_GUIDE.md` | Exact steps to get a publicly shareable app URL |

## Run on your own computer
Python 3.10+ is recommended; use Python 3.11 on Streamlit Cloud if prompted.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Upload `example_expression.csv` and try **CPM** or format conversion. For TPM, upload `example_gene_lengths.csv` when requested.

## Test
```bash
python -m pip install pytest
python -m pytest -q
```

## Live app
After deployment, paste your actual app URL here: `https://YOUR-APP-NAME.streamlit.app/`.

Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) to deploy. GitHub stores the files; Streamlit Community Cloud **runs** the Python app. GitHub Pages alone will not run this server-side Python app.
