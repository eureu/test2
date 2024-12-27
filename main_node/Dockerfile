FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 5001

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5001"]

