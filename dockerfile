# Use an official Python runtime as a parent image
FROM python:3.10.11-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add current directory code to /app in container
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the application:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
