# Use the official Python image as base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your application
CMD ["python3", "campus_cash.py"]
