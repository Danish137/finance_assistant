# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent's code into the container
COPY data_ingestion/scraping_agent/ ./data_ingestion/scraping_agent/

# Expose the port the Scraping Agent will listen on
EXPOSE 8002

# Command to run the Scraping Agent
CMD ["uvicorn", "data_ingestion.scraping_agent.main:app", "--host", "0.0.0.0", "--port", "8002"] 