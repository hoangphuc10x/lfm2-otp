# Part 5 — Điểm (async + warmup healthcheck) — THẤT BẠI

**Chấm:** 2026-07-19 · **config_hash:** `sha256:603c84...853881` — **GIỐNG HỆT part4**.

| Chỉ số | part2 | part4 | **part5** |
|---|---|---|---|
| final_score | 55.23 | 51.54 | **49.01** ❌ |
| TTFT p50 | 80 | 42 | 47 |
| TTFT p95 | 117 | 71 | 73 |
| TPOT median | 4 | 4 | 4 |
| **failed_count** | 0 | 74 | **88** |
| total_count | 330 | 420 | 420 |
| warmup_count | 90 | 0 | 0 |

## Kết luận (quan trọng)
1. **config_hash part4 == part5** → **healthcheck KHÔNG nằm trong hash; BTC bỏ qua healthcheck của compose.**
   → Warmup-qua-healthcheck **vô tác dụng**. Cách này chết.
2. **51.54 vs 49.01 (cùng config) = nhiễu ~2.5đ.** async ổn định ở ~80 fail, ~50đ.
3. **Cơ chế fail:** `warmup_count=0`, `failed_count≈88 ≈ 90 primer`. → **async-scheduling làm request primer (cold-start) FAIL** thay vì chạy-chậm-thành-công như part2. Primer fail → mất warmup → chấm cả 420 (gồm ~88 fail) → tụt điểm.
4. **warmup/total tương quan với CONFIG (async), không phải thời điểm grading** → grading KHÔNG đổi; async là thủ phạm.

## Quyết định
- ❌ **BỎ async-scheduling** — không warmup được (BTC bỏ qua healthcheck), primer fail chí mạng.
- ✅ **Revert part2 (55.23, 0 fail)** — best an toàn.
- Xác nhận: re-nộp part2 (kỳ vọng vẫn 330/90/0-fail/55.23 → chốt async là nguyên nhân).

## Bài học
- BTC dùng **healthcheck riêng** (không phải của compose) → không thể can thiệp thời điểm bắt đầu chấm.
- Tối ưu nào **làm fail request lúc cold-start** đều bị phạt nặng (mất warmup + fail). Config phải **ổn định ngay từ request đầu**.
