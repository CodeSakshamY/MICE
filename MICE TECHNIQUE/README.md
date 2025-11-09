# MICE Imputation Tool

A beautiful and elegant web application for filling missing values in Excel files using the MICE (Multivariate Imputation by Chained Equations) technique.

## Features

- Drag-and-drop file upload interface
- Multiple imputation methods:
  - Auto (Recommended)
  - Predictive Mean Matching (PMM)
  - Bayesian Ridge
  - Random Forest
- Customizable number of iterations
- Real-time processing feedback
- Beautiful, modern UI with smooth animations
- Download imputed Excel files
- Statistics about filled values

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Deploy to Vercel (Recommended for Production)

1. **Install Vercel CLI** (if not already installed):
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy to Vercel**:
```bash
cd "/Users/ARUN/Desktop/MICE TECHNIQUE"
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? Select your account
- Link to existing project? **No**
- What's your project's name? **mice-imputation** (or any name you prefer)
- In which directory is your code located? **./** (press Enter)
- Want to override settings? **No**

4. Vercel will deploy your app and provide a URL like: `https://your-project.vercel.app`

5. Your app is now live! Visit the URL to use the MICE imputation tool.

### Option 2: Run Locally

1. Start the Flask backend server:
```bash
python3 app.py
```

The server will start on `http://localhost:5000`

2. Open the frontend in your browser:
   - Simply open `index.html` in your web browser

## Usage

1. **Upload File**: Click "Browse Files" or drag and drop your Excel file (.xlsx or .xls)
2. **Configure Options**:
   - Set the number of iterations (default: 10)
   - Choose an imputation method (default: Auto)
3. **Process**: Click "Process File" to start the MICE imputation
4. **Download**: Once complete, download your imputed Excel file

## How MICE Works

MICE (Multivariate Imputation by Chained Equations) is a sophisticated statistical technique that:

1. Models each variable with missing values as a function of other variables
2. Iteratively imputes missing values using regression models
3. Produces more accurate imputations than simple methods like mean/median filling
4. Preserves relationships between variables in your data

## Supported File Types

- Excel 2007+ (.xlsx)
- Excel 97-2003 (.xls)

Maximum file size: 10MB

## Project Structure

```
MICE TECHNIQUE/
├── index.html          # Frontend HTML
├── style.css           # Styling and animations
├── script.js           # Frontend JavaScript
├── app.py              # Flask backend server (for local development)
├── api/                # Vercel serverless functions
│   ├── upload.py       # File upload and processing endpoint
│   └── health.py       # Health check endpoint
├── vercel.json         # Vercel configuration
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
└── README.md          # This file
```

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Flask (Python) with Vercel serverless functions
- **Data Processing**: Pandas, NumPy, scikit-learn
- **Excel Handling**: openpyxl, xlrd
- **Deployment**: Vercel

## Troubleshooting

**Server not connecting:**
- Make sure the Flask server is running (`python app.py`)
- Check that port 5000 is not being used by another application

**File upload fails:**
- Ensure your file is a valid Excel format (.xlsx or .xls)
- Check that the file size is under 10MB
- Verify the file contains numeric data for imputation

**Imputation errors:**
- Ensure your Excel file contains at least some numeric columns
- Check that there are enough non-missing values for the algorithm to learn from

## License

MIT License - Feel free to use and modify as needed!

## Support

For issues or questions, please check the Flask server logs for detailed error messages.
