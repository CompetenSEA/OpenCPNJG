FROM python:3.11-slim
RUN apt-get update && apt-get install -y cmake g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
COPY opencpn-libs /workspace/opencpn-libs
COPY chart-tiler /workspace/chart-tiler
COPY web-client /workspace/web-client
CMD ["bash"]
