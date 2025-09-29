# Gebruik Python base image
FROM python:3.12-slim

# Werkomgeving
WORKDIR /app

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code + PDF
COPY . .

# Poort
ENV PORT 8080

# Start de app
CMD ["python", "main.py"]
