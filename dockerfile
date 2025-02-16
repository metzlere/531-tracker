# Parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy codebase
COPY . .

# Expose the port
EXPOSE 5000

# Production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
