# Publish the gene expression app and get its live URL

## Part A: Upload the project to GitHub

1. Download and **extract** `Gene_Expression_GitHub_Ready.zip` on your computer.
2. Sign into https://github.com/ and click **+** > **New repository**.
3. Repository name suggestion: `gene-expression-qc-tool`.
4. Select **Public** (easiest for a class demo) and click **Create repository**.
5. Choose **uploading an existing file** / **Add file > Upload files**.
6. Open the extracted project folder and upload **the files inside it**, not the ZIP file or an enclosing folder. Include `app.py`, `processor.py`, `requirements.txt`, `README.md`, `DEPLOYMENT_GUIDE.md`, the two sample CSVs, and `tests/test_processor.py`. The `.streamlit/config.toml` file is optional for deployment; some browsers hide dotted folders. If it is missing, the app still runs.
7. Click **Commit changes**.
8. In your GitHub repository, you should see `app.py` and `requirements.txt` immediately at the top level (root).

## Part B: Create the live application

1. Open https://share.streamlit.io/ and sign in using GitHub.
2. Click **Create app** / **New app** and select **Deploy a public app from GitHub** if offered.
3. Select the repository you created above.
4. Branch: `main` (or whichever branch your repo uses).
5. Main file path / entrypoint: **`app.py`**.
6. Choose a unique app subdomain if prompted; deploy.
7. Once the app opens successfully, copy the actual URL, usually `https://your-chosen-name.streamlit.app/`.
8. Test the online app with `example_expression.csv` before submitting the link to your professor.

**Important:** Uploading the files to GitHub does not itself generate a working Python app URL. The Streamlit Cloud deployment above is required.

## If deployment fails
- **ModuleNotFoundError:** Check that `requirements.txt` is in the same root directory as `app.py` and contains `streamlit`, `pandas`, `numpy`, `openpyxl`.
- **File not found / entrypoint error:** Main file path must be exactly `app.py`, and it must be in the repository root.
- **No repositories shown:** Check your GitHub/Streamlit authorization and repository access.
- **File fails to load:** Use the example input to check the expected format: column 1 is gene ID, other columns are sample measurements.
- **TPM errors:** Upload a separate gene-length CSV with columns `gene_id,length_bp`; lengths must be positive and cover every gene.
- **App sleeping:** Community Cloud may put idle apps to sleep. Open the URL to wake it before demonstrating.

## Suggested details for project submission
- **Project title:** Gene Expression Data Format Converter and QC Tool
- **GitHub URL:** `https://github.com/YOUR-USERNAME/gene-expression-qc-tool`
- **Live app URL:** paste the real Streamlit link after deployment succeeds
- **Team:** Hasini Upputuri and Nainika Medarametla
