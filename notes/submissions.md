# Submissions log

Bảng theo dõi từng bài nộp. Cần khi chọn ≤ 5 bài cuối cho GPQA (RULES.md R4.6).

| Tag | Ngày | Cấu hình chính | ERS local | **final_score** | Δ | TTFT p50/p95 | TPOT med | Ghi chú |
|-----|------|----------------|-----------|-----------------|---|--------------|----------|---------|
| part1 | 2026-07-17 | prefix-cache + **kv**-fp8 + max-len 4608 (weights BF16) | — | **43.82** | 0* | 98/147 ms | 5 ms | 0 fail. baseline |
| part2 | 2026-07-17 | + `--quantization=fp8` (FP8 weights) | — | **55.23** | 0* | 80/117 ms | 4 ms | **+11.4đ**. Δ thật CHƯA đo (GPQA) |
| part3 | 2026-07-18 | + speculative decoding (n-gram) | — | ❌ **FAIL** | — | — | — | 330/330 transport errors, server crash. Rollback về part2 |

### ⚠️ BTC ĐỔI CÁCH CHẤM (2026-07-19)
Giờ chấm **cả 420 request, KHÔNG miễn 90 warmup** → cold-start tính cho mọi config. Điểm cũ bị hạ:
- **part4 (async) = 51.54 → CAO NHẤT hiện tại.** part2 tụt còn ~50.
- Chiến lược mới: **cold-start giờ quan trọng.** async có TTFT tốt nhất (42ms) nhưng ~74 fail cold-start.
  → Diệt fail này mà giữ TTFT 42ms → **~64đ**. Đây là ROI cao nhất.
- Nghi phạm fail: **cold-start compile chậm trên 3-CPU của BTC → primer timeout** (async làm lộ rõ hơn sync).

*Δ online = default, chưa chạy GPQA. `config_hash` băm theo image+command (không theo healthcheck).

**Accuracy FP8 đã kiểm (2026-07-18, arc_challenge proxy):** BF16 acc_norm=0.4121 vs FP8=0.4155 → **Δ≈0, FP8 không tụt accuracy**. part2 an toàn ở Accuracy Gate. Spec decode (part3) đã loại (crash hybrid).

## Nhật ký thử nghiệm (điền dần)

### sub-01
- **Config:** `--enable-prefix-caching --kv-cache-dtype=fp8 --max-model-len=4608 --gpu-memory-utilization=0.92`
- **Giả thuyết:** prefix caching giảm TTFT (multi-turn); KV FP8 tăng concurrency; giảm max-len tiết kiệm KV cache.
- **ERS local:** _(chạy `run_bench.py` rồi điền)_
- **Δ accuracy:** _(chạy `eval/bench-gpqa-diamond.sh` rồi điền — mục tiêu Δ ≤ 0.10)_
- **Quan sát / bước tiếp theo:**
