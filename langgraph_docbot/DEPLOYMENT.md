# 🚀 Deployment Guide

This project supports deployment to Google Cloud Platform (Cloud Run).

## Quick Start from Zero

1. **Install Requirements**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Locally**:
   ```bash
   ./start_server.sh
   # In another terminal:
   ./run_streamlit.sh
   ```

3. **Deploy to GCP**:
   
   See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a 3-step rapid deployment.
   
   See [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md) for a comprehensive, step-by-step guide including troubleshooting.

## Configuration

Ensure you have your `GOOGLE_API_KEY` set up.
- For local run: in `.env` file.
- For GCP: in Secret Manager (see guides above).
