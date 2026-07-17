# Part 1 — Điểm

**Chấm:** 2026-07-17 · **config_hash:** `sha256:a84041...820ff55c`

| Chỉ số | Giá trị |
|---|---|
| **final_score** | **43.82** |
| ERS | 0.4382 |
| f_delta / accuracy_drop | 1.0 / 0 (⚠️ đây là DEFAULT online, GPQA chưa chạy) |
| total_count | 330 |
| **failed_count** | **0** ✅ |
| warmup_count | 90 |
| TTFT p50 / p95 | 98 / 147 ms |
| TPOT median | 5 ms/token |

**Config:** FP8 **KV cache**, weights **BF16**, prefix-cache, max-len 4608.

> 📌 BÀI HỌC HẠ TẦNG: `config_hash` của BTC **chỉ băm theo IMAGE digest, KHÔNG theo command args**.
> → Đổi flag vLLM (quantization, max-len, scheduling…) **không làm đổi hash** và **không cần build lại image**.
> Rất tiện để iterate nhanh. Nhưng cũng nghĩa là hash KHÔNG dùng để phân biệt các biến thể command của mình.

## Phân tích (tách đóng góp ERS, γ=2, w=0.5)

| Nửa điểm | Metric | s = clamp((C−x)/(C−F))² | Đóng góp (×0.5) | % tối đa | Headroom |
|---|---|---|---|---|---|
| TTFT | 98 ms | ((400−98)/390)² = **0.60** | 0.300 | 60% | +0.20 ERS (+20đ) |
| TPOT | 5 ms | ((10−5)/9)² = **0.31** | 0.154 | 31% | **+0.35 ERS (+35đ)** |

**Kết luận:**
- Độ ổn định hoàn hảo (0 fail, Δ=0) → còn **nguyên ngân sách accuracy 0.10** để đánh đổi lấy tốc độ.
- **TPOT là đòn bẩy #1** (mới 31% tối đa). 5ms→2ms sẽ +~24đ; 5ms→1ms +~35đ.
- **TTFT là đòn bẩy #2**. 98ms→50ms +~10đ; →20ms +~17đ.
- Điểm mấu chốt: **weights vẫn đang BF16** (part1 chỉ quantize KV cache). Chưa dùng FP8 weights → còn dư địa lớn cho cả TPOT lẫn TTFT vì decode/prefill của model nhỏ là memory-bandwidth-bound.

## Về mục tiêu 100 điểm (thành thật)
ERS=1.0 đòi hỏi **đồng thời** TTFT ≤ 10ms **và** TPOT ≤ 1ms (1000 tok/s). Đây là sát sàn vật lý —
rất khó tuyệt đối. Lộ trình thực tế: đẩy từng nửa về gần floor. Cột mốc hợp lý kế tiếp:
TPOT ~2ms + TTFT ~40-50ms → ERS ~0.7 (≈70đ). Sau đó mới tối ưu sâu để tiến gần 100.
