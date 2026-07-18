# CLAUDE.md — LLM Inference Optimization Challenge (Phase 1)

> Đây là **index đề bài**. Nội dung chi tiết đã tách thành các file rule đơn-chủ-đề trong
> [.claude/rules/](.claude/rules/) — Claude Code **auto-load** toàn bộ thư mục này mỗi phiên.
> Ngôn ngữ làm việc: tiếng Việt (thuật ngữ kỹ thuật giữ nguyên tiếng Anh).

## TL;DR (đọc trước)

- **Mục tiêu số 1 (vòng online):** tối đa hóa **ERS** (điểm tốc độ dựa trên TTFT + TPOT) — leaderboard chấm mỗi lần nộp.
- **Ràng buộc số 1 (sau online):** giữ accuracy `Δ ≤ 0.10` so với baseline BF16; `Δ ≥ 0.16` → 0 điểm.
- **Framework bắt buộc:** chỉ **vLLM**. **Hardware chấm:** MiG H200 — 18GB VRAM, 3 CPU, 8GB RAM.
- **Model:** `LiquidAI/LFM2.5-1.2B-Instruct` (1.2B). Bottleneck nghiêng về **latency/scheduling**.
- **Điểm cuối:** `Score = 100 × ERS × f(Δ)`.

## Mục lục rules (.claude/rules/)

| File | Nội dung |
|---|---|
| [overview.md](.claude/rules/overview.md) | TL;DR mục tiêu, ràng buộc, con trỏ tổng |
| [workload.md](.claude/rules/workload.md) | Nhiệm vụ, đặc điểm workload, trace công khai |
| [grading-environment.md](.claude/rules/grading-environment.md) | Hạ tầng & môi trường chấm (GPU/CPU/RAM) |
| [scoring.md](.claude/rules/scoring.md) | Công thức ERS, accuracy gate f(Δ), điểm cuối |
| [optimization-space.md](.claude/rules/optimization-space.md) | Các kỹ thuật tối ưu được phép (vLLM) |
| [optimization-discipline.md](.claude/rules/optimization-discipline.md) | Kỷ luật tối ưu R2 (đo trước, ROI, ngân sách Δ) |
| [benchmarking.md](.claude/rules/benchmarking.md) | Quy tắc benchmark R3 |
| [golden-rules.md](.claude/rules/golden-rules.md) | Quy tắc VÀNG R1 + anti-cheating (không vi phạm) |
| [submission.md](.claude/rules/submission.md) | Quy trình nộp, Docker, R4, docker-compose mẫu, checklist |
| [tie-break.md](.claude/rules/tie-break.md) | Tie-break & khiếu nại |
| [folder-conventions.md](.claude/rules/folder-conventions.md) | Cấu trúc thư mục + quy tắc code R5 |
| [versioning-workflow.md](.claude/rules/versioning-workflow.md) | Quy trình phiên bản versions/ (tự động khi user gửi điểm) |
| [communication-and-done.md](.claude/rules/communication-and-done.md) | Giao tiếp R6 + định nghĩa "Done" R7 |

> Luật thực thi R1–R7 (trước ở RULES.md) đã nằm rải trong các file rule tương ứng ở trên.
