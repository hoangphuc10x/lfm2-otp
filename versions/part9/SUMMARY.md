# Part 9 — full-decode CUDA graph (tấn công TPOT, đòn bẩy #1)

**Ngày:** 2026-07-20 · **Dựa trên:** part2 (sync, FP8, **0 fail**, 55.23 banked) · **Trạng thái:** chờ nộp.
**Đổi 1 biến duy nhất** so với part2 (R2.1). **Không build lại image** (config_hash băm theo IMAGE, command vẫn áp dụng) → dùng lại tag `sub-01`, chỉ đổi command trong compose.

## Thay đổi so với part2 (1 biến)
Thêm:
```
--compilation-config={"cudagraph_mode":"FULL_AND_PIECEWISE","cudagraph_capture_sizes":[1,2,4,8,16]}
```
- `cudagraph_mode=FULL_AND_PIECEWISE` → **full CUDA graph cho decode** (piecewise cho prefill/mixed).
- `cudagraph_capture_sizes=[1,2,4,8,16]` → **cap size nhỏ** (peak concurrency trace ~5) để **né crash Mamba**
  (`assert num_cache_lines >= batch` trong `causal_conv1d_update` khi FULL-decode batch > số Mamba cache block —
  vLLM PR #34571, merged 2026-03-04). Cap thủ công là workaround kể cả khi v0.22.1 chưa có fix đó.

## Giả thuyết (R6.1)
- **Nền tảng:** TPOT hiện = 4ms = **250 tok/s** — CHẬM cho 1.2B FP8 (trần băng thông MiG ước ~580 tok/s).
  ~2x headroom bị **CPU/kernel-launch overhead** ăn (host 3-CPU).
- **Cơ chế:** LFM2.5 là **hybrid Mamba+attention**. vLLM nhiều khả năng **tự hạ xuống PIECEWISE**
  (attention + Mamba chạy eager trên decode path) để tránh crash → decode KHÔNG được graph hóa
  → per-layer launch overhead cao → TPOT kẹt 4ms.
- **Kỳ vọng:** ép full-decode graph (với size cap né crash) → cắt launch overhead → **TPOT 4→~2ms**
  → s_tpot 0.44→0.79 → **ERS +~0.17 → +~17đ** (55→~72), giữ **0 fail** (không đụng async).
- TTFT gần như không đổi (prefill vẫn piecewise).

## Rủi ro & rollback
- ⚠️ **Rủi ro crash lúc load/generate** (giống spec decode part3) nếu full-decode graph vẫn xung khắc hybrid
  dù đã cap size → server 500/503 → unscoreable. **Rollback = part2 (55.23) đã banked.**
- ⚠️ **Có thể là no-op** nếu v0.22.1 vốn ĐÃ dùng FULL_AND_PIECEWISE cho LFM2 (default). Trường hợp đó:
  điểm ≈ part2 (~55) → KẾT LUẬN: TPOT 4ms là floor thật của model/hạ tầng, không phải overhead
  → chuyển đòn bẩy sang TTFT (part10: warmup-proxy async).
- Cả hai kết cục đều **thông tin có giá trị** (blind-submit, còn nhiều lượt, khẩu vị rủi ro OK).

## Cách đọc kết quả
| Kết cục | TPOT | fail | Ý nghĩa | Bước tiếp |
|---|---|---|---|---|
| **THẮNG** | 4→~2ms | 0 | full-decode graph hiệu quả | giữ; part10 = + warmup-proxy async (ăn TTFT) |
| No-op | ~4ms | 0 | LFM2 vốn đã full | TPOT là floor → dồn lực TTFT |
| Crash | — | 330/330 | hybrid vẫn xung khắc full graph | rollback part2; TPOT bế tắc ở config level |

## Lưu ý quoting (bài học part3)
Trong docker-compose, viết flag thành **1 scalar YAML có single-quote** để JSON không bị YAML/shell cắt:
```yaml
- '--compilation-config={"cudagraph_mode":"FULL_AND_PIECEWISE","cudagraph_capture_sizes":[1,2,4,8,16]}'
```

## Fallback banked
part2 (sync FP8, 55.23, 0 fail) · part4 (async, 51.54, 42ms TTFT nhưng 74 fail).
