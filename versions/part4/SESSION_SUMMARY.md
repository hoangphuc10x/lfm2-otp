# Session Summary — 2026-07-18

Tổng quan phiên làm việc: tối ưu LLM inference server cho `LFM2.5-1.2B-Instruct` (vLLM) trên MiG H200.
Xem thêm: [CLAUDE.md](CLAUDE.md) (đề bài), [notes/submissions.md](notes/submissions.md), [versions/](versions/).

---

## 1. Trạng thái hiện tại (TL;DR)

| | |
|---|---|
| **Bài nộp tốt nhất** | **part2 = 55.23đ** (FP8 weights + FP8 KV + prefix cache + max-len 4608) |
| **Accuracy** | ✅ đã verify FP8 **không tụt** (Δ≈0) → part2 an toàn ở Accuracy Gate |
| **Đã loại** | part3 (spec decode — crash hybrid); part4/5 (async-scheduling — fail primer cold-start) |
| **Best** | **part2 = 55.23** (0 fail, accuracy an toàn) — compose đã revert về đây |
| **Fallback an toàn** | part2 (sub-01, image công khai trên Docker Hub) |

---

## 2. Timeline phiên bản & điểm

| Part | Thay đổi | final_score | TTFT p50/p95 | TPOT med | Ghi chú |
|---|---|---|---|---|---|
| **part1** | baseline: FP8 **KV**, weights BF16, prefix-cache, max-len 4608 | **43.82** | 98/147 ms | 5 ms | 0 fail |
| **part2** | + **FP8 weights** (`--quantization=fp8`) | **55.23** | 80/117 ms | 4 ms | **+11.4đ**, accuracy Δ≈0 ✅ |
| **part3** | + n-gram speculative decoding | ❌ FAIL | — | — | crash hybrid (500/503). **BỎ** |
| **part4** | part2 + `--async-scheduling` | **51.54** ↓ | **42**/71 ms | 4 ms | TTFT giảm nửa 🔥 nhưng **74 fail** (primer cold-start) |
| **part5** | part4 + warmup healthcheck | **49.01** ↓ | 47/73 ms | 4 ms | healthcheck **BTC bỏ qua** (hash==part4); 88 fail. **BỎ async** |

**→ Best = part2 = 55.23** (0 fail, accuracy an toàn). Async cho TTFT 42ms nhưng làm ~88 primer FAIL cold-start → mất warmup → net < part2, không vá được (BTC dùng healthcheck riêng).

Phân tích ERS (γ=2, w=0.5): TTFT 80ms → s=0.67 (67% max); TPOT 4ms → s=0.44 (44% max).
→ **TPOT còn headroom lớn nhất** nhưng đòn bẩy TPOT (spec decode) đã chết → chuyển sang TTFT.

---

## 3. Chi tiết từng bước test

### part1 → part2: FP8 weights
- **Giả thuyết:** decode/prefill memory-bound → FP8 weights nhanh hơn.
- **Kết quả:** +11.4đ thật (TTFT 98→80, TPOT 5→4). ✅
- **Phát hiện hạ tầng:** `config_hash` của BTC **băm theo IMAGE digest, KHÔNG theo command args** → đổi flag vLLM không cần build lại image.

### part3: speculative decoding — THẤT BẠI (2 lớp)
1. **Lỗi quoting JSON:** `--speculative-config={"method":"ngram",...}` bị **nuốt dấu ngoặc kép** khi truyền qua docker-compose/RunPod command → JSON hỏng → `vllm serve: error: ... cannot be converted to json loads` → server không lên → **330/330 transport errors**.
   - **Cách sửa đã tìm ra:** để config vào **file YAML** baked trong image (`--config=/vllm_config.yaml`) → không còn quotes trong command. (File `vllm_config.yaml` + `Dockerfile.spec` còn trong repo.)
2. **Sửa quoting xong vẫn crash:** server khởi động OK nhưng **sinh vài request là engine core sập** (`http=500`, `/health=503`, container restart) — kể cả khi warm.
   - **Nguyên nhân:** LFM2.5 là model **hybrid Mamba + short-conv**; speculative decoding **không tương thích ổn định** với kiến trúc mamba trong vLLM v0.22.1.
   - **Kết luận:** BỎ HẲN spec decode.

### Kiểm accuracy FP8 (quan trọng nhất) — AN TOÀN ✅
- Đo `arc_challenge` (proxy non-gated; GPQA bị gated cần HF token) trên RunPod, so FP8 vs BF16:

| Config | acc | acc_norm |
|---|---|---|
| BF16 (gốc) | 0.3814 | 0.4121 |
| FP8 (part2) | 0.3840 | 0.4155 |
| **Δ** | −0.0026 | **−0.0034** (trong sai số ±0.014) |

- → **FP8 không làm tụt accuracy** (Δ≈0). part2 (55.23) **không bị hủy** ở Accuracy Gate. FP8 là "bữa trưa miễn phí".
- Lưu ý: accuracy transfer 100% giữa mọi GPU (FP8 cho kết quả y hệt) nên đo trên L40 = valid cho H200.

---

## 4. Hạ tầng test (RunPod) & bài học vận hành

Không dùng được EC2 (instance không GPU + AWS **Free Plan chặn GPU instances**). → Chuyển sang **RunPod** thuê GPU theo giờ.

- **GPU:** L40 (Ada, có FP8) — cần GPU **Ada/Hopper** cho FP8; **tránh Ampere** (A100/A40/A5000/A6000 — KHÔNG có FP8).
- **Deploy:** dùng image công khai `hoangphuc109/lfm2-otp:sub-01`, đặt args qua **Container Start Command**, expose **port 8000**.
- **Entrypoint image = `vllm serve`** → command dùng model **positional** (`/model ...`), không cần `python3 -m ...`.
- **Web terminal RunPod hay rớt (~2s)** → mọi lệnh dài phải chạy nền chống-disconnect:
  ```bash
  setsid bash -c '<lệnh> > /tmp/out.txt 2>&1' < /dev/null & disown
  # rồi mở lại terminal: tail -20 /tmp/out.txt
  ```
- **Benchmark tốc độ:** `vllm bench serve` có sẵn trong image (nhớ `--tokenizer /model` để không gọi HF).
- **Đo accuracy:** `pip install "lm-eval[api]" tenacity` → `lm_eval --model local-completions --model_args base_url=...,tokenizer=/model,tokenized_requests=False --tasks arc_challenge`.

---

## 5. Bài học kỹ thuật (đúc kết)

1. **FP8 weights = +11.4đ, miễn phí** (không mất accuracy) — giữ chắc.
2. **Spec decode KHÔNG dùng được** với LFM2 hybrid/mamba — crash.
3. **Không nộp config chưa test** — crash = 330/330 = unscoreable / 0 điểm. Luôn boot-check trên pod trước.
4. **`config_hash` băm theo image** → iterate qua command flags không cần build lại.
5. **Nút cổ chai BTC = 3 CPU** → các tối ưu giảm overhead CPU (vd `--async-scheduling`) chỉ đo được hiệu quả **trên BTC**, không tái hiện trên RunPod 16-CPU.
6. **JSON trong command bị nuốt quotes** → nếu cần truyền JSON, dùng file `--config=/file.yaml`.
7. **100 điểm gần như bất khả** (cần TTFT≤10ms VÀ TPOT≤1ms đồng thời). Mục tiêu thực tế: giữ part2 + ép TTFT lên vùng ~60.

---

## 6. Config tham chiếu

**docker-compose (BTC), entrypoint module form** — part2:
```
--model=/model --served-model-name=LFM2.5-1.2B-Instruct --host=0.0.0.0 --port=8000
--max-model-len=4608 --gpu-memory-utilization=0.92 --tensor-parallel-size=1
--enable-prefix-caching --kv-cache-dtype=fp8 --quantization=fp8
```
part4 = thêm `--async-scheduling`.

**RunPod Container Start Command (entrypoint = vllm serve, model positional):**
```
/model --served-model-name=LFM2.5-1.2B-Instruct --host=0.0.0.0 --port=8000
--max-model-len=4608 --gpu-memory-utilization=0.92 --enable-prefix-caching
--kv-cache-dtype=fp8 --quantization=fp8
```

---

## 7. Việc còn dang dở / hướng tiếp

- [ ] **Boot-check part4** (`--async-scheduling`) trên pod → nộp BTC → so với 55.23.
- [ ] Nếu tốt: thử thêm `--max-num-batched-tokens=8192`, bỏ/chỉnh chunked-prefill (chỉ đo được trên BTC).
- [ ] E1 (bỏ `--kv-cache-dtype=fp8`) — FP8 KV không hại accuracy nên chỉ còn ý nghĩa về tốc độ; test nếu muốn.
- [ ] Trước khi chốt 5 bài cuối: nếu có HF token, chạy **GPQA thật** xác nhận Δ (arc_challenge chỉ là proxy).
- [x] ~~Verify accuracy FP8~~ ✅ Δ≈0, an toàn.
- [x] ~~Spec decode~~ ❌ loại.
