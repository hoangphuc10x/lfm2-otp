# Part 11 — Điểm (`--enforce-eager`) — **THẤT BẠI KÉP (rollback ngay)**

**Config:** part2 (sync FP8) + `--enforce-eager` (bỏ graph). Image sub-01, command-only.

## KẾT QUẢ (chấm 2026-07-23) — final_score **27.74** ⬇️ (từ 50.38)

| Chỉ số | part9 (graphs) | **part11 (eager)** |
|---|---|---|
| final_score / ers | 50.38 | **27.74** |
| **TPOT (tbt) median** | 4 ms | **10 ms** ← = C_tpot ceiling → **s_tpot = 0** |
| TTFT p50 / p95 | 48 / 75 ms | 74 / 120 ms |
| **failed_count** | 75 | **76** ← KHÔNG đổi |
| accuracy_drop | 0 | 0 |
| tokens_per_sec | — | 0.0546 |

## Hai kết luận CỨNG

1. **Fails KHÔNG startup-bound.** enforce-eager = startup nhanh nhất khả dĩ (bỏ hết compile+capture)
   mà fails vẫn 76. Cùng với async (74-89), healthcheck-warmup (88), reduced-capture (75),
   max-num-seqs, batched-tokens — **KHÔNG đòn bẩy config nào chạm được fails.**
   → **~75 fails = floor cold-start CẤU TRÚC** (vLLM+CUDA init ~20-40s vs BTC bắn từ t=0).
   Fix sạch (proxy gate port) bị R1.6/R1.7 cấm. → **Ngừng đốt submit sửa fails bằng config.**

2. **Piecewise CUDA graph mặc định = SỐNG CÒN cho TPOT.** part2 đã có nó (→4ms); FULL thêm (part9) = no-op;
   bỏ hết (eager) → 10ms. → **KHÔNG BAO GIỜ dùng `--enforce-eager`. TPOT 4ms là floor thật.**

## Trần điểm thực tế
ERS ≈ (345/420)×[0.5·s_ttft(48ms)+0.5·s_tpot(4ms)] = 0.821×0.63 ≈ **~51-52đ**. part9/part2 đã gần sát.

**→ part12:** rollback về part2 (default graphs, phục hồi TPOT 4ms) + **max-model-len 8192** (phép thử
MIỄN PHÍ duy nhất chưa làm cho fails: nếu 1 phần fails là context-overflow >4608 → giảm; nếu không → xác nhận
fails cấu trúc, chuyển trọng tâm sang bảo vệ f(Δ) GPQA cho vòng chọn 5 bài).
