from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge
import io
import base64
from datetime import datetime

app = Flask(__name__)

def get_imputer(method='auto', max_iter=10):
    """Create an imputer based on the selected method"""
    if method == 'bayesian':
        estimator = BayesianRidge()
    elif method == 'rf':
        estimator = RandomForestRegressor(n_estimators=10, random_state=42)
    else:
        estimator = BayesianRidge()

    return IterativeImputer(
        estimator=estimator,
        max_iter=max_iter,
        random_state=42,
        verbose=0
    )

def process_excel_file(file, method='auto', iterations=10):
    """Process Excel file and apply MICE imputation"""
    try:
        df = pd.read_excel(file)
        original_shape = df.shape
        missing_before = df.isnull().sum().sum()

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
        non_numeric_data = df[non_numeric_cols].copy()

        if len(numeric_cols) > 0:
            imputer = get_imputer(method=method, max_iter=iterations)
            numeric_data = df[numeric_cols].copy()
            imputed_numeric = imputer.fit_transform(numeric_data)
            df_imputed = pd.DataFrame(imputed_numeric, columns=numeric_cols)

            for col in non_numeric_cols:
                df_imputed[col] = non_numeric_data[col]

            df_imputed = df_imputed[df.columns]
        else:
            df_imputed = df.copy()

        missing_after = df_imputed.isnull().sum().sum()

        stats = {
            'missing_filled': int(missing_before - missing_after),
            'total_rows': int(original_shape[0]),
            'total_cols': int(original_shape[1]),
            'missing_before': int(missing_before),
            'missing_after': int(missing_after)
        }

        # Convert to Excel bytes
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_imputed.to_excel(writer, index=False, sheet_name='Imputed Data')
        output.seek(0)

        # Encode file as base64 for JSON response
        file_base64 = base64.b64encode(output.getvalue()).decode('utf-8')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"imputed_{timestamp}.xlsx"

        return {
            'success': True,
            'file_data': file_base64,
            'filename': output_filename,
            'stats': stats
        }

    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload an Excel file'}), 400

        method = request.form.get('method', 'auto')
        iterations = int(request.form.get('iterations', 10))

        result = process_excel_file(file, method=method, iterations=iterations)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# For Vercel serverless
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
