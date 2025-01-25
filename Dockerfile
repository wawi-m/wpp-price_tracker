# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . /app

# Create a non-root user (optional for security)
RUN useradd -ms /bin/bash appuser
USER appuser

# Define the command to run the application
# CMD ["python", "run.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
