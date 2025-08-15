FROM python:3.11-slim
RUN apt-get update && apt-get install -y cmake g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY opencpn-libs /workspace/opencpn-libs
COPY chart-tiler /workspace/chart-tiler
RUN pip install --no-cache-dir -r chart-tiler/requirements.txt
COPY web-client /workspace/web-client
WORKDIR /workspace/chart-tiler
CMD ["uvicorn", "tileserver:app", "--host", "0.0.0.0", "--port", "8000"]
