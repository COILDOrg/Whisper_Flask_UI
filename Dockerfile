FROM python:3.11 AS builder

WORKDIR /app
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11
WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app.py \
    PYTHONUNBUFFERED=1

COPY . .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 7860

CMD ["python3", "app.py"]