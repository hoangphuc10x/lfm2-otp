#!/usr/bin/env python3
"""
Sinh trace tổng hợp KHỚP đặc tả đề bài để test pipeline khi chưa có
trace_grading_public.jsonl thật:
    - 15 conversation primer + 70 conversation được chấm (tổng 330 turn chấm).
    - arrival theo Poisson.
    - input ~ tối đa 4k token, output <= 200 token.

Xác định (deterministic) qua --seed để tái lập (RULES.md R3.4).

    python bench/make_synthetic_trace.py --out bench/trace_synth.jsonl
"""
from __future__ import annotations

import argparse
import json
import random


def gen(seed: int, n_primer: int, n_graded_conv: int, n_graded_turns: int,
        rate_per_s: float):
    rng = random.Random(seed)
    convs = []
    for i in range(n_primer):
        convs.append((f"primer{i:02d}", True))
    for i in range(n_graded_conv):
        convs.append((f"conv{i:02d}", False))

    # Phân bổ số turn cho mỗi graded conv sao cho tổng = n_graded_turns.
    turns_per = [1] * n_graded_conv
    for _ in range(n_graded_turns - n_graded_conv):
        turns_per[rng.randrange(n_graded_conv)] += 1

    items = []
    t = 0.0
    # Trộn: primer trước, rồi graded conversation, mỗi conv nhiều turn nối tiếp.
    for cid, is_primer in convs:
        n_turns = 1 if is_primer else turns_per[int(cid[4:])]
        base_in = rng.randint(200, 800)          # token đầu conv
        for turn in range(n_turns):
            # arrival Poisson: khoảng cách ~ Exponential(rate).
            t += rng.expovariate(rate_per_s)
            # input lớn dần theo turn (tích lũy lịch sử), clamp ~4k.
            in_tok = min(4000, base_in + turn * rng.randint(150, 400))
            out_tok = rng.randint(40, 200)
            items.append({
                "conv_id": cid,
                "turn": turn,
                "arrival": round(t, 4),
                "in_tokens": in_tok,
                "out_tokens": out_tok,
                "is_primer": is_primer,
            })
    items.sort(key=lambda x: x["arrival"])
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="bench/trace_synth.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--primer", type=int, default=15)
    ap.add_argument("--graded-conv", type=int, default=70)
    ap.add_argument("--graded-turns", type=int, default=330)
    ap.add_argument("--rate", type=float, default=2.0, help="request/giây (Poisson)")
    args = ap.parse_args()

    items = gen(args.seed, args.primer, args.graded_conv, args.graded_turns, args.rate)
    with open(args.out, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    graded = sum(1 for i in items if not i["is_primer"])
    print(f"[synth] {len(items)} turn ({graded} chấm) -> {args.out}")


if __name__ == "__main__":
    main()
