# Use a lightweight Python image
FROM python:3.12-slim

# Prevents Python from buffering stdout/stderr (so logs show up immediately)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first so Docker can reuse the dependency layer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application source code
COPY . .

# Application listens on port 8000
EXPOSE 8000

# Apply migrations and start FastAPI
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]