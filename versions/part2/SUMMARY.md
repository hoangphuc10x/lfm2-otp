# Part 2 — FP8 weight quantization

**Ngày tạo:** 2026-07-17 · **Dựa trên:** part1 (43.82đ) · **Image tag:** `hoangphuc109/lfm2-otp:sub-02`
**Trạng thái:** chờ điểm.

---

## Thay đổi so với part1 (đúng 1 biến — RULES.md R2.1)
| | part1 | **part2** |
|---|---|---|
| Weights | BF16 | **FP8 (`--quantization=fp8`)** |
| KV cache | fp8 | fp8 (giữ) |
| Còn lại | | giữ nguyên (max-len 4608, prefix-cache, cuda graph, util 0.92) |

File thay đổi: `files/docker-compose.yml` (chỉ thêm `--quantization=fp8` + đổi tag). **Dockerfile không đổi** (weights gốc vẫn bake vào /model; FP8 là online quant lúc load).

## Giả thuyết
Decode & prefill của LFM2.5-1.2B là **memory-bandwidth-bound**. FP8 weights giảm ~1/2 số byte đọc mỗi bước → kỳ vọng:
- **TPOT 5ms → ~2.5-3ms** (đòn bẩy chính, +15~24đ).
- **TTFT 98ms → giảm** nhờ prefill nhanh hơn (+vài đến ~10đ).
- Tận dụng ngân sách accuracy đang còn nguyên (Δ=0 ở part1).

## Rủi ro & phải kiểm
1. **Δ accuracy tăng** do FP8 weights → BẮT BUỘC chạy `eval/bench-gpqa-diamond.sh`, xác nhận **Δ ≤ 0.10** (giữ f_δ=1). Nếu Δ vượt → cân nhắc FP8 chỉ một phần / quay lại.
2. **Tương thích kiến trúc:** LFM2.5 là hybrid (conv + attention). Cần xác nhận vLLM v0.22.1 load được `--quantization=fp8` cho kiến trúc này — **healthcheck phải pass**. Nếu server không lên → thử `--quantization=fp8 --kv-cache-dtype=auto` hoặc bỏ FP8 KV để cô lập lỗi.
3. Nếu FP8 online không hỗ trợ → phương án B: pre-quantize offline (llm-compressor) rồi bake bản FP8 vào /model.

## Việc cần làm để nộp part2
1. `DOCKERHUB_USER=hoangphuc109 TAG=sub-02 bash scripts/build_and_push.sh` (Dockerfile không đổi nên có thể tái dùng image part1, chỉ cần retag sub-02 — xem ghi chú dưới).
2. `bash scripts/serve_local.sh up` → healthcheck pass?
3. `python bench/run_bench.py ... --name sub-02` → so TPOT/TTFT với part1.
4. `bash eval/bench-gpqa-diamond.sh` → **Δ ≤ 0.10?**
5. Nộp `docker-compose.yml` (bản part2) lên Portal.

> Ghi chú build: vì Dockerfile giống part1, có thể retag thay vì build lại:
> `docker tag hoangphuc109/lfm2-otp:sub-01 hoangphuc109/lfm2-otp:sub-02 && docker push hoangphuc109/lfm2-otp:sub-02`
> (FP8 nằm ở command runtime, không nằm trong image.)

## Kết quả
_(điền vào score.md khi có điểm; so sánh với part1)_
