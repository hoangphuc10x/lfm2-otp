# Part 11 — `--enforce-eager`: diệt cold-start fail bằng giảm startup time

**Ngày:** 2026-07-22 · **Dựa trên:** part2 (banked, sync FP8) · **Đổi 1 biến:** thêm `--enforce-eager`
(và bỏ `--compilation-config` của part9 — đã chứng minh no-op). **Command-only, dùng lại image `sub-01`.**

## Bối cảnh (dữ liệu part9, chấm 2026-07-22 = 50.38)
- **TPOT vẫn 4ms** dù full-decode CUDA graph → đòn bẩy TPOT qua `cudagraph_mode` **CHẾT** (no-op). 4ms = floor thật.
- **75 fail / 420 (17.9%)** = drag lớn nhất còn lại. Grading MỚI chấm cả 420 (không miễn warmup) → request
  Poisson đến sớm rơi vào cửa sổ container **chưa-ready** → fail.
- TTFT 48ms đã xuất sắc (không phải ưu tiên).
- Toán ERS: diệt hết 75 fail (giữ TTFT48/TPOT4) → ERS ~0.63 = **~63đ (+13)**; giảm còn ~40 fail → ~57đ (+7).

## Vì sao `--enforce-eager` (không phải proxy, không async)
- **Proxy gate port 8000 bị CẤM** (R1.6 khóa entrypoint, R1.7 khóa `--port=8000`).
- **async / reduced-capture đã thử → không diệt fail:** part4-7 (async) 74-89 fail; part9 (sync, capture chỉ 5 sizes)
  vẫn 75 fail → số capture-size KHÔNG phải nguyên nhân. Nguyên nhân = **TỔNG startup time**.
- **Đòn bẩy hợp lệ duy nhất còn lại = giảm startup time.** Web search (2026-07-22) xác nhận:
  `--enforce-eager` bỏ CUDA graph capture (~11% startup), và eager cũng bỏ torch.compile (nguồn tốn nhất
  cho model nhỏ). Engine ready sớm hơn → cửa sổ chết ngắn hơn → **ít request fail hơn**.
- Bỏ full-graph = **miễn phí** vì part9 đã chứng minh nó không giúp TPOT.

## Giả thuyết (R6.1)
- **H:** fails là **startup-bound** (request đến trước khi engine ready). enforce-eager cắt compile+capture
  → ready sớm → fail 75 → ~30-45.
- **Kỳ vọng:** TTFT ~50-80ms (mất graph, có thể nhích), TPOT 4→~5ms (eager, nhích nhẹ), **fail ↓ mạnh**.
  Net: nếu fail 75→40 (+7đ) trội hơn phần TPOT/TTFT nhích → **tổng ~54-58đ**, có thể hơn.

## Rủi ro & rollback
| Kết cục | Đọc | Bước tiếp |
|---|---|---|
| **fail ↓ mạnh (→~30-45), điểm ↑** | fails LÀ startup-bound | giữ; part12 tinh chỉnh (thử `-O0` giữ piecewise-graph để cứu TPOT mà vẫn startup nhanh) |
| fail ~75 KHÔNG đổi | fails **structural** (BTC bắn từ t=0 bất kể ready) | **rollback part2**; KHÓA SỔ hướng fails; điểm bị cap ~50-55; chỉ còn tinh chỉnh biên |
| TPOT nhích mạnh (>6ms) nuốt hết lợi | eager quá đắt cho decode | part12 = `-O0` (giữ cudagraph piecewise decode, chỉ bỏ compile) thay vì enforce-eager |

## Fallback banked
part2 (sync FP8, 55.23 grading cũ / ~50 grading mới, ổn định) · part9 (sync+graph, 50.38, no-op).

## Cách nộp (command-only, KHÔNG build lại)
```
cp versions/part11/files/docker-compose.yml docker-compose.yml
# nộp docker-compose.yml lên Portal BTC (image sub-01 giữ nguyên)
```
Xác minh đã vào: startup log KHÔNG có dòng "Capturing CUDA graphs" / "torch.compile"; xem failed_count có giảm.
