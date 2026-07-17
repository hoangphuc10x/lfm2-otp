# Part 1 — Phiên bản 1 (baseline tối ưu đầu tiên)

**Ngày tạo:** 2026-07-17
**Trạng thái:** chờ điểm từ leaderboard (điền vào `score.md` khi có).
**Image tag dự kiến:** `hoangphuc109/lfm2-otp:sub-01`

---

## Logic & các file đã thực hiện

### Đóng gói (submission-critical — snapshot trong `files/`)
- **Dockerfile** — base `vllm/vllm-openai:v0.22.1`, bake weights `LiquidAI/LFM2.5-1.2B-Instruct`
  vào `/model` lúc build (không network lúc serve — RULES.md R1.3). Không set ENTRYPOINT/CMD
  (để docker-compose khai báo theo ràng buộc BTC).
- **docker-compose.yml** — cấu hình serve, giữ nguyên các dòng `#Don't change this to vllm-server`.

### Tham số vLLM (điểm khác biệt so với config mẫu BTC)
| Tham số | Giá trị part1 | Lý do |
|---|---|---|
| `--max-model-len` | **4608** | context thật ~4k+200; giảm từ 32768 → tiết kiệm KV cache → concurrency cao hơn |
| `--enable-prefix-caching` | bật | multi-turn → hit rate cao → giảm TTFT |
| `--kv-cache-dtype` | **fp8** | gấp đôi token cache được (cần kiểm Δ accuracy) |
| `--gpu-memory-utilization` | 0.92 | chừa VRAM cho CUDA graph/activation |
| CUDA graphs | bật (không `--enforce-eager`) | giảm overhead TTFT batch nhỏ |

### Hạ tầng benchmark (dùng chung, không đổi mỗi submission)
- `bench/ers.py` — tính ERS đúng công thức đề bài (F/C TTFT-TPOT, γ=2, w=0.5). Đã self-test.
- `bench/trace.py` — đọc trace + tổng hợp prompt giữ prefix chung theo conversation.
- `bench/run_bench.py` — phát lại trace (arrival Poisson), đo TTFT/TPOT streaming, tính ERS.
- `bench/make_synthetic_trace.py` — sinh trace test khi chưa có trace thật.
- `eval/bench-gpqa-diamond.sh` — kiểm accuracy GPQA → ước lượng Δ.

---

## Giả thuyết tối ưu của part1
Prefix caching + KV FP8 + giảm max-len là 3 đòn bẩy ROI cao nhất, rủi ro thấp.
Kỳ vọng: TTFT giảm mạnh nhờ prefix cache (multi-turn), TPOT ổn nhờ model nhỏ 1.2B.
Rủi ro cần theo dõi: KV FP8 có thể làm tụt accuracy (Δ) — phải kiểm trước khi coi là bài chốt.

## ERS đo cục bộ (nếu có)
_(điền sau khi chạy run_bench.py)_
