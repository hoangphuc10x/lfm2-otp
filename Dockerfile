# Image giải pháp: bake sẵn weights vào /model để KHÔNG cần network lúc serve
# (RULES.md R1.3). Base là image vLLM baseline được BTC cho phép.
#
# Build:
#   docker build -t <user>/lfm2-otp:sub-01 .
# Push (phải Public — RULES.md R4.3):
#   docker push <user>/lfm2-otp:sub-01
#
# Network chỉ dùng lúc BUILD để tải weights — hợp lệ. Lúc RUN không gọi mạng.

FROM vllm/vllm-openai:v0.22.1

ARG MODEL_REPO=LiquidAI/LFM2.5-1.2B-Instruct
# Tải weights lúc build bằng huggingface_hub, lưu vào /model.
# HF_TOKEN chỉ cần nếu repo yêu cầu; truyền qua --build-arg khi cần.
ARG HF_TOKEN=""

ENV HF_HUB_ENABLE_HF_TRANSFER=1

RUN pip install --no-cache-dir "huggingface_hub[hf_transfer]" && \
    HF_TOKEN="${HF_TOKEN}" python3 -c "\
from huggingface_hub import snapshot_download; \
snapshot_download(repo_id='${MODEL_REPO}', local_dir='/model', \
    ignore_patterns=['*.pth','*.bin.index.json.lock','original/*'])" && \
    pip uninstall -y hf_transfer || true

# Config vLLM (chứa speculative_config) — trỏ bằng --config=/vllm_config.yaml.
# Baked vào image để tránh lỗi mất quotes khi truyền JSON qua command (part3).
COPY vllm_config.yaml /vllm_config.yaml

# Không đặt ENTRYPOINT/CMD ở đây — docker-compose.yml khai báo entrypoint/command
# theo đúng ràng buộc BTC (python3 -m vllm.entrypoints.openai.api_server).
