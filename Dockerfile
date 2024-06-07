# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8091

# Set environment variables
ENV PROJECT_ID=tatvic-gcp-dev-team
ENV BQ_CREDENTIALS_PATH=/app/credentials.json
ENV SLACK_WEBHOOK_URL=https://hooks.slack.com/services/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

# Copy the credentials file into the container
# Make sure you have the credentials file in your local directory
COPY credentials.json /app/credentials.json

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "temp:app", "--host", "0.0.0.0", "--port", "8091"]