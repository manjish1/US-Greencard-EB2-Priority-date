# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port 8080 for Fly.io
EXPOSE 8080

# Run the app with gunicorn
CMD ["gunicorn", "-b", ":8080", "app:app"] 