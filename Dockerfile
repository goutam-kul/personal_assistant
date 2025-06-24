# Use Python Alpine base image
FROM python:3.12.11-alpine3.22

# Set working directory inside container
WORKDIR /app

# Install system dependencies required by some Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy requirement file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the codebase
COPY . .

# Run app (adjust if using Flask vs FastAPI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
