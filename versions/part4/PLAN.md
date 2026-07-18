# Part 4 — Lab tuning trên RunPod (an toàn, không spec decode)

**Nền:** part2 (FP8, 55.23, ổn định). Spec decode đã loại (crash hybrid).
**Mục tiêu:** đo TTFT/TPOT từng config trên GPU thật → chọn config tốt nhất → nộp BTC.
**Lưu ý:** RunPod = L40 16-CPU; BTC = MiG H200 3-CPU. TPOT transfer tốt; TTFT phải xác nhận lại trên BTC.

## Cách đo (mỗi config)
1. **Edit Pod** → đổi *Container Start Command* → save (pod restart) → chờ health 200.
2. Mở **web terminal**, chạy benchmark (giống nhau cho mọi config):
```bash
vllm bench serve --model LFM2.5-1.2B-Instruct --base-url http://localhost:8000 \
  --dataset-name random --random-input-len 1000 --random-output-len 150 \
  --num-prompts 100 --request-rate 10 --ignore-eos
```
(Nếu `vllm bench` không có: `python3 /vllm-workspace/benchmarks/benchmark_serving.py` với tham số tương tự.)
3. Gửi lại: **Mean/Median/P99 TTFT** và **Mean/Median TPOT**.

## Các config cần test (Container Start Command)

Phần chung (giữ nguyên): 
`/model --served-model-name=LFM2.5-1.2B-Instruct --host=0.0.0.0 --port=8000 --max-model-len=4608 --gpu-memory-utilization=0.92 --enable-prefix-caching`

| Tên | Thêm vào phần chung | Giả thuyết |
|---|---|---|
| **part2** (baseline) | `--kv-cache-dtype=fp8 --quantization=fp8` | mốc so sánh |
| **E1** | `--quantization=fp8` (bỏ kv-fp8) | bỏ overhead quant KV + tốt accuracy; ta thừa VRAM |
| **E3** | `--kv-cache-dtype=fp8 --quantization=fp8 --max-num-batched-tokens=8192` | prefill nhanh hơn → TTFT ↓ |
| **E4** | `--kv-cache-dtype=fp8 --quantization=fp8 --no-enable-chunked-prefill` | tải thấp → prefill 1 lần → TTFT ↓ |
| **E2** | `--kv-cache-dtype=fp8 --quantization=fp8 --async-scheduling` | giảm overhead CPU (hợp BTC 3-CPU) |

Ưu tiên: part2 → E1 → E2 → E3 → E4.

## Accuracy (BẮT BUỘC trước khi chốt)
Chạy GPQA để đo Δ thật của FP8 (online Δ=0 là giả). E1 (bỏ FP8 KV) cũng nhằm bảo toàn accuracy.
```bash
lm_eval --model local-completions \
  --model_args base_url=http://localhost:8000/v1/completions,model=LFM2.5-1.2B-Instruct,num_concurrent=8 \
  --tasks gpqa_diamond_zeroshot --batch_size auto
```
