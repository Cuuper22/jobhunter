#!/bin/bash
# JobHunter AI Agent — GCP Infrastructure Setup
# Run this once to set up all required GCP resources.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Billing enabled on the GCP project
#
# Usage:
#   export PROJECT_ID=gen-lang-client-0362384446
#   bash infrastructure/setup.sh

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID env var}"
REGION="${REGION:-us-central1}"

echo "=== Setting up JobHunter infrastructure ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project "$PROJECT_ID"

# 1. Enable required APIs
echo "--- Enabling APIs ---"
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudtasks.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  firebase.googleapis.com

# 2. Create Firestore database (if it doesn't exist)
echo "--- Creating Firestore database ---"
gcloud firestore databases create --type=firestore-native --location=nam5 2>/dev/null || \
  echo "Firestore database already exists"

# 3. Create Cloud Storage buckets
echo "--- Creating storage buckets ---"
gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://${PROJECT_ID}-resumes" 2>/dev/null || true
gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://${PROJECT_ID}-screenshots" 2>/dev/null || true

# 4. Create Cloud Tasks queue
echo "--- Creating Cloud Tasks queue ---"
gcloud tasks queues create job-applications \
  --location="$REGION" \
  --max-dispatches-per-second=1 \
  --max-concurrent-dispatches=5 \
  --max-attempts=3 \
  --min-backoff=10s \
  --max-backoff=300s 2>/dev/null || \
  echo "Queue already exists"

# 5. Set billing alerts
echo "--- Setting billing alerts ---"
# Note: Billing budgets require the Billing API and are better set via Console
echo "WARNING: Set billing alerts manually in GCP Console:"
echo "  - Alert at \$20"
echo "  - Alert at \$40"
echo "  - Budget cap at \$50"

# 6. Store Gemini API key in Secret Manager
echo "--- Storing secrets ---"
if [ -n "${GEMINI_API_KEY:-}" ]; then
  echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=- 2>/dev/null || \
    echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-
  echo "Gemini API key stored in Secret Manager"
else
  echo "GEMINI_API_KEY not set — skipping secret creation"
fi

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "  1. Set billing alerts in GCP Console"
echo "  2. Upload resume to gs://${PROJECT_ID}-resumes/"
echo "  3. Deploy services: bash infrastructure/deploy.sh"
