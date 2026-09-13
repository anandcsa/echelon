#!/usr/bin/env bash
# Provision only after packaging succeeds. No credentials are placed in VM metadata.
set -euo pipefail
PROJECT=${ECHELON_GCP_PROJECT:-gen-lang-client-0773193027}
ZONE=${ECHELON_GCP_ZONE:-us-central1-a}
REGION=${ZONE%-*}
VM=echelon-stream
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
PACKAGE=${1:?Usage: GCP/provision.sh /absolute/path/to/packaged/Linux [hostname]}
PACKAGE=$(realpath "$PACKAGE")
[[ -f "$PACKAGE/Echelon.sh" ]] || { echo 'Package must contain Echelon.sh; compile Unreal first.' >&2; exit 1; }
[[ -d "$PACKAGE/Echelon/Binaries/Linux" ]] || { echo 'Missing native Linux game binary directory.' >&2; exit 1; }
[[ -f "$ROOT/GCP/player/dist/index.html" ]] || { echo 'Build GCP/player first.' >&2; exit 1; }
# All names scoped to Echelon. Do not reuse/modify other game or team VMs.
gcloud compute networks describe "$VM" --project "$PROJECT" >/dev/null 2>&1 || gcloud compute networks create "$VM" --subnet-mode=custom --project "$PROJECT"
gcloud compute networks subnets describe "$VM-$REGION" --region "$REGION" --project "$PROJECT" >/dev/null 2>&1 || gcloud compute networks subnets create "$VM-$REGION" --network "$VM" --range=10.86.0.0/24 --region "$REGION" --project "$PROJECT"
gcloud compute firewall-rules describe "$VM-iap" --project "$PROJECT" >/dev/null 2>&1 || gcloud compute firewall-rules create "$VM-iap" --network "$VM" --allow=tcp:22 --source-ranges=35.235.240.0/20 --target-tags="$VM" --project "$PROJECT"
gcloud compute firewall-rules describe "$VM-player" --project "$PROJECT" >/dev/null 2>&1 || gcloud compute firewall-rules create "$VM-player" --network "$VM" --allow=tcp:80,tcp:443,tcp:3478,udp:3478,udp:49152-49351 --source-ranges=0.0.0.0/0 --target-tags="$VM" --project "$PROJECT"
# Fail if already present, rather than unexpectedly replacing an existing deployment.
gcloud compute instances create "$VM" --project "$PROJECT" --zone "$ZONE" \
 --machine-type=g2-standard-8 --network="$VM" --subnet="$VM-$REGION" --tags="$VM" \
 --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud \
 --boot-disk-size=100GB --boot-disk-type=pd-balanced --maintenance-policy=TERMINATE \
 --no-restart-on-failure --no-service-account --no-scopes \
 --max-run-duration=4h --instance-termination-action=STOP \
 --labels=app=echelon,purpose=streaming-preview
IP=$(gcloud compute instances describe "$VM" --zone "$ZONE" --project "$PROJECT" --format='value(networkInterfaces[0].accessConfigs[0].natIP)')
HOST=${2:-${IP}.sslip.io}
[[ "$HOST" =~ ^[a-zA-Z0-9.-]+$ ]] || { echo 'Invalid hostname' >&2; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
# Only the packaged game and built player are transferred; no Epic source or cloud credentials.
if command -v pigz >/dev/null 2>&1; then
 tar --exclude='*/Saved' --exclude='*/Intermediate' --exclude='*/DerivedDataCache' -I 'pigz -1 -p 4' -cf "$TMP/game.tar.gz" -C "$PACKAGE" .
else
 tar --exclude='*/Saved' --exclude='*/Intermediate' --exclude='*/DerivedDataCache' -czf "$TMP/game.tar.gz" -C "$PACKAGE" .
fi
tar -czf "$TMP/player.tar.gz" -C "$ROOT/GCP/player/dist" .
# Fresh VMs need time to boot and accept the IAP SSH key.
SSH_READY=false
for attempt in $(seq 1 30); do
 if gcloud compute ssh "$VM" --tunnel-through-iap --project "$PROJECT" --zone "$ZONE" --quiet --ssh-flag='-o ConnectTimeout=10' --command=true; then
  SSH_READY=true
  break
 fi
 sleep 10
done
[[ "$SSH_READY" == true ]] || { echo 'VM created, but SSH is not ready; inspect before retrying.' >&2; exit 1; }
gcloud compute scp --tunnel-through-iap --project "$PROJECT" --zone "$ZONE" "$TMP/game.tar.gz" "$TMP/player.tar.gz" "$ROOT/GCP/install-runtime.sh" "$VM:~/"
gcloud compute ssh "$VM" --tunnel-through-iap --project "$PROJECT" --zone "$ZONE" --command="sudo bash ./install-runtime.sh '$HOST' '$IP'"
printf 'After the driver reboot, verify https://%s and inspect journalctl -u echelon-game.\n' "$HOST"
printf 'Preview login is stored only on the VM at /root/echelon-preview-login. Retrieve it over IAP SSH.\n'
