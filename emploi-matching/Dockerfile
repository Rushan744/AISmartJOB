# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app/emploi-matching

# Copy the requirements file into the container at /app/emploi-matching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]