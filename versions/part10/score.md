# Part 10 — Điểm (async + full-graph reduced-capture) — **HẠ ƯU TIÊN / có thể BỎ**

**Config:** part9 (sync FP8 + full-decode CUDA graph, capture[1..16]) **+** `--async-scheduling`.

## 2026-07-22 — CHƯA NỘP, và giả thuyết cốt lõi đã bị part9 làm suy yếu

part9 (sync + reduced-capture[1..16]) đã cho **75 fail** — tức **reduced-capture KHÔNG diệt cold-start fail**
ngay cả khi sync. Vậy giả thuyết chính của part10 ("capture nhanh 5 sizes → engine ready sớm → hết fail")
gần như đã bị bác: số lượng capture-size KHÔNG phải nguyên nhân fail. Fail đến từ **tổng startup time**
(weight load + torch.compile + capture), không riêng số size.

**Hệ quả:**
- part10 = async + full-graph: async có xu hướng **NHIỀU fail hơn** sync (74–89 vs 75) và full-graph = no-op TPOT.
  → part10 gần như không còn upside → **hạ ưu tiên, có thể bỏ.**
- Hướng đúng = **giảm TỔNG startup time** (bỏ compile + capture) = `--enforce-eager` = **part11**, giữ sync (ít fail hơn async).

**Nếu vẫn muốn thử async sau:** chỉ thử SAU khi part11 xác định fails có phải startup-bound không.
Nếu part11 (enforce-eager, startup nhanh nhất) mà fail VẪN ~75 → fails là structural (BTC bắn từ t=0
bất kể) → async cũng vô ích → khóa sổ hướng fails.
