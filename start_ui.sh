#!/bin/sh
set -e

exec streamlit run ui/app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-8501}" \
  --server.headless true
