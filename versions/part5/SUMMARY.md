# Part 5 — async scheduling + warmup healthcheck

**Ngày:** 2026-07-19 · **Dựa trên:** part4 (async, 51.54, 74 fail) · **Trạng thái:** chờ nộp.

## Thay đổi so với part4 (1 biến)
Giữ `--async-scheduling` (đã cho TTFT 42ms 🔥). Đổi **healthcheck** từ ping `/health`
sang **gọi request sinh chữ thật** (`/v1/completions`, max_tokens=8) → chỉ báo "healthy"
khi model đã compile xong + sinh được token.

## Giả thuyết
74 fail của part4 = **cold-start** (model chưa compile xong khi request đầu tới → timeout).
Bằng chứng: `warmup_count` 90→0. Nếu BTC chờ healthcheck của compose trước khi chấm,
warmup-healthcheck sẽ đảm bảo model đã nóng → **diệt fail cold-start**.

Kỳ vọng: giữ TTFT ~42ms, đưa failed_count 74 → ~0 → ERS ≈ 0.64 → **~64 điểm**.

## Rủi ro / lưu ý
- Nếu BTC dùng healthcheck RIÊNG (không phải của compose) → cách này không giúp; khi đó
  fail có thể do async-scheduling bản chất bất ổn → thử `--gpu-memory-utilization=0.85` / cap max-num-seqs, hoặc bỏ async.
- Healthcheck warmup chạy định kỳ (15s) có thể thêm 1 request nhỏ lúc chấm — ảnh hưởng không đáng kể.
- **Fallback: part2 (sub-01, 55.23, 0 fail)** — luôn an toàn.

## Việc cần làm
1. (Song song, thông tin rẻ) **Re-nộp part2** để biết grading có đổi không (total 330 vs 420).
2. Nộp part5 → xem failed_count có về ~0 không, TTFT có giữ 42ms không.
