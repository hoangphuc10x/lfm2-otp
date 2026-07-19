# Part 6 — async + cap max-num-seqs (probe overload)

**Ngày:** 2026-07-19 · **Dựa trên:** part4 (async, 51.54 — BEST hiện tại) · **Trạng thái:** chờ nộp.

## Bối cảnh
BTC đổi cách chấm (chấm cả 420 request, bỏ warmup). async (part4) giờ là best 51.54,
nhưng còn ~74 fail (nghi cold-start hoặc quá tải 3-CPU). Diệt fail → mục tiêu ~64đ.

## Thay đổi so với part4 (1 biến)
Thêm `--max-num-seqs=64` → giảm số sequence đồng thời → nhẹ tải scheduler trên 3-CPU.

## Giả thuyết & cách đọc
- **Nếu fail giảm mạnh** → đúng là async quá tải 3-CPU → thử tinh chỉnh thêm (32/48).
- **Nếu fail KHÔNG giảm** (vẫn ~74) → fail là **cold-start** → chuyển part7 (warm-up/precompile).
  Lưu ý: concurrency workload có thể vốn thấp → nếu vậy max-num-seqs không đổi gì (kết quả ~ part4).

## Rủi ro
- Cap quá thấp → queueing → TTFT tăng → có thể thêm timeout. 64 là mức vừa (có headroom).
- Fallback: part4 (async, 51.54) / part2.

## Việc cần làm
1. Nộp part6 → xem failed_count so với 74.
2. Nếu không rõ, chẩn đoán RunPod (ghim 3-CPU, đo request đầu) để phân định cold-start vs overload.
