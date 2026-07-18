# Overview — TL;DR đề bài

> Ngôn ngữ làm việc: tiếng Việt (thuật ngữ kỹ thuật giữ nguyên tiếng Anh).
> Đây là "bộ nhớ đề bài" cô đọng. Chi tiết từng phần nằm ở các file rule khác trong thư mục này.

- **Mục tiêu số 1 (vòng online):** tối đa hóa **ERS** (điểm tốc độ, dựa trên TTFT + TPOT). Đây là thứ leaderboard chấm mỗi lần nộp. → xem [scoring.md](scoring.md).
- **Ràng buộc số 1 (sau online):** giữ **accuracy** không tụt quá `Δ ≤ 0.10` so với baseline BF16, nếu không sẽ bị phạt điểm (`f(Δ)`); `Δ ≥ 0.16` → 0 điểm.
- **Framework bắt buộc:** chỉ được dùng **vLLM**. Không được đổi framework khác. → xem [golden-rules.md](golden-rules.md).
- **Hardware chấm:** 1 MiG H200 slice — **18GB VRAM, 3 CPU core, 8GB RAM**. Nhỏ → phải tiết kiệm bộ nhớ. → xem [grading-environment.md](grading-environment.md).
- **Model:** `LiquidAI/LFM2.5-1.2B-Instruct` (nhỏ, 1.2B). Bottleneck thực tế nghiêng về **latency/scheduling**, không phải throughput thô.
- **Nộp bài:** đóng gói Docker image → push public lên Docker Hub → nộp `docker-compose.yml` lên Portal BTC. → xem [submission.md](submission.md).
- **Điểm cuối:** `Score = 100 × ERS × f(Δ)`. Điểm đội = Score tốt nhất trong ≤ 5 bài tự chọn còn hợp lệ.

Công thức cần luôn nhớ khi tinh chỉnh: **ERS là hàm bậc 2 (γ=2)** của mức độ "nhanh". Cải thiện latency ở vùng gần floor cho điểm cận biên rất lớn.

**Nguyên tắc chung khi làm việc:** mọi quyết định tối ưu phải có **số liệu ERS đo được, không phỏng đoán** → xem [optimization-discipline.md](optimization-discipline.md), [benchmarking.md](benchmarking.md).
