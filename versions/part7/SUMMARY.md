# Part 7 — async + max-num-batched-tokens=8192

**Ngày:** 2026-07-19 · **Dựa trên:** part4 (async, 51.54 = best) · **Trạng thái:** chờ nộp.

## Thay đổi so với part4 (1 biến)
Thêm `--max-num-batched-tokens=8192` (>= max-model-len 4608) → prefill prompt dài trong 1 step,
không bị chunk.

## Giả thuyết
- Prefill nhanh hơn → **TTFT thấp hơn**.
- Request đầu (cold-start) prefill nhanh hơn → **có thể ít timeout/fail hơn**.
- An toàn: chỉ là param batching/memory, không gây crash/instability. VRAM 18GB thừa cho model 1.2B.

## Cách đọc
- TTFT giảm và/hoặc failed_count giảm so với part4 (42ms, 74 fail) → giữ.
- Không đổi hoặc tệ hơn → bỏ, thử part8 (bỏ --kv-cache-dtype=fp8).

## Lưu ý
- Điểm gần đây có thể bị nhiễu/drift do contention BTC → chỉ tin thay đổi RÕ RỆT (> ~3đ).
- Fallback: part4 (async, 51.54) đã banked.
