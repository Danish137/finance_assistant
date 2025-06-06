# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the Orchestrator will listen on
EXPOSE 8007

# Command to run the Orchestrator
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8007"]