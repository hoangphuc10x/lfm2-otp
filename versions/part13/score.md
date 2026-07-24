# Part 13 — Điểm (max-model-len 8192 → 12288)

**Config:** part12 (banked, 60.11 ATH) **+** `--max-model-len=12288` (từ 8192). Image `sub-01`, command-only.

| Chỉ số | part9 (4608, graph) | part11 (eager) | part12 (8192) | **part13 (12288)** |
|---|---|---|---|---|
| final_score / ers | 50.38 | 27.74 | **60.11** | _chờ_ |
| **failed_count** | 75 | 76 | **5** | **_chờ (kỳ vọng: ↓0-1 nếu overflow tiếp, else ~5 = floor thật)_** |
| TPOT (tbt) median | 4 ms | 10 ms | 4 ms | _chờ (kỳ vọng 4ms — không đổi)_ |
| TTFT p50 / p95 | 48 / 75 ms | 74 / 120 ms | 45 / 80 ms | _chờ (kỳ vọng ~45ms — không đổi)_ |
| accuracy_drop | 0 | 0 | 0 | _chờ (kỳ vọng 0 — không đụng weights)_ |

**Câu hỏi part13 trả lời:** 5 fail còn lại của part12 có phải overflow hiếm (>8192) không?
- **fails → 0-1** → có → +~1đ, giữ 12288, đóng sổ hướng fails (đã sạch).
- **fails ~5 không đổi** → floor thật (jitter/edge-case, không liên quan context) → khóa sổ vĩnh viễn,
  chuyển hẳn trọng tâm sang GPQA/f(Δ) (xem SUMMARY.md).

**Nhận xét:** _(điền khi có điểm)_
