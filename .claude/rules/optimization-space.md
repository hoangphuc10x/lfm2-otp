# Không gian tối ưu (chỉ dùng vLLM)

> Đây là các kỹ thuật **được phép/khuyến khích**. Kỷ luật khi áp dụng (đo trước, ROI, ngân sách accuracy) nằm ở [optimization-discipline.md](optimization-discipline.md).

Các hướng được phép:

1. **Quantization** — Online Quantization (vd FP8 weights/activations). Đánh đổi với ngân sách `Δ ≤ 0.10`.
2. **KV Cache & Memory** — Paged Attention; KV cache quant (FP8/INT8); **Prefix caching** (rất quan trọng vì multi-turn); Semantic caching; Offloading CPU/NVMe (cẩn thận RAM 8GB).
3. **Serving & Scheduling** — Continuous/Dynamic batching; **Speculative decoding**; Memory-aware scheduling.
4. **System & Runtime** — Custom CUDA/Triton kernels; Fused attention (FlashAttention / FlashInfer); Memory layout; **CUDA Graphs**.

**Ưu tiên đề xuất (heuristic ban đầu, cần benchmark xác nhận):**
- Bật `--enable-prefix-caching` (multi-turn → hit rate cao → giảm TTFT mạnh).
- Bật CUDA Graphs (giảm TTFT overhead cho batch nhỏ).
- Model chỉ 1.2B → thử FP8 online quant để tăng tốc decode (kiểm accuracy Δ).
- Speculative decoding: cân nhắc — có thể giảm TPOT nếu draft tốt, nhưng thêm rủi ro & bộ nhớ.
- `--max-model-len` chỉ cần ~4k+200; **không cần 32768** như mẫu → giảm để tiết kiệm KV cache & tăng concurrency.
