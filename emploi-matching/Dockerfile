# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app/emploi-matching
ENV OLLAMA_API_URL="http://host.docker.internal:11434/api/generate"
ENV DATABASE_URL="sqlite:///emploi.db"

# Copy the requirements file into the container at /app/emploi-matching
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
# RUN python src/main.py   # ne pas active que si on veux re cree la base est c'est trés tres long

# Expose the port that FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]