# Submissions log

Bảng theo dõi từng bài nộp. Cần khi chọn ≤ 5 bài cuối cho GPQA (RULES.md R4.6).

| Tag | Ngày | Cấu hình chính | ERS (local) | ERS (leaderboard) | Δ accuracy (ước lượng) | Ghi chú |
|-----|------|----------------|-------------|-------------------|------------------------|---------|
| sub-01 | | prefix-cache + kv-fp8 + max-len 4608 | | | | baseline tối ưu đầu tiên |

## Nhật ký thử nghiệm (điền dần)

### sub-01
- **Config:** `--enable-prefix-caching --kv-cache-dtype=fp8 --max-model-len=4608 --gpu-memory-utilization=0.92`
- **Giả thuyết:** prefix caching giảm TTFT (multi-turn); KV FP8 tăng concurrency; giảm max-len tiết kiệm KV cache.
- **ERS local:** _(chạy `run_bench.py` rồi điền)_
- **Δ accuracy:** _(chạy `eval/bench-gpqa-diamond.sh` rồi điền — mục tiêu Δ ≤ 0.10)_
- **Quan sát / bước tiếp theo:**
