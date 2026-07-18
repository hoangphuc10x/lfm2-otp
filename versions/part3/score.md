# Part 3 — Điểm (n-gram speculative decoding)

## ❌❌ BỎ HẲN — spec decode crash với LFM2 hybrid

**Kết luận cuối (2026-07-18):** đã sửa được lỗi quoting (dùng file config), server KHỞI ĐỘNG được,
NHƯNG khi sinh thật thì **engine core sập**: request đầu chậm rồi các request sau `http=500`,
`/health=503`, container restart. Test lại lúc warm vẫn `500/503`.

**Nguyên nhân:** LFM2.5 là model **hybrid Mamba + short-conv**; speculative decoding (n-gram)
**không tương thích ổn định** với kiến trúc mamba/hybrid trong vLLM v0.22.1.

→ **Spec decode LOẠI khỏi mọi phương án.** Giữ part2 (FP8, 55.23) làm nền. Chuyển sang tuning an toàn (part4+).

---
## (Lịch sử) THẤT BẠI lần 1 — unscoreable

**Lỗi:** `protocol aborted: transport errors 330/330 (> 10%) — contestant unscoreable`

→ **330/330 request lỗi transport = server KHÔNG chạy / crash ngay khi startup.** Không phải vấn đề
tốc độ hay điểm — endpoint không phản hồi.

**Chẩn đoán:** part2 (chỉ FP8) chạy tốt (55.23). Biến mới duy nhất ở part3 là
`--speculative-config` (n-gram spec decode) → gần như chắc chắn spec decode làm vLLM crash lúc load,
hoặc **FP8 + spec decode xung khắc** trong vLLM v0.22.1.

**Hành động:**
- ✅ Rollback root docker-compose về **part2 (FP8)** — trạng thái chấm được (55.23).
- ⏸️ Spec decode tạm gác. Sẽ debug trên instance test **g6** (đọc log crash thật) trước khi thử lại.

## Việc cần làm để debug part3 (trên g6)
1. `docker compose up` với dòng spec decode → đọc `docker compose logs` tìm traceback thật.
2. Giả thuyết cần loại trừ:
   - Cú pháp `--speculative-config` (đã xác nhận đúng dạng JSON theo docs vLLM).
   - **FP8 + spec decode không tương thích** → thử spec decode KHÔNG kèm `--quantization=fp8`.
   - vLLM v0.22.1 bản cũ chưa hỗ trợ ngram spec decode với engine V1 → thử tắt/bật `VLLM_USE_V1`.
3. Nếu FP8+spec xung khắc: chọn 1 trong 2 (ưu tiên FP8 vì đã +11đ), hoặc tìm đòn bẩy TPOT khác.
