# Part 12 — Điểm (rollback part11 + max-model-len 8192) — 🏆 **ALL-TIME HIGH (grading mới)**

**Config:** part2 (sync FP8, default piecewise graph, prefix-cache, kv-fp8) **+** `--max-model-len=8192`
(từ 4608). Bỏ enforce-eager (part11) và compilation-config (part9). Image `sub-01`, command-only.

## KẾT QUẢ (chấm 2026-07-23) — final_score **60.11** ⬆️⬆️ (từ 50.38, +9.73đ)

| Chỉ số | part9 (nền, 4608) | part11 (eager, 4608) | **part12 (8192)** |
|---|---|---|---|
| final_score / ers | 50.38 | 27.74 | **60.11** |
| f_delta / penalty | 1 / 1 | 1 / 1 | 1 / 1 |
| **failed_count** | 75 | 76 | **5** ← 🔥 |
| total_count | 420 | 420 | 420 |
| **TPOT (tbt) median** | 4 ms | 10 ms | **4 ms** ✅ phục hồi |
| TTFT p50 / p95 | 48 / 75 ms | 74 / 120 ms | **45 / 80 ms** |
| accuracy_drop | 0 | 0 | 0 |
| tokens_per_sec | — | 0.0546 | 0.0646 |

## Kết luận — giả thuyết context-overflow ĐÚNG, đảo ngược kết luận part11

**part11 đã kết luận sai "fails = structural cold-start"** vì nó chỉ đổi startup-time (enforce-eager) mà
**vẫn giữ nguyên `--max-model-len=4608`** — nên tất nhiên fails không đổi (76). Kết luận đúng ra phải là
"startup-time không phải nguyên nhân", KHÔNG PHẢI "fails là structural". part12 đổi đúng biến còn lại
(context length) và **fails rơi từ 75 → 5 (giảm 93%)**. Điều này chứng minh:

1. **~70/75 fails trước đây là 400 context-overflow reject**, không phải cold-start timing. Đây là phép thử
   MIỄN PHÍ duy nhất chưa ai đụng qua 11 part — và nó chính là đòn bẩy lớn nhất còn lại.
2. TPOT phục hồi đúng 4ms (default piecewise graph vẫn nguyên, không đổi) — xác nhận lại part11: **luôn
   giữ default graph, không bao giờ `--enforce-eager`.**
3. TTFT p50 thậm chí **tốt hơn part9** (45 vs 48ms) dù max-len tăng gấp đôi — KV cache dư dả không ảnh
   hưởng latency ở concurrency thấp (~5). Đúng như giả thuyết "chi phí ~0" trong SUMMARY.md.
4. TTFT p95 nhích nhẹ (80 vs 75ms) — nhiễu đo / có thể do 415 request thành công thay vì 345 (nhiều dữ
   liệu hơn ở tail). Không đáng lo.

## Trần điểm cập nhật (thay thế ước tính "~51" trong part11/memory — ĐÃ SAI)

Với 415/420 thành công, s_ttft(45ms)≈0.83, s_tpot(4ms)≈0.44 → ERS ước tính ≈ 0.988×(0.5·0.83+0.5·0.44)
≈ **0.629 (~63đ)** — khớp với 60.11 đo được (chênh lệch do dùng p50/median thay vì mean thật + đuôi p95).

**Nếu diệt nốt 5 fail còn lại:** ERS ước tính chỉ tăng thêm **~0.7-1 điểm** (5×~0.63/420) — biên tế nhỏ.
**TPOT (s_tpot=0.44) vẫn là số hạng thua thiệt lớn nhất**, nhưng đã xác nhận floor 3 lần (part2/part9/part11)
→ không còn đòn bẩy config nào được biết để hạ dưới 4ms.

## → Part13
Xem `versions/part13/SUMMARY.md`: đẩy tiếp `--max-model-len=8192→12288` (rẻ, đúng phương pháp 1-biến) để
kiểm 5 fail còn lại có phải overflow nốt hay là floor thật (~5 = cold-start/network jitter thuần).
Song song: **chạy GPQA thật** (`eval/bench-gpqa-diamond.sh`) cho config FP8 này — Δ mới chỉ đo bằng
arc_challenge proxy (Δ≈0), CHƯA đo GPQA thật — đây là rủi ro lớn nhất còn lại cho `f(Δ)` ở vòng chọn 5 bài.
