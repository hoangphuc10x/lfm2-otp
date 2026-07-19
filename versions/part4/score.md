# Part 4 — Điểm (async scheduling)

**Chấm:** 2026-07-18 · **config_hash:** `sha256:603c84...853881` (KHÁC part1/2 → hash lần này có tính command)

| Chỉ số | part2 | **part4** |
|---|---|---|
| final_score | 55.23 | **51.54** ↓ |
| **TTFT p50** | 80 ms | **42 ms** 🔥 |
| TTFT p95 | 117 ms | **71 ms** 🔥 |
| TPOT median | 4 ms | 4 ms |
| **failed_count** | 0 | **74** ❌ |
| total_count | 330 | 420 |
| warmup_count | 90 | **0** |
| accuracy_drop | 0 | 0 |

## Phân tích
- ✅ `--async-scheduling` **giảm TTFT gần nửa (80→42ms)** — đúng kỳ vọng (giảm overhead scheduler trên 3-CPU của BTC). Đòn bẩy TTFT hiệu quả nhất tìm được.
- ❌ **74 request fail** (17.6% của 420) = 0 điểm mỗi cái → kéo tụt tổng xuống dưới part2.
- **Tiềm năng:** request thành công đạt ~0.64 điểm (TTFT 42 + TPOT 4). Nếu 0 fail → ERS ≈ 0.64 → **~64 điểm**.
  Kiểm: (346×0.64 + 74×0)/420 = 0.527 ≈ 0.5154 ✓.
- **→ Diệt 74 fail = +~12 điểm.** Hướng ROI cao nhất hiện tại.

## Bất thường cần làm rõ
- **total_count 330→420, warmup_count 90→0.** 2 khả năng:
  1. **Grading đổi** (đếm cả 90 primer, không warmup) → part2 chấm lại có thể cũng khác.
  2. **async-scheduling** làm hỏng warmup → 90 request cold-start bị đếm + fail.
- 74 fail ≈ gần 90 (primer) → nghi ngờ **fail tập trung ở cold-start** (model chưa compile xong khi request đầu tới → timeout).

## Hướng tiếp
1. **Re-nộp part2** để phân định: grading đổi hay async gây fail (thông tin rẻ, quan trọng).
2. Nếu async gây fail → mitigations: warmup cold-start, `--gpu-memory-utilization=0.85`, cap `--max-num-seqs`.
3. Giữ part2 (55.23) làm fallback.
