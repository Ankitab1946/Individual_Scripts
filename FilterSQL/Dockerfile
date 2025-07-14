# Use a minimal base image with Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit with no CORS limit so external access works
CMD ["streamlit", "run", "your_script_name.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]
