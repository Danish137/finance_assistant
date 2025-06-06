FROM python:3.10-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential

# Set working directory
WORKDIR /app

# Copy requirements file separately for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app
COPY . .

# Expose Gradio port
EXPOSE 7860

# Run the Gradio app
CMD ["python", "gradio_app/app.py"]
