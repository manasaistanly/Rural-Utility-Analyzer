# Smart Rural Utility Consumption Analysis and Forecasting

This project is a bilingual (Telugu/English) web application designed for rural households to analyze electricity and water consumption using OCR and Machine Learning.

## Project Structure

- **backend/**: FastAPI application (Python)
  - `app/`: Source code
  - `requirements.txt`: Python dependencies
- **frontend/**: React application (Vite + Tailwind)
  - `src/`: Source code
- **ml_models/**: Directory for saving trained ML models
- **data/**: Directory for uploads and datasets

## Quick Start

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Key Features
- **OCR**: Extract data from bills (Basic Regex/Tesseract).
- **Voice Output**: Text-to-Speech info in Telugu/English.
- **Forecasting**: ML-based predictions (mock logic used for prototype).
- **Bilingual**: Full UI localization.

## Database
Configured to use PostgreSQL. Update `backend/app/core/config.py` with your credentials.
