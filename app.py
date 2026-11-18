"""Streamlit prototype: gene expression matrix converter and QC dashboard."""
import json
from io import BytesIO
import pandas as pd
import streamlit as st
from processor import (analyze_expression, normalize_cpm, normalize_tpm,
                       prepare_matrix, read_expression_file, to_bytes)

st.set_page_config(page_title='Gene Expression Converter & QC', layout='wide')
st.title('Gene Expression Data Format Converter & QC Tool')
st.write('Upload a gene-by-sample expression table. The first column must contain gene IDs; each other column should contain numeric values for one sample.')
st.caption('This prototype supports tabular expression matrices (CSV, TSV, TXT, Excel), not FASTQ/BAM/CRAM or single-cell H5AD conversion.')

uploaded = st.file_uploader('Upload expression matrix', type=['csv', 'tsv', 'txt', 'xlsx'])
if uploaded is None:
    st.info('Try the included example_expression.csv file to explore the app.')
    st.stop()

try:
    raw = read_expression_file(uploaded, uploaded.name)
    matrix, qc, stats = analyze_expression(raw)
except Exception as exc:
    st.error(f'Could not read file: {exc}')
    st.stop()

st.subheader('Preview')
st.dataframe(raw.head(15), use_container_width=True)
cols = st.columns(4)
for col, key, label in zip(cols, ['genes', 'samples', 'missing_values', 'duplicate_gene_ids'],
                           ['Gene rows', 'Samples', 'Missing values', 'Duplicate gene IDs']):
    col.metric(label, qc[key])
st.subheader('Quality control checks')
st.dataframe(pd.DataFrame([{'check': k.replace('_', ' ').title(), 'count': v}
                            for k, v in qc.items()]), hide_index=True, use_container_width=True)
st.subheader('Per-sample statistics')
st.dataframe(stats, hide_index=True, use_container_width=True)
st.download_button('Download QC report (JSON)', data=json.dumps(qc, indent=2),
                   file_name='qc_report.json', mime='application/json')
st.download_button('Download sample statistics (CSV)',
                   data=stats.to_csv(index=False), file_name='sample_statistics.csv', mime='text/csv')

st.subheader('Conversion / normalization')
aggregate = st.checkbox('Sum duplicate gene IDs (appropriate for raw count matrices only)', value=False)
method = st.selectbox('Data processing', ['No normalization', 'CPM', 'TPM'])
lengths_upload = None
if method == 'TPM':
    st.info('Upload a CSV/TSV with columns gene_id and length_bp. Lengths must be positive and cover every gene.')
    lengths_upload = st.file_uploader('Gene lengths file', type=['csv', 'tsv'], key='lengths')
target = st.selectbox('Output file format', ['CSV', 'TSV', 'Excel'])
try:
    output = prepare_matrix(matrix, aggregate_duplicates=aggregate)
    if method == 'CPM':
        output = normalize_cpm(output)
    elif method == 'TPM':
        if lengths_upload is None:
            st.warning('Upload a gene lengths file to calculate TPM.')
            st.stop()
        sep = '\t' if lengths_upload.name.lower().endswith('.tsv') else ','
        length_table = pd.read_csv(lengths_upload, sep=sep)
        if not {'gene_id', 'length_bp'}.issubset(length_table.columns):
            raise ValueError('Gene lengths file must have gene_id and length_bp columns.')
        if length_table['gene_id'].duplicated().any():
            raise ValueError('Gene lengths file contains duplicate gene IDs.')
        lengths = length_table.set_index('gene_id')['length_bp']
        output = normalize_tpm(output, lengths)
    st.dataframe(output.head(15), use_container_width=True)
    extensions = {'CSV': ('csv','text/csv'), 'TSV': ('tsv','text/tab-separated-values'),
                  'Excel': ('xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    ext, mime = extensions[target]
    st.download_button('Download converted expression data',
                       data=to_bytes(output, target), file_name=f'expression_output.{ext}', mime=mime)
except Exception as exc:
    st.error(f'Processing could not continue: {exc}')
