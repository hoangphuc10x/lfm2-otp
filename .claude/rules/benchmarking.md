# Quy tắc benchmark

- **R3.1** — Mọi cấu hình đáng cân nhắc → chạy `bench/run_bench.py` và lưu kết quả vào `bench/results/<tên-cấu-hình>.json`.
- **R3.2** — Tính ERS **đúng công thức** trong [scoring.md](scoring.md) (TTFT/TPOT floor-ceiling, γ=2, w=0.5). Không tự chế công thức.
- **R3.3** — Mô phỏng đúng tính chất trace: arrival theo Poisson, multi-turn, ~4k input / ≤200 output, có warmup (bỏ 15 primer khi tính điểm). Xem [workload.md](workload.md).
- **R3.4** — Ghi lại kèm mỗi kết quả: commit/diff cấu hình, tham số vLLM đầy đủ, phiên bản image, ngày đo. Kết quả không tái lập được = vô giá trị.
- **R3.5** — Khi so sánh 2 cấu hình, chạy đủ lần để vượt nhiễu đo (BTC lấy trung vị nhiều lần → ta cũng nên).
