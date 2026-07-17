# Submissions log

Bảng theo dõi từng bài nộp. Cần khi chọn ≤ 5 bài cuối cho GPQA (RULES.md R4.6).

| Tag | Ngày | Cấu hình chính | ERS local | **final_score** | Δ | TTFT p50/p95 | TPOT med | Ghi chú |
|-----|------|----------------|-----------|-----------------|---|--------------|----------|---------|
| part1 | 2026-07-17 | prefix-cache + **kv**-fp8 + max-len 4608 (weights BF16) | — | **43.82** | 0* | 98/147 ms | 5 ms | 0 fail. baseline |
| part2 | 2026-07-17 | + `--quantization=fp8` (FP8 weights) | — | **55.23** | 0* | 80/117 ms | 4 ms | **+11.4đ**. Δ thật CHƯA đo (GPQA) |
| part3 | — | + speculative decoding (n-gram) | — | _dự kiến_ | — | — | mục tiêu ~2ms | đòn bẩy TPOT |

*Δ online = default, chưa chạy GPQA. `config_hash` băm theo IMAGE, không theo command args.

## Nhật ký thử nghiệm (điền dần)

### sub-01
- **Config:** `--enable-prefix-caching --kv-cache-dtype=fp8 --max-model-len=4608 --gpu-memory-utilization=0.92`
- **Giả thuyết:** prefix caching giảm TTFT (multi-turn); KV FP8 tăng concurrency; giảm max-len tiết kiệm KV cache.
- **ERS local:** _(chạy `run_bench.py` rồi điền)_
- **Δ accuracy:** _(chạy `eval/bench-gpqa-diamond.sh` rồi điền — mục tiêu Δ ≤ 0.10)_
- **Quan sát / bước tiếp theo:**
