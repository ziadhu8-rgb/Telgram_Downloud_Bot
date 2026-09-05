# Stage 1: Build the Application
FROM python:3.11 AS build

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
FROM python:3.11

WORKDIR /usr/src/app

# Copy the virtual environment from the build stage
COPY --from=build /opt/venv /opt/venv

# Copy the application code
COPY --from=build /usr/src/app .

# Copy ffmpeg and ffprobe with their libraries from build stage
COPY --from=build /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=build /usr/bin/ffprobe /usr/bin/ffprobe
COPY --from=build /usr/lib/x86_64-linux-gnu/libavcodec.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libavformat.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libavutil.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libswscale.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libswresample.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libavdevice.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libavfilter.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libpostproc.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libx264.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libx265.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libvpx.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libmp3lame.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libopus.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libvorbis.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libtheora.so* /usr/lib/x86_64-linux-gnu/
COPY --from=build /usr/lib/x86_64-linux-gnu/libspeex.so* /usr/lib/x86_64-linux-gnu/

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
