#!/usr/bin/env bash
# Kiểm accuracy GPQA-Diamond cục bộ để ước lượng Δ so với baseline BF16 (CLAUDE.md 3.2).
# Chạy khi endpoint vLLM đã lên. Dùng lm-eval-harness qua OpenAI-compatible API.
#
#   pip install lm-eval
#   bash eval/bench-gpqa-diamond.sh
#
# Δ = Accuracy_baseline(BF16) - Accuracy_submission. Vùng an toàn: Δ <= 0.10 (RULES.md R2.4).
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000/v1}"
MODEL="${MODEL:-LFM2.5-1.2B-Instruct}"
TASK="${TASK:-gpqa_diamond_zeroshot}"
OUT_DIR="${OUT_DIR:-eval/results}"

mkdir -p "$OUT_DIR"

echo "[gpqa] endpoint=$BASE_URL model=$MODEL task=$TASK"

lm_eval \
  --model local-completions \
  --model_args "base_url=${BASE_URL}/completions,model=${MODEL},tokenized_requests=False,num_concurrent=8" \
  --tasks "$TASK" \
  --batch_size auto \
  --output_path "$OUT_DIR"

echo "[gpqa] xong. Xem accuracy trong $OUT_DIR, tính Δ vs baseline BF16 rồi ghi notes/submissions.md"
