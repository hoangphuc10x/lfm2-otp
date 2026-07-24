# Part 9 — Điểm (full-decode CUDA graph, tấn công TPOT)

**Config:** part2 (sync FP8, prefix-cache, kv-fp8, max-len 4608) **+** `cudagraph_mode=FULL_AND_PIECEWISE`,
`cudagraph_capture_sizes=[1,2,4,8,16]`. Dùng lại image `sub-01` (chỉ đổi command).

## KẾT QUẢ (chấm 2026-07-22) — final_score **50.38**

| Chỉ số | part2 (nền, grading CŨ) | **part9 (grading MỚI)** |
|---|---|---|
| final_score / ers | 55.23 | **50.38** |
| f_delta / penalty | 1 / 1 | 1 / 1 |
| **TPOT (tbt) median** | 4 ms | **4 ms** ← KHÔNG ĐỔI |
| TTFT p50 / p95 | 80 / 117 ms | **48 / 75 ms** |
| **failed_count** | 0 (warmup được miễn) | **75** / 420 |
| accuracy_drop | 0* | 0 |
| config_hash | (sub-01) | sha256:603c84… (sub-01, image-only) |

> ⚠️ Nhận diện: `config_hash` băm theo IMAGE → mọi biến thể command của sub-01 đều ra 603c84,
> KHÔNG phân biệt được part9 vs part2. Working-tree compose lúc nộp = part9 (có `--compilation-config`,
> KHÔNG có `--async-scheduling`) → đọc là part9. Kết luận dưới đây đúng cho CẢ HAI cách đọc.

## Nhận xét — nhánh "NO-OP" (theo bảng "Cách đọc kết quả" trong SUMMARY.md)

1. **TPOT vẫn 4ms** → full-decode CUDA graph **KHÔNG hạ TPOT**. LFM2 hoặc đã graph decode sẵn, hoặc
   4ms là floor thật (bandwidth / launch-overhead host 3-CPU). → **Đòn bẩy TPOT qua `cudagraph_mode` = CHẾT.**
2. **75 fail (17.9%)** = drag lớn nhất còn lại. Grading MỚI chấm cả 420, không miễn warmup → request
   Poisson đến sớm rơi vào cửa sổ container chưa-ready → fail. Diệt được → **+7…+13đ**.
3. **TTFT 48ms xuất sắc** (full-graph chỉ ảnh hưởng decode → 48ms do grading/contention, không phải flag).

**→ Pivot part11:** đòn bẩy lớn còn lại DUY NHẤT = 75 cold-start fail. Proxy cấm (R1.6/R1.7)
→ tấn công bằng **giảm startup time** (`--enforce-eager`) → engine ready sớm → ít fail.
