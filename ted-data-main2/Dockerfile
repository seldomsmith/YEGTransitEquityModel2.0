FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless libgdal-dev g++ wget unzip && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x setup_data.sh
CMD ["bash", "-c", "./setup_data.sh && python3 test_pipeline.py"]
