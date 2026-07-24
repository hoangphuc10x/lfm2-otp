# Part 12 — Rollback part11 + max-model-len 8192 (phép thử miễn phí cuối cho fails)

**Ngày:** 2026-07-23 · **Dựa trên:** part2 (banked, sync FP8, DEFAULT piecewise graph) ·
**Đổi 1 biến:** `--max-model-len` 4608 → 8192. **Command-only, dùng lại image `sub-01`.**

## Vì sao (dữ liệu part9=50.38, part11=27.74)
- part11 (enforce-eager) = thảm họa: TPOT 4→10ms (s_tpot=0), fails 76 không đổi. → **rollback ngay** về
  default graphs (TPOT 4ms). Đây là điều kiện tiên quyết: phục hồi ~50 trước đã.
- Fails đã chứng minh **KHÔNG** giảm bằng async / eager / capture / scheduling / healthcheck.
  Còn đúng MỘT biến chưa ai đụng qua 11 part: **`--max-model-len`** (luôn = 4608).

## Giả thuyết (R6.1)
- **H:** một phần ~75 fails là request bị vLLM **REJECT (400 context length exceeded)** khi
  total context (multi-turn tích lũy, hoặc input "~4k" thực tế >4408) + output 200 **vượt 4608**.
  Điều này **trace-determined** → giải thích vì sao fails ~hằng số (74-89) bất kể config.
- **Cách đo:** 8192 dư sức chứa; nếu fails GIẢM → xác nhận context-overflow. Nếu KHÔNG đổi → xác nhận
  fails là cold-start cấu trúc thuần (đóng sổ hướng fails).
- **Chi phí:** ~0. VRAM 18GB / 1.2B FP8 + KV-FP8, concurrency đỉnh ~5 → KV cache thừa, không OOM,
  không giảm concurrency. Request ≤4608 chạy y hệt (không đổi latency).
- **Rủi ro nhỏ:** KV profiling lúc startup dài hơn chút → có thể +vài fail. Net dương nếu có overflow.

## Cách đọc kết quả
| Kết cục | fails | Ý nghĩa | Bước tiếp |
|---|---|---|---|
| **fails ↓ rõ** (vd 75→~40) | context-overflow LÀ 1 phần fails | **+điểm** | giữ 8192; xem còn overflow không, cân nhắc 12288 |
| fails ~75 không đổi | fails = cold-start CẤU TRÚC thuần | trần ~51 xác nhận | **đóng sổ hướng fails**; chuyển sang bảo vệ f(Δ) + chọn 5 bài |
| điểm ~50, TPOT 4ms | rollback part11 thành công (mốc phục hồi) | — | — |

## Chiến lược sau part12 (nếu fails không giảm → ta ở trần)
1. **Bảo vệ f(Δ):** FP8 mới đo arc_challenge (Δ≈0), CHƯA đo GPQA. Nếu GPQA Δ>0.10 → phạt điểm.
   Chạy `eval/bench-gpqa-diamond.sh` cho part2/part12. Nếu Δ rủi ro → giữ part1 (BF16, 43.82, Δ an toàn) làm bài dự phòng.
2. **Chọn 5 bài cuối:** part12/part9 (~50, FP8) + part1 (~44, BF16 an toàn) → BTC chạy GPQA chọn cái tối ưu Score=100·ERS·f(Δ).
3. **Long-shot còn lại (rủi ro/nặng, chỉ nếu muốn):**
   - `--num-scheduler-steps>1` (nếu v0.22.1 còn hỗ trợ) — amortize CPU launch overhead 3-CPU → có thể TPOT<4ms. Rủi ro TTFT.
   - Bake **pre-quantized FP8 offline** (bỏ `--quantization=fp8` online) — cần rebuild + quant offline (không GPU = khó). Có thể rút ngắn startup (load FP8 nhỏ hơn) → thử lại giả thuyết fails-startup-bound ở khía cạnh online-quant mà eager chưa loại.

## Fallback banked
part9 (sync + graph, 50.38) ≈ part2 (default). part1 (BF16, 43.82, Δ an toàn nhất).

## Cách nộp (command-only, KHÔNG build lại)
```
cp versions/part12/files/docker-compose.yml docker-compose.yml
# nộp docker-compose.yml lên Portal BTC (image sub-01 giữ nguyên)
```
Xác minh đã vào: TPOT về lại ~4ms (KHÔNG 10ms); xem failed_count.
