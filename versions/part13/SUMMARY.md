# Part 13 — max-model-len 8192 → 12288 (kiểm nốt 5 fail còn lại của part12)

**Ngày:** 2026-07-24 · **Dựa trên:** part12 (banked, **60.11 — ATH**, sync FP8, default piecewise graph,
prefix-cache, kv-fp8, max-len 8192, 5 fail). **Đổi 1 biến:** `--max-model-len` 8192 → 12288.
**Command-only, dùng lại image `sub-01`.**

## Vì sao (dữ liệu part12=60.11, đảo ngược kết luận part11)

part11 (`--enforce-eager`, giữ max-len=4608) kết luận sai rằng fails "structural" — vì nó không hề đụng
tới biến gây fail thật sự. part12 đổi đúng biến (max-model-len 4608→8192, giữ nguyên mọi thứ khác) và
**fails rớt 75 → 5 (-93%)**, score 50.38 → **60.11**. Điều này xác nhận gần như toàn bộ fails trước đây là
vLLM reject 400 (context vượt giới hạn) do multi-turn tích lũy context, **không phải cold-start timing**.

## Giả thuyết (R6.1)

- **H:** 5 fail còn lại trong part12 (max-len 8192) vẫn có thể là overflow **hiếm** — vài hội thoại
  multi-turn trong trace có tổng context (lịch sử + output) vượt 8192 dù hiếm hơn nhiều so với vượt 4608.
- **Cách đo:** 12288 dư sức chứa mọi context hợp lý (~4k input theo workload.md + lịch sử multi-turn +
  200 output). Nếu fails → 0 (hoặc gần 0): xác nhận overflow tiếp, giữ 12288. Nếu fails vẫn ~5: đó là floor
  thật (network jitter / edge-case cold-start hiếm, KHÔNG liên quan context) → khóa sổ hướng fails tại đây.
- **Chi phí:** ~0. part12 đã chứng minh tăng max-len 4608→8192 KHÔNG làm xấu TTFT (45ms, thậm chí tốt hơn
  part9's 48ms) hay TPOT (vẫn 4ms) — concurrency đỉnh ~5 nên KV cache dư dả ở cả 12288. Rủi ro startup
  KV-profiling dài hơn chút là có nhưng part12 đã cho thấy net dương, nhiều khả năng lặp lại.
- **Upside kỳ vọng:** nhỏ — chỉ ~0.7-1 điểm (5/420 request × ~0.63 điểm/request trung bình). Đây là phép
  thử "dọn nốt", không phải đòn bẩy lớn — đòn bẩy lớn (context-overflow) đã ăn hết ở part12.

## Cách đọc kết quả

| Kết cục | fails | Ý nghĩa | Bước tiếp |
|---|---|---|---|
| fails → 0-1 | overflow tiếp tục là nguyên nhân | +~1đ, giữ 12288, đóng sổ (đã sạch) | — |
| fails ~5 không đổi | floor thật (jitter/edge-case), không phải context | khóa sổ hướng fails vĩnh viễn | chuyển hẳn sang GPQA/f(Δ) |
| TTFT/TPOT xấu đi | 12288 bắt đầu chạm giới hạn KV cache/VRAM | rollback về 8192 (part12) | — |

## Song song (không tốn submit) — ưu tiên ngang hoặc cao hơn part13

**Chạy GPQA thật** cho config FP8 (part12/part13, giống nhau về accuracy vì chỉ đổi max-model-len — không
ảnh hưởng weights/tokenizer): `bash eval/bench-gpqa-diamond.sh`. Δ hiện mới chỉ đo qua arc_challenge proxy
(Δ≈0) — đây là rủi ro LỚN NHẤT còn lại cho `f(Δ)` ở vòng chọn ≤5 bài cuối, lớn hơn nhiều so với ~1đ upside
của part13. Nếu GPQA Δ > 0.10 → cần giữ `part1` (BF16, 43.82, Δ an toàn) làm phương án dự phòng.

## Fallback banked

**part12 (60.11, ATH)** là bài tốt nhất hiện tại — nếu part13 không cải thiện hoặc làm xấu đi, rollback
ngay về part12 (chỉ cần đổi lại `--max-model-len=8192` trong compose, không build lại).

## Cách nộp (command-only, KHÔNG build lại)

```
cp versions/part13/files/docker-compose.yml docker-compose.yml
# nộp docker-compose.yml lên Portal BTC (image sub-01 giữ nguyên)
```

Xác minh sau khi có điểm: `failed_count` (kỳ vọng ↓ từ 5), TTFT/TPOT không xấu đi so với part12 (45ms / 4ms).
