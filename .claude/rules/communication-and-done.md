# Giao tiếp khi làm việc & Định nghĩa "Done"

## Quy tắc giao tiếp (R6)

- **R6.1** — Khi đề xuất tối ưu: nêu **giả thuyết → cách đo → kết quả kỳ vọng**, không khẳng định chắc chắn khi chưa đo.
- **R6.2** — Khi một thay đổi đánh đổi accuracy lấy tốc độ: **nói rõ ước lượng Δ** và rủi ro vượt ngân sách 0.10.
- **R6.3** — Báo cáo trung thực: nếu benchmark tệ hơn hoặc bước bị bỏ qua → nói thẳng kèm số liệu.
- **R6.4** — Khi chạm giới hạn/nghi ngờ vi phạm R1 → dừng và hỏi user, không tự quyết. Xem [golden-rules.md](golden-rules.md).

## Định nghĩa "Done" cho một cấu hình ứng viên nộp (R7)

Một cấu hình chỉ được coi là **sẵn sàng nộp** khi:
1. ✅ Container build + healthcheck pass ở mức tài nguyên ~MiG.
2. ✅ Chạy full trace cục bộ, **0 request fail/timeout/0-token**.
3. ✅ ERS đo được, ghi vào `bench/results/`.
4. ✅ Δ accuracy đã kiểm (≥ ước lượng), nằm trong vùng an toàn hoặc chấp nhận được.
5. ✅ Không vi phạm bất kỳ luật R1 nào.
6. ✅ Image tag cố định đã push Public; compose trỏ đúng.
7. ✅ Đã ghi mapping vào `notes/submissions.md`.
