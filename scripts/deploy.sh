#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
SERVICE=${ECHELON_SERVICE:-echelon-breakpoint}
DEPLOYED_REVISION=$(gcloud run deploy "$SERVICE" --source . --project gen-lang-client-0773193027 --region us-central1 --allow-unauthenticated --port 8080 --memory 512Mi --cpu 1 --min-instances 0 --max-instances 2 --concurrency 20 --service-account echelon-director@gen-lang-client-0773193027.iam.gserviceaccount.com --set-env-vars GCP_PROJECT=gen-lang-client-0773193027,FIRESTORE_DATABASE=echelon-world,DIRECTOR_MODEL=gemini-2.5-flash-lite,AI_DAILY_LIMIT=300 --quiet --format='value(status.latestCreatedRevisionName)')
[[ "$DEPLOYED_REVISION" == "$SERVICE"-* ]] || { echo 'Deployment did not return a revision name.' >&2; exit 1; }
# A pinned service otherwise keeps serving its previous revision after a successful build.
gcloud run services update-traffic "$SERVICE" --project gen-lang-client-0773193027 --region us-central1 --to-revisions="$DEPLOYED_REVISION=100" --quiet
