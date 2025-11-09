from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge
import io
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store processed files temporarily
processed_files = {}

def get_imputer(method='auto', max_iter=10):
    """Create an imputer based on the selected method"""
    if method == 'bayesian':
        estimator = BayesianRidge()
    elif method == 'rf':
        estimator = RandomForestRegressor(n_estimators=10, random_state=42)
    else:  # 'pmm' or 'auto'
        estimator = BayesianRidge()  # Default to Bayesian Ridge

    return IterativeImputer(
        estimator=estimator,
        max_iter=max_iter,
        random_state=42,
        verbose=0
    )

def process_excel_file(file, method='auto', iterations=10):
    """Process Excel file and apply MICE imputation"""
    try:
        # Read the Excel file
        df = pd.read_excel(file)

        # Store original shape
        original_shape = df.shape

        # Count missing values before imputation
        missing_before = df.isnull().sum().sum()

        # Separate numeric and non-numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns

        # Store non-numeric columns
        non_numeric_data = df[non_numeric_cols].copy()

        # Apply MICE imputation only to numeric columns
        if len(numeric_cols) > 0:
            imputer = get_imputer(method=method, max_iter=iterations)
            numeric_data = df[numeric_cols].copy()

            # Perform imputation
            imputed_numeric = imputer.fit_transform(numeric_data)

            # Create DataFrame with imputed values
            df_imputed = pd.DataFrame(imputed_numeric, columns=numeric_cols)

            # Combine with non-numeric columns
            for col in non_numeric_cols:
                df_imputed[col] = non_numeric_data[col]

            # Reorder columns to match original
            df_imputed = df_imputed[df.columns]
        else:
            df_imputed = df.copy()

        # Count missing values after imputation
        missing_after = df_imputed.isnull().sum().sum()

        # Create statistics
        stats = {
            'missing_filled': int(missing_before - missing_after),
            'total_rows': int(original_shape[0]),
            'total_cols': int(original_shape[1]),
            'missing_before': int(missing_before),
            'missing_after': int(missing_after)
        }

        return df_imputed, stats

    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

@app.route('/upload', methods=['POST'])
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

        # Get options from request
        method = request.form.get('method', 'auto')
        iterations = int(request.form.get('iterations', 10))

        # Process the file
        df_imputed, stats = process_excel_file(file, method=method, iterations=iterations)

        # Generate a unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"imputed_{timestamp}.xlsx"

        # Save to BytesIO object
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_imputed.to_excel(writer, index=False, sheet_name='Imputed Data')
        output.seek(0)

        # Store the file
        file_id = timestamp
        processed_files[file_id] = {
            'data': output.getvalue(),
            'filename': output_filename,
            'stats': stats
        }

        return jsonify({
            'success': True,
            'file_id': file_id,
            'stats': stats,
            'filename': output_filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download the processed file"""
    try:
        if file_id not in processed_files:
            return jsonify({'error': 'File not found'}), 404

        file_data = processed_files[file_id]

        return send_file(
            io.BytesIO(file_data['data']),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=file_data['filename']
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'MICE Imputation API is running'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
