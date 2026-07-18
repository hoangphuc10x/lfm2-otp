# Tie-break & Khiếu nại

Khi điểm sát nhau (≤ 1–2 điểm, trong biên nhiễu), xếp hạng theo thứ tự:
1. Mức độ suy giảm accuracy (Δ nhỏ hơn thắng).
2. **p95 TTFT** thấp hơn.
3. Tốc độ sinh văn bản (TPOT) nhanh hơn.
4. Thời điểm nộp sớm hơn.

→ **Hệ quả tối ưu:** đừng chỉ tối ưu mean; **p95 TTFT** cũng là tiêu chí phụ → cần giảm tail latency (tránh queueing spikes). Xem [optimization-discipline.md](optimization-discipline.md) R2.3.

Khiếu nại: trong 24h kể từ email thông báo kết quả dự kiến. BTC có quyền chấm lại lấy trung vị nhiều lần chạy.
