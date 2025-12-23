#!/bin/bash

# Start API server
cd "$(dirname "$0")"
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

