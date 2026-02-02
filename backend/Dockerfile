FROM python:3.10-slim

# Install system dependencies
# tesseract-ocr: for OCR
# tesseract-ocr-eng: English language pack
# tesseract-ocr-kan: Kannada language pack (for your multilingual bills)
# libgl1-mesa-glx: needed for some image processing libs like OpenCV if used, safe to include
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-kan \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Start command
# We use $PORT environment variable which Render sets automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
