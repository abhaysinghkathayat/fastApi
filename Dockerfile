# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy all contents into the container
COPY . .

# Install uvicorn, gunicorn for production, and any other dependencies
RUN pip install --no-cache-dir uvicorn gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Expose port 80 for production, or port 8000 for development with uvicorn
EXPOSE 80

# Command to run the uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
