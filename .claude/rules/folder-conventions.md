# Quy ước thư mục & code

> Cập nhật file này khi cấu trúc project đổi. Trạng thái hiện tại: **khung code đã dựng xong.**

## Cấu trúc thư mục

```
LLM-otp/
├── CLAUDE.md                 # index đề bài (trỏ tới .claude/rules/)
├── RULES.md                  # index luật thực thi (trỏ tới .claude/rules/)
├── .claude/rules/            # các rule đơn-chủ-đề (auto-load)
├── Dockerfile                # build image giải pháp (bake weights vào /model)
├── docker-compose.yml        # config nộp cho BTC (đổi image:tag đã push)
├── .dockerignore / .gitignore
├── src/                      # code custom (kernels/plugin/launcher — khi cần)
├── configs/                  # các bộ tham số vLLM để so sánh
├── bench/
│   ├── ers.py                # tính điểm ERS đúng công thức (constants cố định)
│   ├── trace.py              # đọc trace + tổng hợp prompt giữ prefix multi-turn
│   ├── run_bench.py          # phát lại trace vào endpoint, đo TTFT/TPOT, tính ERS
│   ├── make_synthetic_trace.py  # sinh trace test khi chưa có trace thật
│   ├── requirements.txt      # aiohttp
│   ├── trace_grading_public.jsonl  # (đặt trace thật của BTC vào đây)
│   └── results/              # kết quả benchmark từng cấu hình
├── eval/
│   └── bench-gpqa-diamond.sh # kiểm accuracy GPQA (lm_eval) -> ước lượng Δ
├── scripts/
│   ├── build_and_push.sh     # build + push image (1 tag / submission)
│   └── serve_local.sh        # dựng endpoint cục bộ để tự bench
├── notes/
│   └── submissions.md        # log tag <-> config <-> ERS <-> Δ
└── versions/                 # LƯU MỌI PHIÊN BẢN (xem versioning-workflow.md)
    ├── part1/{SUMMARY.md, files/, score.md}
    └── part2/...             # tạo dần mỗi lần nộp
```

## Quy trình chuẩn (end-to-end)

```
1. python bench/make_synthetic_trace.py            # (hoặc đặt trace thật vào bench/)
2. DOCKERHUB_USER=... TAG=sub-01 bash scripts/build_and_push.sh
3. bash scripts/serve_local.sh up                  # cần GPU
4. pip install -r bench/requirements.txt
   python bench/run_bench.py --trace bench/trace_synth.jsonl \
       --out bench/results/sub-01.json --name sub-01
5. bash eval/bench-gpqa-diamond.sh                 # kiểm Δ accuracy
6. Điền notes/submissions.md -> nộp docker-compose.yml lên Portal
```

## Quy tắc code & thư mục (R5)

- **R5.1** — Tuân theo cấu trúc thư mục ở trên. Tạo thư mục khi cần, cập nhật file này nếu cấu trúc đổi.
- **R5.2** — Code custom (kernel/plugin/launcher) đặt trong `src/`, có comment ngắn giải thích *tại sao*, không chỉ *cái gì*.
- **R5.3** — Không để file tạm/thử nghiệm rác trong repo. Dùng scratchpad cho thứ vứt đi.
- **R5.4** — Ghi chú quyết định quan trọng (đã thử gì, kết quả, vì sao chọn/loại) vào `notes/`. Đây là trí nhớ dài hạn của dự án.
- **R5.5** — Không commit weights model vào repo (chỉ bake vào image). Repo giữ code + config + notes.

## Nguyên tắc làm việc chung
- Mọi thay đổi cấu hình phải **đo ERS cục bộ** trước khi nộp (xem [benchmarking.md](benchmarking.md)).
- Mỗi cấu hình đáng cân nhắc → lưu số liệu vào `bench/results/` để so sánh.
- Trước khi chốt bài nộp: kiểm accuracy để đảm bảo `Δ ≤ 0.10` (an toàn) hoặc ít nhất `< 0.16`.
- Không hardcode, không dual-path, không network calls (xem [golden-rules.md](golden-rules.md)).
- Giữ nguyên các dòng `#Don't change this to vllm-server` trong docker-compose.
