# Part 8 — Điểm (part2 sync, so với async dưới contention hiện tại)

**Mục đích:** đo part2 (sync, 0 fail) NGAY BÂY GIỜ để so với async (part7=46.27, 90 fail) cùng điều kiện contention.

| Chỉ số | async (part7, hiện tại) | part8 = part2 sync |
|---|---|---|
| final_score | 46.27 | _chờ_ |
| TTFT p50 | 55 | _chờ_ |
| **failed_count** | 90 | _chờ (kỳ vọng ~0)_ |

## Cách đọc
- **part8 > 46.27** (và fail ~0) → sync BỀN hơn khi contention cao → **chọn part2 cho bài chốt.**
- **part8 < 46.27** → async vẫn nhỉnh hơn dù fail → giữ part4 (51.54 banked).
- Dù sao: **part4=51.54 (async, lúc ít contention) vẫn banked** — là điểm sàn tốt nhất đã ghi.
