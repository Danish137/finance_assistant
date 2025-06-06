# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the gradio app code into the container
COPY gradio_app/ ./gradio_app/
COPY audio_outputs/ ./audio_outputs/
COPY .env .

# Expose the port the Gradio app will listen on
EXPOSE 7860

# Command to run the Gradio app
CMD ["python", "gradio_app/app.py", "--host", "0.0.0.0", "--port", "7860", "--share", "False"] 