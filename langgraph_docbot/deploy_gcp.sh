#!/bin/bash

# GCP Deployment Script for LangGraph DocBot
# Usage: ./deploy_gcp.sh YOUR_PROJECT_ID

set -e

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required"
    echo "Usage: ./deploy_gcp.sh YOUR_PROJECT_ID"
    exit 1
fi

echo "🚀 Starting deployment to GCP..."
echo "📋 Project ID: $PROJECT_ID"

# Set project
echo "🔧 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Check if secret exists
echo "🔑 Checking for google-api-key secret..."
if ! gcloud secrets describe google-api-key &>/dev/null; then
    echo "⚠️  Secret 'google-api-key' not found!"
    echo "Please create it first:"
    echo "  echo -n 'YOUR_API_KEY' | gcloud secrets create google-api-key --data-file=-"
    read -p "Do you want to create it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -sp "Enter your Google API Key: " API_KEY
        echo
        echo -n "$API_KEY" | gcloud secrets create google-api-key --data-file=-
        echo "✅ Secret created!"
    else
        echo "❌ Cannot proceed without secret. Exiting."
        exit 1
    fi
fi

# Grant access to Cloud Run service account
echo "🔐 Granting secret access to Cloud Run..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --quiet || echo "⚠️  Policy might already exist"

# Build and deploy using Cloud Build
echo "🐳 Building and deploying with Cloud Build..."
BUCKET_NAME="${PROJECT_ID}-build-sources"
if ! gcloud storage buckets describe gs://$BUCKET_NAME &>/dev/null; then
    echo "🪣 Creating Cloud Storage bucket gs://$BUCKET_NAME for build sources..."
    gcloud storage buckets create gs://$BUCKET_NAME --project=$PROJECT_ID --location=us-central1
fi
gcloud builds submit --config cloudbuild.yaml --gcs-source-staging-dir=gs://$BUCKET_NAME/source

# Get service URLs
echo "📊 Getting service URLs..."
FASTAPI_URL=$(gcloud run services describe langgraph-docbot-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)' 2>/dev/null || echo "")

STREAMLIT_URL=$(gcloud run services describe langgraph-docbot-ui \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)' 2>/dev/null || echo "")

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📡 Service URLs:"
echo "  FastAPI:  $FASTAPI_URL"
echo "  Streamlit: $STREAMLIT_URL"
echo ""
echo "🧪 Testing FastAPI health endpoint..."
if [ ! -z "$FASTAPI_URL" ]; then
    curl -s "$FASTAPI_URL/health" && echo "" || echo "⚠️  Health check failed"
fi
echo ""
echo "🎉 Done! Open Streamlit URL in your browser to use the application."



