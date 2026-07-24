# Submissions log

Bảng theo dõi từng bài nộp. Cần khi chọn ≤ 5 bài cuối cho GPQA (RULES.md R4.6).

| Tag | Ngày | Cấu hình chính | ERS local | **final_score** | Δ | TTFT p50/p95 | TPOT med | Ghi chú |
|-----|------|----------------|-----------|-----------------|---|--------------|----------|---------|
| part1 | 2026-07-17 | prefix-cache + **kv**-fp8 + max-len 4608 (weights BF16) | — | **43.82** | 0* | 98/147 ms | 5 ms | 0 fail. baseline |
| part2 | 2026-07-17 | + `--quantization=fp8` (FP8 weights) | — | **55.23** | 0* | 80/117 ms | 4 ms | **+11.4đ**. Δ thật CHƯA đo (GPQA) |
| part3 | 2026-07-18 | + speculative decoding (n-gram) | — | ❌ **FAIL** | — | — | — | 330/330 transport errors, server crash. Rollback về part2 |
| part4 | 2026-07-18 | + `--async-scheduling` (sync→async) | — | **51.54** | 0* | **42**/71 ms | 4 ms | TTFT 🔥 nhưng **74 fail** cold-start. banked |
| part5 | 2026-07-19 | async + warmup-healthcheck | — | 49.01 | 0* | 47/73 ms | 4 ms | ❌ BTC bỏ qua healthcheck compose. 88 fail |
| part6 | 2026-07-19 | async + `--max-num-seqs=64` | — | 47.58 | 0* | 54/87 ms | 4 ms | ❌ queueing, fail không giảm (fail = cold-start) |
| part7 | 2026-07-19 | async + `--max-num-batched-tokens=8192` | — | 46.27 → **48.37** (re-grade 2026-07-21) | 0* | 42→44/80 ms | 4 ms | ↓ do contention; **89 fail** cold-start. hash 603c84 |
| part8 | 2026-07-19 | revert part2 (sync) — đo dưới contention | — | _CHƯA nộp_ | 0* | — | — | so sync vs async cùng điều kiện (sync còn 0-fail dưới grading mới?) |
| **part9** | 2026-07-22 | part2 + **full-decode CUDA graph** (cudagraph_mode=FULL_AND_PIECEWISE, capture_sizes[1..16]) | — | **50.38** | 0 | **48**/75 ms | **4 ms** | ⚠️ full-graph = **NO-OP trên TPOT** (vẫn 4ms). **75 fail** dưới grading mới. Hash 603c84 (image-only, không phân biệt được part). Bỏ compilation-config |
| **part10** | 2026-07-21 | part9 + `--async-scheduling` | — | **BỎ / hạ ưu tiên** | — | — | — | ❌ part9 (sync, capture 5 sizes) vẫn 75 fail → reduced-capture KHÔNG diệt fail → giả thuyết part10 bị bác. async nhiều fail hơn sync. Bỏ trừ khi part11 chứng minh fails startup-bound |
| **part11** | 2026-07-22 | part2 + `--enforce-eager` (bỏ graph) | — | **27.74** ⬇️ | 0 | 74/120 ms | **10 ms** | ❌ **THẤT BẠI KÉP.** TPOT 4→10ms (s_tpot=0, bỏ graph = chết). fails 76 KHÔNG đổi → **fails NOT startup-bound → cấu trúc**. Không bao giờ dùng enforce-eager |
| **part12** | 2026-07-23 | part2 + `--max-model-len` 4608→**8192** (rollback part11) | — | **60.11** 🏆 ATH | 0 | **45**/80 ms | **4 ms** | ✅✅ **failed_count 75→5!** Giả thuyết context-overflow ĐÚNG. +9.73đ vs part9. TPOT phục hồi 4ms. Dùng lại sub-01, command-only |
| **part13** | 2026-07-24 | part12 + `--max-model-len` 8192→**12288** | — | **CHƯA nộp** | 0* | kỳ vọng ~45 ms | kỳ vọng 4 ms | 🎯 Kiểm nốt 5 fail còn lại: overflow tiếp hay floor thật (~5 = jitter/cold-start irreducible)? Dùng lại sub-01, command-only |

> **2026-07-23 — part12 ĐÃ CÓ ĐIỂM = 60.11 — ALL-TIME HIGH kể từ khi BTC đổi cách chấm (2026-07-19).**
> **SỬA LẠI kết luận part11 ("fails = structural cold-start"): SAI.** part11 chỉ đổi startup-time
> (enforce-eager) nhưng GIỮ NGUYÊN `--max-model-len=4608` → dĩ nhiên fails không đổi (76). Biến thật sự
> gây fail là **context length**, không phải cold-start timing. part12 đổi đúng biến còn lại (8192) →
> **fails 75→5 (-93%)**. Bài học: đổi *đúng* biến quan trọng hơn tốc độ startup. Xem `versions/part12/score.md`.
> Trần điểm cũ "~51" trong memory/part11 SUMMARY đã lỗi thời — trần mới ước tính **~63-64đ** (TPOT floor
> 4ms vẫn là số hạng thua thiệt lớn nhất, s_tpot≈0.44 vs s_ttft≈0.83, nhưng đã xác nhận floor qua 3 lần đo).

> **2026-07-22 — part9 ĐÃ CÓ ĐIỂM = 50.38.** TPOT vẫn 4ms → full-decode CUDA graph **NO-OP** (đòn bẩy TPOT ở config level = chết). 75 fail dưới grading mới. `config_hash=603c84` băm theo IMAGE nên KHÔNG phân biệt được part (mọi biến thể sub-01 đều 603c84) — phân biệt bằng TTFT + failed_count, không phải hash.
>
> **BÀI HỌC LỚN về cold-start fail (2026-07-22):** part9 = sync + `cudagraph_capture_sizes` chỉ **5 sizes** mà VẪN **75 fail** → **số capture-size KHÔNG phải nguyên nhân fail** → giả thuyết part10 (capture nhanh → hết fail) bị **BÁC**. Fail đến từ **TỔNG startup time** (weight load + torch.compile + capture), không riêng số size. → Đòn bẩy hợp lệ đúng = **giảm TỔNG startup** (`--enforce-eager` bỏ compile+capture) = **part11**. Proxy gate port vẫn CẤM (R1.6/R1.7). part11 sẽ phân định fails là startup-bound hay structural.

### ⚠️ BTC ĐỔI CÁCH CHẤM (2026-07-19)
Giờ chấm **cả 420 request, KHÔNG miễn 90 warmup** → cold-start tính cho mọi config. Điểm cũ bị hạ:
- **part4 (async) = 51.54 → CAO NHẤT hiện tại.** part2 tụt còn ~50.
- Chiến lược mới: **cold-start giờ quan trọng.** async có TTFT tốt nhất (42ms) nhưng ~74 fail cold-start.
  → Diệt fail này mà giữ TTFT 42ms → **~64đ**. Đây là ROI cao nhất.
- Nghi phạm fail: **cold-start compile chậm trên 3-CPU của BTC → primer timeout** (async làm lộ rõ hơn sync).

*Δ online = default, chưa chạy GPQA. `config_hash` băm theo image+command (không theo healthcheck).

**Accuracy FP8 đã kiểm (2026-07-18, arc_challenge proxy):** BF16 acc_norm=0.4121 vs FP8=0.4155 → **Δ≈0, FP8 không tụt accuracy**. part2 an toàn ở Accuracy Gate. Spec decode (part3) đã loại (crash hybrid).

## Nhật ký thử nghiệm (điền dần)

### sub-01
- **Config:** `--enable-prefix-caching --kv-cache-dtype=fp8 --max-model-len=4608 --gpu-memory-utilization=0.92`
- **Giả thuyết:** prefix caching giảm TTFT (multi-turn); KV FP8 tăng concurrency; giảm max-len tiết kiệm KV cache.
- **ERS local:** _(chạy `run_bench.py` rồi điền)_
- **Δ accuracy:** _(chạy `eval/bench-gpqa-diamond.sh` rồi điền — mục tiêu Δ ≤ 0.10)_
- **Quan sát / bước tiếp theo:**
