# Part 10 — async + full-graph reduced-capture (diệt cold-start fail + giữ TTFT + TPOT)

**Ngày:** 2026-07-21 · **Dựa trên:** part9 (sync + full CUDA graph) · **Đổi 1 biến:** thêm `--async-scheduling`.
**Không build lại image** (command-only, dùng lại `sub-01`).

## Bối cảnh (vì sao đổi hướng)
Web search 2026-07-21 làm rõ cơ chế 89 fail của async:
- vLLM `/health` trả **200 khi engine process còn sống, KHÔNG đợi CUDA graph capture xong**
  (vllm issues #6073, #36960). Capture mặc định ~67 batch sizes → **~54s**.
- Nếu BTC probe `/health` → pass sớm → bắn ~90 primer request → engine **chưa ready** → **fail**.
- ⚠️ Đồng thời: `--async-scheduling` bị ghi nhận **crash/bất ổn dưới tải** (vllm #29379, #31679, #25777).
  → fail của async có thể còn do instability, không chỉ cold-start.

## Ý tưởng part10 (hợp lệ, chỉ đổi command — KHÔNG proxy/không đụng entrypoint R1.6/R1.7)
Warmup-proxy nguyên gốc **BỎ** (vướng R1.6 entrypoint khóa + R1.7 --port=8000). Thay bằng đòn bẩy command:
- **`cudagraph_capture_sizes=[1,2,4,8,16]`** (5 sizes thay vì ~67) → capture nhanh hơn nhiều
  → engine **sẵn sàng sớm** → **thu hẹp cửa sổ "/health=200 nhưng chưa ready"** → **giảm cold-start fail**.
- **`cudagraph_mode=FULL_AND_PIECEWISE`** → full graph cho decode → **TPOT 4→~2ms**.
- **`--async-scheduling`** → **TTFT ~44ms**.

## Giả thuyết (R6.1)
Nếu fail là cold-start (capture chậm) → reduced-capture diệt phần lớn → async **44ms TTFT + ~0 fail + TPOT ~2ms**:
- s_ttft((400-44)/390)²=0.833, s_tpot((10-2)/9)²=0.790 → **ERS ~0.81 = ~81đ** (đích mơ ước).
- Ngay cả TPOT vẫn 4ms mà 0 fail: ERS 0.643 = **~64đ**.

## ⚠️ Rủi ro & rollback
- async có thể **crash dưới tải** (instability, không phải cold-start) → reduced-capture KHÔNG cứu được → fail vẫn ~90.
- full graph có thể xung khắc hybrid → 330/330 transport.
- **Rollback:** part9 (sync+graph, kỳ vọng 0 fail) hoặc part2 (55.23 banked).

## THỨ TỰ NỘP (quan trọng — kỷ luật 1 biến R2.1)
**Nộp part9 TRƯỚC, part10 SAU.** Lý do: part9 (sync+graph) tách bạch:
- (U1) full graph có hạ TPOT không? (U2) sync có 0-fail dưới grading hiện tại không?
part10 = part9 + async → so với part9 biết async đóng góp gì (TTFT↓, fail thay đổi ra sao).
Nếu nộp thẳng part10 → lẫn 2 biến (async + graph), khó quy trách.

| Nộp | Thấy gì | Kết luận |
|---|---|---|
| part9 | TTFT~80, TPOT<4, 0 fail | full graph OK + sync an toàn → bankable ~73 |
| part10 | TTFT~44, **fail giảm mạnh** | reduced-capture diệt cold-start → **~64-81đ, config chốt** |
| part10 | TTFT~44, **fail vẫn ~90** | async là INSTABILITY, không cứu bằng flag → **bỏ async**, giữ part9 |
| part10 | 330/330 | crash → rollback part9 |

## Cách nộp part10 (sau part9)
`cp versions/part10/files/docker-compose.yml docker-compose.yml` → nộp Portal (không build lại).
Xác minh đã vào: TTFT p50 ≈ 44ms (async) + xem failed_count.
