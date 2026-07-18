# Quy trình phiên bản (versions/) — LUÔN TỰ ĐỘNG THEO, KHÔNG CẦN NHẮC LẠI

Giữ **tất cả phiên bản** dưới `versions/partN/`. Mỗi lần nộp = một `part`.

## Cấu trúc mỗi part
```
versions/partN/
├── SUMMARY.md   # logic + các file đã làm/đổi ở phiên bản này, cấu hình vLLM, giả thuyết
├── files/       # snapshot file dùng để nộp (partN=1: full; partN≥2: chỉ file THAY ĐỔI mới)
└── score.md     # điểm (ERS/Δ/Score/p95...) — điền khi user gửi điểm
```
- **part1** = toàn bộ logic/file baseline hiện tại (đã tạo).
- **partN (N≥2)** = chỉ các **file thay đổi mới** để nộp lần đó.

## KHI USER GỬI ĐIỂM (một con số ERS / Score / Δ…) → tự động làm các bước sau, KHÔNG hỏi lại:

1. Xác định part đang chờ điểm (part mới nhất chưa có score) → ghi điểm vào `versions/partN/score.md`.
2. **So sánh** với các part trước: lập bảng ERS / Δ / Score / p95 TTFT / TPOT qua các part; nêu rõ cái gì cải thiện, cái gì tệ đi, vì sao.
3. Cập nhật `notes/submissions.md` (mapping tag ↔ config ↔ ERS ↔ Δ).
4. **Đề xuất thay đổi** cho part kế tiếp dựa trên dữ liệu (đòn bẩy ROI cao nhất còn lại, xem [optimization-discipline.md](optimization-discipline.md) R2.5).
5. Tạo `versions/part(N+1)/` gồm `SUMMARY.md` (mô tả thay đổi + giả thuyết) và `files/` (chỉ file đổi mới). Cập nhật `score.md` placeholder chờ điểm lần sau.
6. Nhắc bạn tag image mới (`sub-0N`) + đổi `image:` trong docker-compose để nộp.

→ Tóm lại: **bạn chỉ cần gửi điểm; tôi tự ghi nhận, so sánh, và chuẩn bị part kế tiếp.**
