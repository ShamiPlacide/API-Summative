# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY wrapify.py /app

ENV ENVIRONMENT=production

# Expose the Flask port
EXPOSE 80

# Run the Flask app
CMD ["python", "wrapify.py"]
