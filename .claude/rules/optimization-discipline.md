# Kỷ luật tối ưu (optimization discipline)

> Nguyên tắc gốc: **mọi quyết định tối ưu phải có số liệu ERS đo được, không phỏng đoán.**
> Danh sách kỹ thuật được phép: [optimization-space.md](optimization-space.md). Cách đo: [benchmarking.md](benchmarking.md).

- **R2.1 — Đo trước, sửa sau.** Không đổi tham số nào mà không có baseline ERS để so sánh. Mỗi lần đổi **1 biến** khi có thể, để biết biến nào tạo ra khác biệt.
- **R2.2 — Ổn định > tốc độ cận biên.** Một request timeout / 0 token = 0 điểm cho request đó. Không đánh đổi để vài request fail nhằm tăng tốc số còn lại.
- **R2.3 — Tối ưu cả tail.** Theo dõi **p95 TTFT** (tie-break) chứ không chỉ mean. Tránh queueing spikes.
- **R2.4 — Ngân sách accuracy là `Δ ≤ 0.10`.** Mọi kỹ thuật giảm chất lượng (quant, spec decoding sai...) phải nằm trong ngân sách này. Kiểm accuracy trước khi coi một cấu hình là "ứng viên nộp".
- **R2.5 — Ưu tiên theo ROI (ước lượng, cần xác nhận bằng đo):**
  1. `--enable-prefix-caching` (multi-turn → hit cao → giảm TTFT).
  2. Giảm `--max-model-len` xuống ~4300 (chừa đủ 4k input + 200 output) → nhiều KV cache hơn → concurrency cao hơn.
  3. CUDA Graphs (giảm overhead TTFT ở batch nhỏ).
  4. FP8 online quant (weights/KV) — kiểm Δ.
  5. Speculative decoding — chỉ nếu đo được TPOT giảm mà Δ vẫn an toàn.
- **R2.6 — Không copy config thần thánh.** Config mẫu của BTC (`max-model-len=32768`) là baseline, không phải mục tiêu. Mọi giá trị đều phải justify được.
- **R2.7 — Bám ràng buộc phần cứng:** 18GB VRAM, 3 CPU core, 8GB RAM. Test ở mức tài nguyên tương đương; cẩn thận CPU/NVMe offloading vì RAM chỉ 8GB.
