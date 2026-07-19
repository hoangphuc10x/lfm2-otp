# Part 6 — Điểm (async + max-num-seqs=64) — LÀM HẠI

**Chấm:** 2026-07-19 · **config_hash:** `603c84...` (GIỐNG part4/5 → hash theo IMAGE, không theo command)

| Chỉ số | part4 (async) | part5 | **part6** |
|---|---|---|---|
| final_score | 51.54 | 49.01 | **47.58** ↓ |
| TTFT p50 | 42 | 47 | **54** ↑ (hại) |
| TTFT p95 | 71 | 73 | 87 |
| failed_count | 74 | 88 | 88 |
| TPOT median | 4 | 4 | 4 |

## Kết luận
1. **`--max-num-seqs=64` gây HẠI:** TTFT 42→54ms (queueing), fail KHÔNG giảm.
   → **Fail KHÔNG do quá tải 3-CPU. Fail là COLD-START.** Concurrency workload vốn thấp → cap seqs chỉ hại.
2. **part4 (async trần) = 51.54 = best.** part5 (healthcheck) và part6 (max-seqs) đều tệ hơn.
3. **`config_hash` = IMAGE digest**, không theo command. Command vẫn áp dụng (async chạy) nhưng hash không phản ánh.

## ⚠️ Xu hướng giảm dần
51.54 → 49.01 → 47.58 suốt ~24h trên config gần như nhau → nghi **contention hạ tầng BTC tăng** (gần deadline)
→ mọi config bị hạ điểm, so sánh giữa các lần nộp gần đây kém tin cậy.

## Quyết định
- Revert **part4 (async trần, 51.54)** — best.
- Fail = cold-start, KHÔNG fix được bằng command (max-seqs, healthcheck đều thất bại).
- Fix cold-start thật cần precompile tầng image — nhưng compile cache **GPU-specific (H200)**, không tái dùng từ L40 → bế tắc nếu không có H200.
