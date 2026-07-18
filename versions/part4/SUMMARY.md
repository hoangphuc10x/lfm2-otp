# Part 4 — async scheduling

**Ngày:** 2026-07-18 · **Dựa trên:** part2 (55.23, đã verify accuracy Δ≈0) · **Trạng thái:** chờ nộp.

## Thay đổi so với part2 (1 biến)
Thêm `--async-scheduling`. Image dùng lại sub-01 (flag runtime, không build lại).

## Giả thuyết
Async scheduling giảm overhead scheduler trên CPU + lấp gap GPU giữa các step →
kỳ vọng **TTFT ↓** (đòn bẩy #2). Đặc biệt hợp **BTC chỉ 3 CPU** (nút cổ chai thật, L40 16-CPU không tái hiện được → phải đo trên BTC).

## An toàn
- KHÔNG phải tính năng model-specific (khác spec decode) → rủi ro crash thấp.
- part2 là fallback: nếu part4 tệ/crash, quay lại sub-01 part2 (55.23).

## Cần làm
1. **Boot-check trên pod** (trước khi tắt): đảm bảo health 200 + sinh được chữ.
2. Nộp `docker-compose.yml` (part4) lên BTC → so điểm với 55.23.
3. Nếu tốt → giữ; nếu tệ hơn → revert part2.
