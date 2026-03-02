#!/bin/bash
# JobHunter AI Agent — Deploy all services to GCP
#
# Usage:
#   export PROJECT_ID=gen-lang-client-0362384446
#   export API_PASSWORD=your-secure-password
#   bash infrastructure/deploy.sh

set -euo pipefail

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID env var}"
REGION="${REGION:-us-central1}"
API_PASSWORD="${API_PASSWORD:-}"

echo "=== Deploying JobHunter services ==="

# 1. Deploy Agent-Browser (via Cloud Build)
echo "--- Building & deploying agent-browser ---"
gcloud builds submit \
  --config=cloudbuild-agent.yaml \
  --project="$PROJECT_ID" \
  .

gcloud run deploy agent-browser \
  --image "us-central1-docker.pkg.dev/$PROJECT_ID/jobhunter/agent-browser:latest" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --platform managed \
  --memory 2Gi \
  --cpu 2 \
  --concurrency 1 \
  --max-instances 3 \
  --timeout 900 \
  --cpu-boost \
  --set-env-vars "PROJECT_ID=$PROJECT_ID,REGION=$REGION,SCREENSHOTS_BUCKET=${PROJECT_ID}-screenshots,APPLICANT_EMAIL=${APPLICANT_EMAIL},APPLICANT_PHONE=${APPLICANT_PHONE}" \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
  --no-allow-unauthenticated

# 2. Deploy API Gateway (via Cloud Build)
echo "--- Building & deploying api-gateway ---"
gcloud builds submit \
  --config=cloudbuild-gateway.yaml \
  --project="$PROJECT_ID" \
  .

gcloud run deploy api-gateway \
  --image "us-central1-docker.pkg.dev/$PROJECT_ID/jobhunter/api-gateway:latest" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --platform managed \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 5 \
  --set-env-vars "PROJECT_ID=$PROJECT_ID,REGION=$REGION,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,AGENT_BROWSER_URL=https://agent-browser-73685042772.us-central1.run.app,API_PASSWORD=$API_PASSWORD" \
  --allow-unauthenticated  # Password auth handled at app level

# 3. Deploy Dashboard (via Cloud Build)
echo "--- Building & deploying dashboard ---"
GATEWAY_URL=$(gcloud run services describe api-gateway --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')

gcloud builds submit \
  --config=cloudbuild-frontend.yaml \
  --project="$PROJECT_ID" \
  .

gcloud run deploy dashboard \
  --image "us-central1-docker.pkg.dev/$PROJECT_ID/jobhunter/dashboard:latest" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --platform managed \
  --memory 256Mi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 3 \
  --set-env-vars "NODE_ENV=production" \
  --allow-unauthenticated

# 4. Get service URLs
AGENT_URL=$(gcloud run services describe agent-browser --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')
GATEWAY_URL=$(gcloud run services describe api-gateway --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')
DASHBOARD_URL=$(gcloud run services describe dashboard --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')

echo ""
echo "=== Deployment complete ==="
echo "Agent-Browser: $AGENT_URL"
echo "API Gateway:   $GATEWAY_URL"
echo "Dashboard:     $DASHBOARD_URL"
echo ""

# 5. Set up Cloud Scheduler (runs every 3 hours)
echo "--- Setting up Cloud Scheduler ---"

# Get the API gateway service account for auth
SA_EMAIL=$(gcloud run services describe api-gateway --region="$REGION" --project="$PROJECT_ID" --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || echo "")
if [ -z "$SA_EMAIL" ]; then
  SA_EMAIL="${PROJECT_ID//-/_}@${PROJECT_ID}.iam.gserviceaccount.com"
fi

# Create or update the scheduler job
gcloud scheduler jobs delete jobhunter-cycle --location="$REGION" --project="$PROJECT_ID" --quiet 2>/dev/null || true

gcloud scheduler jobs create http jobhunter-cycle \
  --project="$PROJECT_ID" \
  --location="$REGION" \
  --schedule="0 */3 * * *" \
  --uri="${GATEWAY_URL}/api/scheduler/trigger" \
  --http-method=POST \
  --oidc-service-account-email="$SA_EMAIL" \
  --oidc-token-audience="$GATEWAY_URL" \
  --attempt-deadline=900s \
  --description="Trigger JobHunter scrape-and-process cycle every 3 hours"

echo "Cloud Scheduler: jobhunter-cycle (every 3 hours)"
echo ""
echo "Done! Dashboard: $DASHBOARD_URL"
