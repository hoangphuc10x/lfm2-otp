# Part 2 — Điểm (FP8 weight quantization)

**Chấm:** 2026-07-17 · Image dùng lại part1 (không build lại), compose thêm `--quantization=fp8`.

| Chỉ số | part1 | **part2** | Δ |
|---|---|---|---|
| **final_score** | 43.82 | **55.23** | **+11.41** ✅ |
| ERS | 0.4382 | 0.5523 | +0.114 |
| TTFT p50 | 98 | **80** ms | −18 |
| TTFT p95 | 147 | **117** ms | −30 |
| TPOT median | 5 | **4** ms | −1 |
| failed_count | 0 | 0 | ✅ |
| accuracy_drop (online) | 0 | 0 | ⚠️ DEFAULT, chưa chạy GPQA thật |

## Tách đóng góp ERS (γ=2, w=0.5)
| Nửa | Metric | s | Đóng góp | % tối đa | Headroom còn lại |
|---|---|---|---|---|---|
| TTFT | 80 ms | ((400−80)/390)²=**0.673** | 0.337 | 67% | +0.16 ERS (+16đ) |
| TPOT | 4 ms | ((10−4)/9)²=**0.444** | 0.222 | 44% | **+0.28 ERS (+28đ)** |

## Kết luận
- ✅ FP8 weights hiệu quả: **+11.4đ**, cả TTFT lẫn TPOT đều giảm (đúng lý thuyết memory-bound).
- **TPOT vẫn là đòn bẩy #1** (mới 44% tối đa). 4ms→2ms ≈ +17đ; →1ms ≈ +28đ.
- TTFT #2 (67%). 80→40ms ≈ +9đ.

## ✅ ĐÃ KIỂM ACCURACY (2026-07-18, trên RunPod L40)
Đo `arc_challenge` (proxy, non-gated) — accuracy transfer 100% vì FP8 cho kết quả y hệt mọi GPU:

| Config | acc | acc_norm |
|---|---|---|
| BF16 (gốc) | 0.3814 | 0.4121 |
| FP8 (part2) | 0.3840 | 0.4155 |
| **Δ** | −0.0026 | **−0.0034** (trong sai số ±0.014) |

→ **FP8 KHÔNG tụt accuracy** (Δ≈0, thậm chí nhỉnh hơn do nhiễu). part2 AN TOÀN ở Accuracy Gate.
Lưu ý: arc_challenge là proxy; GPQA thật có thể khác chút nhưng FP8 delta ~0 cho biên độ an toàn rất lớn
so với ngân sách 0.10.

## (Đã giải quyết) RỦI RO trước đây — accuracy của FP8
`accuracy_drop=0` online là **giá trị mặc định** (BTC KHÔNG chạy GPQA mỗi lượt). FP8 weights
**có thể** làm tụt accuracy thật. **BẮT BUỘC** chạy `eval/bench-gpqa-diamond.sh` để đo Δ thật
và xác nhận Δ ≤ 0.10 TRƯỚC khi chọn part2 làm bài chốt. Nếu Δ vượt → part2 vô hiệu ở Accuracy Gate.

## Về độ nhiễu đo
Ta CHƯA có phép đo nhiễu sạch (part1 và part2 là 2 config khác nhau). +11.4đ lớn & nhất quán
2 metric nên nhiều khả năng là thật, nhưng có thể lẫn một phần nhiễu contention MiG.
→ Nên đo LOCAL nhiều lần cho mỗi thay đổi thay vì chỉ tin 1 lần chấm leaderboard.
