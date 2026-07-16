#!/usr/bin/env bash
# Build + push image giải pháp. Mỗi submission = 1 tag cố định (RULES.md R4.2).
#
#   DOCKERHUB_USER=myuser TAG=sub-01 bash scripts/build_and_push.sh
#
set -euo pipefail

: "${DOCKERHUB_USER:?Cần đặt DOCKERHUB_USER}"
TAG="${TAG:-sub-01}"
IMAGE="${DOCKERHUB_USER}/lfm2-otp:${TAG}"
HF_TOKEN="${HF_TOKEN:-}"

echo "[build] $IMAGE"
docker build --build-arg HF_TOKEN="$HF_TOKEN" -t "$IMAGE" .

echo "[push] $IMAGE (phải Public trên Docker Hub)"
docker push "$IMAGE"

echo
echo "Xong. Cập nhật docker-compose.yml -> image: $IMAGE"
echo "Rồi ghi mapping tag <-> config <-> ERS <-> Δ vào notes/submissions.md (RULES.md R4.6)"
