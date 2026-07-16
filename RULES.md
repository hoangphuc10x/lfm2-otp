# RULES.md — Quy tắc làm việc cho dự án

> Đọc kèm [CLAUDE.md](CLAUDE.md) (đề bài & quy định). File này là **luật thực thi** khi làm việc.
> Nguyên tắc chung: **mọi quyết định tối ưu phải có số liệu ERS đo được, không phỏng đoán.**

---

## R1. Quy tắc VÀNG (không bao giờ vi phạm)

| # | Luật | Vì sao |
|---|---|---|
| R1.1 | **Chỉ dùng vLLM.** Không thay framework (TGI, TensorRT-LLM, SGLang...). | Quy định đề bài. |
| R1.2 | **Không hardcode / pre-bake / dual-path / cache đáp án.** | Anti-cheating → hủy kết quả. |
| R1.3 | **Không network call ra ngoài** trong lúc serve. Weights phải nằm sẵn trong image. | Anti-cheating + môi trường chấm có thể không có internet. |
| R1.4 | **Không sửa tokenizer/weights trái phép.** Quantization hợp lệ; đổi nội dung thì không. | Anti-cheating. |
| R1.5 | **Không tráo image sau khi nộp.** Mỗi submission = 1 tag cố định, immutable. | Anti-cheating. |
| R1.6 | Giữ nguyên các dòng `#Don't change this to vllm-server` trong docker-compose (entrypoint dạng `python3 -m ...`). | Ràng buộc BTC. |
| R1.7 | Giữ `--served-model-name=LFM2.5-1.2B-Instruct`, `--host=0.0.0.0`, `--port=8000`. | BTC gọi endpoint theo đúng tên/cổng. |

Nếu một thay đổi có nguy cơ chạm R1 → **dừng lại, hỏi user trước.**

---

## R2. Quy tắc tối ưu (optimization discipline)

- **R2.1 — Đo trước, sửa sau.** Không đổi tham số nào mà không có baseline ERS để so sánh. Mỗi lần đổi **1 biến** khi có thể, để biết biến nào tạo ra khác biệt.
- **R2.2 — Ổn định > tốc độ cận biên.** Một request timeout / 0 token = 0 điểm cho request đó. Không đánh đổi để vài request fail nhằm tăng tốc số còn lại.
- **R2.3 — Tối ưu cả tail.** Theo dõi **p95 TTFT** (tie-break) chứ không chỉ mean. Tránh queueing spikes.
- **R2.4 — Ngân sách accuracy là `Δ ≤ 0.10`.** Mọi kỹ thuật giảm chất lượng (quant, spec decoding sai...) phải nằm trong ngân sách này. Kiểm accuracy trước khi coi một cấu hình là "ứng viên nộp".
- **R2.5 — Ưu tiên theo ROI (ước lượng, cần xác nhận bằng đo):**
  1. `--enable-prefix-caching` (multi-turn → hit cao → giảm TTFT).
  2. Giảm `--max-model-len` xuống ~4300 (chừa đủ 4k input + 200 output) → nhiều KV cache hơn → concurrency cao hơn.
  3. CUDA Graphs (giảm overhead TTFT ở batch nhỏ).
  4. FP8 online quant (weights/KV) — kiểm Δ.
  5. Speculative decoding — chỉ nếu đo được TPOT giảm mà Δ vẫn an toàn.
- **R2.6 — Không copy config thần thánh.** Config mẫu của BTC (`max-model-len=32768`) là baseline, không phải mục tiêu. Mọi giá trị đều phải justify được.
- **R2.7 — Bám ràng buộc phần cứng:** 18GB VRAM, 3 CPU core, 8GB RAM. Test ở mức tài nguyên tương đương; cẩn thận CPU/NVMe offloading vì RAM chỉ 8GB.

---

## R3. Quy tắc benchmark

- **R3.1** — Mọi cấu hình đáng cân nhắc → chạy `bench/run_bench.py` và lưu kết quả vào `bench/results/<tên-cấu-hình>.json`.
- **R3.2** — Tính ERS **đúng công thức mục 3 của CLAUDE.md** (TTFT/TPOT floor-ceiling, γ=2, w=0.5). Không tự chế công thức.
- **R3.3** — Mô phỏng đúng tính chất trace: arrival theo Poisson, multi-turn, ~4k input / ≤200 output, có warmup (bỏ 15 primer khi tính điểm).
- **R3.4** — Ghi lại kèm mỗi kết quả: commit/diff cấu hình, tham số vLLM đầy đủ, phiên bản image, ngày đo. Kết quả không tái lập được = vô giá trị.
- **R3.5** — Khi so sánh 2 cấu hình, chạy đủ lần để vượt nhiễu đo (BTC lấy trung vị nhiều lần → ta cũng nên).

---

## R4. Quy tắc Docker & nộp bài

- **R4.1** — Base image: `vllm/vllm-openai:v0.22.1` (hoặc phiên bản đã kiểm chứng tương thích). Weights bake sẵn vào `/model`.
- **R4.2** — Tag image **có phiên bản** (vd `:sub-01`, `:sub-02`), **không dùng `latest`** mơ hồ cho bài nộp. 1 submission = 1 tag không đổi.
- **R4.3** — Image phải **Public** trên Docker Hub trước khi nộp.
- **R4.4** — Trước khi nộp: chạy checklist mục 9 của CLAUDE.md. Container phải healthcheck pass và không có request fail dưới tải trace.
- **R4.5** — `docker-compose.yml` nộp phải trỏ đúng `image:tag` đã push và giữ ràng buộc R1.6/R1.7.
- **R4.6** — Lưu lại mapping: `submission tag ↔ config ↔ ERS đo được ↔ Δ accuracy` trong `notes/submissions.md`. Cần khi chọn ≤ 5 bài cuối.

---

## R5. Quy tắc code & thư mục

- **R5.1** — Tuân theo cấu trúc thư mục ở mục 8 CLAUDE.md. Tạo thư mục khi cần, cập nhật CLAUDE.md nếu cấu trúc đổi.
- **R5.2** — Code custom (kernel/plugin/launcher) đặt trong `src/`, có comment ngắn giải thích *tại sao*, không chỉ *cái gì*.
- **R5.3** — Không để file tạm/thử nghiệm rác trong repo. Dùng scratchpad cho thứ vứt đi.
- **R5.4** — Ghi chú quyết định quan trọng (đã thử gì, kết quả, vì sao chọn/loại) vào `notes/`. Đây là trí nhớ dài hạn của dự án.
- **R5.5** — Không commit weights model vào repo (chỉ bake vào image). Repo giữ code + config + notes.

---

## R6. Quy tắc giao tiếp khi làm việc

- **R6.1** — Khi đề xuất tối ưu: nêu **giả thuyết → cách đo → kết quả kỳ vọng**, không khẳng định chắc chắn khi chưa đo.
- **R6.2** — Khi một thay đổi đánh đổi accuracy lấy tốc độ: **nói rõ ước lượng Δ** và rủi ro vượt ngân sách 0.10.
- **R6.3** — Báo cáo trung thực: nếu benchmark tệ hơn hoặc bước bị bỏ qua → nói thẳng kèm số liệu.
- **R6.4** — Khi chạm giới hạn/nghi ngờ vi phạm R1 → dừng và hỏi user, không tự quyết.

---

## R7. Định nghĩa "Done" cho một cấu hình ứng viên nộp

Một cấu hình chỉ được coi là **sẵn sàng nộp** khi:
1. ✅ Container build + healthcheck pass ở mức tài nguyên ~MiG.
2. ✅ Chạy full trace cục bộ, **0 request fail/timeout/0-token**.
3. ✅ ERS đo được, ghi vào `bench/results/`.
4. ✅ Δ accuracy đã kiểm (≥ ước lượng), nằm trong vùng an toàn hoặc chấp nhận được.
5. ✅ Không vi phạm bất kỳ luật R1 nào.
6. ✅ Image tag cố định đã push Public; compose trỏ đúng.
7. ✅ Đã ghi mapping vào `notes/submissions.md`.
