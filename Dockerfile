# Use a small Python base image
FROM python:3.9-slim

# Set Working Directory inside the container
WORKDIR /app

# Install dependencies first (better cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the project 
COPY app/ ./app/
COPY tests/ ./tests/

# Expose Flask port 
EXPOSE 5001

# Run the flask app ( same as you do locally)
CMD ["python3", "-m", "app.app"]

