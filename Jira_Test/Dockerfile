# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy code
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose default streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "your_script_name.py", "--server.port=8501", "--server.enableCORS=false"]
