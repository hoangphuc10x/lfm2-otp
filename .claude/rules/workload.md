# Nhiệm vụ & Workload

Triển khai + tối ưu một **LLM inference server** cho `LFM2.5-1.2B-Instruct`, xử lý một **trace multi-turn** mô phỏng traffic production.

Đặc điểm workload:
- **70 hội thoại** đến theo phân phối **Poisson**.
- Tổng **330 request được chấm** (sau **15 hội thoại primer** warmup — không tính điểm).
- **Context input tối đa ~4k token (~12k ký tự)**.
- **Output tối đa 200 token**.
- Multi-turn → có **prefix chung giữa các turn** → **prefix caching cực kỳ có giá trị**.

BTC benchmark **trực tiếp** vào endpoint của thí sinh (OpenAI-compatible API, port 8000).

## Trace công khai
- File: `bench/trace_grading_public.jsonl` (bản đã lược prompt — chỉ có `arrival` + số token in/out mỗi lượt).
- BTC giữ bản đầy đủ có prompt thật để chấm. → **Không được** dựa vào nội dung prompt cụ thể; chỉ dùng trace để mô phỏng timing/tải khi tự benchmark.
