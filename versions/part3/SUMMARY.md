# Part 3 — N-gram speculative decoding

**Ngày:** 2026-07-17 · **Dựa trên:** part2 (55.23đ, FP8) · **Trạng thái:** chờ nộp + chờ điểm.

## Thay đổi so với part2 (1 biến)
Thêm `--speculative-config={"method":"ngram","num_speculative_tokens":5,"prompt_lookup_max":4,"prompt_lookup_min":2}`.
File đổi: `files/docker-compose.yml`. **Không build lại image** (flag runtime).

## Giả thuyết
- TPOT là đòn bẩy #1 (part2 mới 44% tối đa). N-gram spec decode dự đoán token từ n-gram lặp
  trong context; workload **multi-turn lặp ngữ cảnh** → acceptance kỳ vọng cao → sinh nhiều token/step.
- Mục tiêu: **TPOT 4ms → ~2-2.5ms** (+10~17đ).
- **An toàn accuracy tuyệt đối:** với greedy (temperature=0), spec decode dùng rejection sampling
  cho **output y hệt** decode thường → **Δ = 0**. Không tốn ngân sách accuracy.

## Rủi ro
1. Nếu acceptance thấp (context ít lặp) → overhead verify có thể làm TPOT **tệ hơn** một chút.
   → Đo local; nếu xấu, giảm `num_speculative_tokens` (5→3) hoặc bỏ.
2. TTFT có thể tăng nhẹ do overhead dựng draft ở bước đầu — theo dõi TTFT p50.
3. Cú pháp `--speculative-config` phải đúng version vLLM v0.22.1. Nếu lỗi khởi động →
   thử cú pháp cũ: `--speculative-model "[ngram]" --num-speculative-tokens 5
   --ngram-prompt-lookup-max 4 --ngram-prompt-lookup-min 2`.

## Cần làm
1. Cập nhật compose (đã set ở root) → nộp (không build lại).
2. `serve_local.sh up` → healthcheck pass? Xem log có bật spec decode không.
3. `run_bench.py` local vài lần → so TPOT/TTFT với part2 (delta có vượt nhiễu?).
4. Gửi điểm → tôi so sánh + dựng part4.

## Ý tưởng cho part4+ (hàng đợi)
- **TTFT tuning:** thử bật/tắt chunked prefill, `--max-num-seqs`, kiểm CUDA graph coverage.
- **Tuning spec decode:** quét `num_speculative_tokens` (3/5/7) tìm điểm tối ưu acceptance vs overhead.
- **EAGLE / draft model** nếu n-gram acceptance thấp (mạnh hơn nhưng tốn VRAM + phức tạp).
- **Đo & chốt Δ accuracy của FP8** (part2) bằng GPQA — việc BẮT BUỘC trước khi chọn bài chốt.
