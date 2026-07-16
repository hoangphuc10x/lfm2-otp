"""
Đọc trace_grading_public.jsonl và dựng lịch phát request.

Trace công khai chỉ có timing + số token (KHÔNG có prompt thật). Vì vậy ta
*tổng hợp* nội dung prompt sao cho:
  - đúng số token input mỗi turn (xấp xỉ),
  - multi-turn CÙNG conversation chia sẻ prefix chung -> để prefix caching
    phát huy tác dụng như traffic thật (CLAUDE.md mục 1).

Trace thật của BTC có prompt riêng; script này chỉ dùng để tự benchmark ERS cục bộ.

Do format chính xác của file chưa được công bố đầy đủ, loader này chấp nhận
nhiều tên field khác nhau và tự suy ra. Chỉnh FIELD_ALIASES nếu cần.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

# Các tên field có thể gặp -> tên chuẩn nội bộ.
FIELD_ALIASES = {
    "conv_id":   ["conv_id", "conversation_id", "session_id", "dialog_id", "id"],
    "turn":      ["turn", "turn_id", "turn_index", "round"],
    "arrival":   ["arrival", "arrival_time", "t", "timestamp", "ts", "time"],
    "in_tokens": ["in_tokens", "input_tokens", "prompt_tokens", "n_input", "tokens_in"],
    "out_tokens": ["out_tokens", "output_tokens", "completion_tokens", "max_tokens", "n_output", "tokens_out"],
    "is_primer": ["is_primer", "primer", "warmup"],
}


def _pick(d: dict, key: str, default=None):
    for alias in FIELD_ALIASES[key]:
        if alias in d and d[alias] is not None:
            return d[alias]
    return default


@dataclass
class TraceItem:
    conv_id: str
    turn: int
    arrival: float          # giây, tương đối so với t0
    in_tokens: int
    out_tokens: int
    is_primer: bool = False
    raw: dict = field(default_factory=dict)


def load_trace(path: str) -> list[TraceItem]:
    items: list[TraceItem] = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            items.append(
                TraceItem(
                    conv_id=str(_pick(d, "conv_id", f"conv{lineno}")),
                    turn=int(_pick(d, "turn", 0) or 0),
                    arrival=float(_pick(d, "arrival", 0.0) or 0.0),
                    in_tokens=int(_pick(d, "in_tokens", 0) or 0),
                    out_tokens=int(_pick(d, "out_tokens", 128) or 128),
                    is_primer=bool(_pick(d, "is_primer", False)),
                    raw=d,
                )
            )
    # Chuẩn hóa arrival về t0 = phát đầu tiên.
    if items:
        t0 = min(it.arrival for it in items)
        for it in items:
            it.arrival -= t0
    items.sort(key=lambda it: it.arrival)
    _mark_primer_if_missing(items)
    return items


def _mark_primer_if_missing(items: list[TraceItem]) -> None:
    """Nếu trace không đánh dấu primer: coi 15 conversation ĐẦU TIÊN là primer
    (theo thứ tự conversation xuất hiện), đúng như đề bài (15 primer warmup)."""
    if any(it.is_primer for it in items):
        return
    order: list[str] = []
    for it in items:
        if it.conv_id not in order:
            order.append(it.conv_id)
    primer_convs = set(order[:15])
    for it in items:
        if it.conv_id in primer_convs:
            it.is_primer = True


# --- Tổng hợp nội dung prompt giữ prefix chung theo conversation ---
# ~4 ký tự / token là xấp xỉ thô; đủ để tạo tải đúng độ dài.
CHARS_PER_TOKEN = 4
_LOREM = ("the model serves requests under load and we measure latency "
          "carefully across many turns of a simulated conversation ")


def _text_for_tokens(n_tokens: int, seed: str) -> str:
    n_chars = max(1, n_tokens * CHARS_PER_TOKEN)
    base = (seed + " ") + _LOREM
    reps = (n_chars // len(base)) + 1
    return (base * reps)[:n_chars]


def build_messages(convs_state: dict, item: TraceItem) -> list[dict]:
    """
    Dựng danh sách messages cho 1 turn, tích lũy lịch sử theo conv_id để tạo
    prefix chung (mô phỏng multi-turn -> prefix caching).

    convs_state: dict[conv_id] -> list[messages] (được cập nhật in-place).
    """
    history = convs_state.setdefault(item.conv_id, [])
    # Token input turn này = phần MỚI thêm (không đếm lại lịch sử đã có).
    prev_tokens = sum(len(m["content"]) // CHARS_PER_TOKEN for m in history)
    new_tokens = max(1, item.in_tokens - prev_tokens)
    user_text = _text_for_tokens(new_tokens, seed=f"{item.conv_id}-t{item.turn}")
    history.append({"role": "user", "content": user_text})
    messages = list(history)
    # Chèn placeholder assistant reply vào lịch sử cho turn sau (giữ prefix lớn dần).
    history.append({"role": "assistant", "content": "(reply placeholder)"})
    return messages
