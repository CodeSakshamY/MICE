from http.server import BaseHTTPRequestHandler
import json
import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge
import io
import base64
import cgi
from datetime import datetime
from urllib.parse import parse_qs

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

def process_excel_file(file_data, method='auto', iterations=10):
    """Process Excel file and apply MICE imputation"""
    try:
        df = pd.read_excel(io.BytesIO(file_data))
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

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            # Get content type and boundary
            content_type = self.headers['Content-Type']

            if 'multipart/form-data' not in content_type:
                self.send_error(400, 'Content-Type must be multipart/form-data')
                return

            # Parse multipart form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )

            # Get file
            if 'file' not in form:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No file provided'}).encode())
                return

            file_item = form['file']

            if not file_item.filename:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No file selected'}).encode())
                return

            if not file_item.filename.endswith(('.xlsx', '.xls')):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid file format'}).encode())
                return

            # Get form parameters
            method = form.getvalue('method', 'auto')
            iterations = int(form.getvalue('iterations', 10))

            # Process file
            file_data = file_item.file.read()
            result = process_excel_file(file_data, method=method, iterations=iterations)

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
