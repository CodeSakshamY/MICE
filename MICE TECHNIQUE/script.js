// Use relative URLs for Vercel deployment, fallback to localhost for development
const API_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : '';

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadSection = document.getElementById('uploadSection');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeBtn = document.getElementById('removeBtn');
const processBtn = document.getElementById('processBtn');
const processing = document.getElementById('processing');
const resultSection = document.getElementById('resultSection');
const downloadBtn = document.getElementById('downloadBtn');
const newFileBtn = document.getElementById('newFileBtn');
const iterationsInput = document.getElementById('iterations');
const methodSelect = document.getElementById('method');

// State
let selectedFile = null;
let currentFileId = null;
let processedFileData = null; // Store base64 file data for Vercel

// Event Listeners
browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
uploadBox.addEventListener('click', (e) => {
    if (e.target === uploadBox || e.target.closest('.upload-icon, h2, p')) {
        fileInput.click();
    }
});
uploadBox.addEventListener('dragover', handleDragOver);
uploadBox.addEventListener('dragleave', handleDragLeave);
uploadBox.addEventListener('drop', handleDrop);
removeBtn.addEventListener('click', resetUpload);
processBtn.addEventListener('click', processFile);
downloadBtn.addEventListener('click', downloadFile);
newFileBtn.addEventListener('click', resetUpload);

// Functions
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        validateAndDisplayFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file) {
        validateAndDisplayFile(file);
    }
}

function validateAndDisplayFile(file) {
    // Check file type
    const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ];

    if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls)$/i)) {
        alert('Please upload a valid Excel file (.xlsx or .xls)');
        return;
    }

    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size must be less than 10MB');
        return;
    }

    selectedFile = file;
    displayFileInfo(file);
}

function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    uploadSection.style.display = 'none';
    fileInfo.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function resetUpload() {
    selectedFile = null;
    currentFileId = null;
    processedFileData = null;
    fileInput.value = '';

    uploadSection.style.display = 'block';
    fileInfo.style.display = 'none';
    processing.style.display = 'none';
    resultSection.style.display = 'none';
}

async function processFile() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }

    // Hide file info and show processing
    fileInfo.style.display = 'none';
    processing.style.display = 'block';

    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('method', methodSelect.value);
    formData.append('iterations', iterationsInput.value);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to process file');
        }

        if (data.success) {
            // Store file data for download (supports both Vercel and local)
            if (data.file_data) {
                processedFileData = {
                    data: data.file_data,
                    filename: data.filename
                };
            } else {
                currentFileId = data.file_id;
            }
            displayResults(data.stats);
        } else {
            throw new Error('Processing failed');
        }

    } catch (error) {
        console.error('Error:', error);
        alert(`Error processing file: ${error.message}`);
        // Reset to file info on error
        processing.style.display = 'none';
        fileInfo.style.display = 'block';
    }
}

function displayResults(stats) {
    processing.style.display = 'none';
    resultSection.style.display = 'block';

    // Update statistics
    document.getElementById('missingCount').textContent = stats.missing_filled;
    document.getElementById('totalRows').textContent = stats.total_rows;
    document.getElementById('totalCols').textContent = stats.total_cols;

    // Animate the numbers
    animateValue('missingCount', 0, stats.missing_filled, 1000);
    animateValue('totalRows', 0, stats.total_rows, 1000);
    animateValue('totalCols', 0, stats.total_cols, 1000);
}

function animateValue(id, start, end, duration) {
    const element = document.getElementById(id);
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

async function downloadFile() {
    try {
        // For Vercel deployment (base64 data)
        if (processedFileData) {
            const byteCharacters = atob(processedFileData.data);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = processedFileData.filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            return;
        }

        // For local server (file ID)
        if (!currentFileId) {
            alert('No file to download');
            return;
        }

        const response = await fetch(`${API_URL}/download/${currentFileId}`);

        if (!response.ok) {
            throw new Error('Failed to download file');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `imputed_${selectedFile.name}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error('Error:', error);
        alert(`Error downloading file: ${error.message}`);
    }
}

// Check server status on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) {
            console.warn('Server not responding');
        }
    } catch (error) {
        console.warn('Cannot connect to server. Make sure the Flask server is running.');
    }
});
