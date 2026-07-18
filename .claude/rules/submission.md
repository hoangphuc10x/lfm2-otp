# Quy trình nộp bài & Docker

## Quy trình nộp

1. **Develop & Package** — code giải pháp + tối ưu → đóng gói thành **1 Docker Image**.
2. **Push Image** — đẩy lên Docker Hub cá nhân/tổ chức, để **Public**.
3. **Submit** — nộp `docker-compose.yml` (khai báo chính xác đường dẫn image + lệnh chạy) lên Portal BTC.
4. **Automated Evaluation** — hệ thống pull image → dựng container trên MiG H200 → healthcheck → chạy benchmark ERS (KHÔNG chạy GPQA mỗi lượt).
5. **Leaderboard** — cập nhật theo ERS.
6. **Sau online** — chọn ≤ 5 submissions → BTC hậu kiểm hợp lệ → chạy GPQA full → chốt Score.

## Quy tắc Docker & nộp bài (R4)

- **R4.1** — Base image: `vllm/vllm-openai:v0.22.1` (hoặc phiên bản đã kiểm chứng tương thích). Weights bake sẵn vào `/model`.
- **R4.2** — Tag image **có phiên bản** (vd `:sub-01`, `:sub-02`), **không dùng `latest`** mơ hồ cho bài nộp. 1 submission = 1 tag không đổi.
- **R4.3** — Image phải **Public** trên Docker Hub trước khi nộp.
- **R4.4** — Trước khi nộp: chạy checklist bên dưới. Container phải healthcheck pass và không có request fail dưới tải trace.
- **R4.5** — `docker-compose.yml` nộp phải trỏ đúng `image:tag` đã push và giữ ràng buộc R1.6/R1.7 (xem [golden-rules.md](golden-rules.md)).
- **R4.6** — Lưu lại mapping: `submission tag ↔ config ↔ ERS đo được ↔ Δ accuracy` trong `notes/submissions.md`. Cần khi chọn ≤ 5 bài cuối.

## Baseline image
`vllm/vllm-openai:v0.22.1`

## docker-compose.yml mẫu (BTC cung cấp)
Các dòng có comment `#Don't change this to vllm-server` **phải giữ nguyên entrypoint/command dạng module** (`python3 -m vllm.entrypoints.openai.api_server`), không đổi sang lệnh `vllm-server`.

```yaml
services:
  model:
    image: vllm/vllm-openai:v0.22.1
    entrypoint:
      - python3                                    #Don't change this to vllm-server
      - -m                                         #Don't change this to vllm-server
      - vllm.entrypoints.openai.api_server         #Don't change this to vllm-server
    command:
      - --model=/model                             #Don't change this to vllm-server
      - --served-model-name=LFM2.5-1.2B-Instruct   #Don't change this to vllm-server
      - --host=0.0.0.0                             #Don't change this to vllm-server
      - --port=8000                                #Don't change this to vllm-server
      - --max-model-len=32768
      - --gpu-memory-utilization=0.95
      - --tensor-parallel-size=1
      - --enable-prefix-caching
    ports:
      - "8000:8000"
    shm_size: "2g"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Lưu ý cấu hình để tối ưu (so với mẫu):**
- `--served-model-name=LFM2.5-1.2B-Instruct` — giữ nguyên tên này (BTC gọi endpoint theo tên).
- `--model=/model` — weights nằm ở path `/model` trong container.
- `--max-model-len` có thể giảm mạnh (~4300) để tiết kiệm KV cache.
- `--gpu-memory-utilization` có thể đẩy cao (nhưng chừa VRAM cho CUDA graph/activation).
- `--port=8000`, `--host=0.0.0.0` — giữ nguyên.

## Checklist trước khi nộp mỗi submission

- [ ] Container khởi động & healthcheck pass trên cấu hình gần giống MiG (18GB VRAM).
- [ ] Endpoint OpenAI-compatible tại `:8000`, `served-model-name=LFM2.5-1.2B-Instruct`.
- [ ] Không có request nào timeout / trả 0 token dưới tải trace (mọi fail = 0 điểm).
- [ ] Đã đo ERS cục bộ, ghi lại số + cấu hình vào `bench/results/`.
- [ ] Không vi phạm anti-cheating (xem [golden-rules.md](golden-rules.md)).
- [ ] Image đã push Public lên Docker Hub, tag cố định (không mutable `latest` mơ hồ).
- [ ] `docker-compose.yml` trỏ đúng image + tag đã push.
- [ ] (Trước khi chọn 5 bài cuối) đã kiểm Δ accuracy.
