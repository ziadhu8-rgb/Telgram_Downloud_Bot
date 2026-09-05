# Stage 1: Build the Application
FROM python:3.11-slim AS build

WORKDIR /usr/src/app

# تثبيت system dependencies (بما فيها ffmpeg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements.txt
COPY requirements.tx[t] ./requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    if [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    fi

# Copy the rest of the application source code
COPY . .

# Stage 2: Create the Final Production Image
FROM python:3.11-slim

WORKDIR /usr/src/app

# تثبيت ffmpeg في المرحلة النهائية (الحل الأضمن)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the build stage
COPY --from=build /opt/venv /opt/venv

# Copy the application code
COPY --from=build /usr/src/app .

# Set the virtual environment as the active Python environment
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user to run the application
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /usr/src/app
USER appuser

# Expose the port your app runs on
ENV PORT=8080
EXPOSE $PORT

# Define the command to start your application
CMD ["python", "Bot.py"]
