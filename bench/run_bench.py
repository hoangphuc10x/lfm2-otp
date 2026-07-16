#!/usr/bin/env python3
"""
Benchmark ERS cục bộ: phát lại trace vào endpoint vLLM (OpenAI-compatible),
đo TTFT/TPOT từng request bằng streaming, rồi tính ERS theo đúng công thức đề bài.

Cách dùng:
    pip install -r bench/requirements.txt
    python bench/run_bench.py \
        --trace bench/trace_grading_public.jsonl \
        --base-url http://localhost:8000/v1 \
        --model LFM2.5-1.2B-Instruct \
        --out bench/results/baseline.json \
        --name baseline

Ghi chú:
    - Arrival được tôn trọng theo wall-clock (Poisson như trace). Có --speed để
      tua nhanh/chậm khi thử nghiệm (mặc định 1.0 = thời gian thật).
    - TTFT đo từ lúc GỬI request đến chunk có nội dung đầu tiên.
    - TPOT = (tổng thời gian sinh - TTFT) / (số token output - 1).
    - Xem RULES.md R3 để biết kỷ luật benchmark.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import time

import aiohttp

from ers import RequestResult, summarize
from trace import TraceItem, build_messages, load_trace


async def _stream_one(
    session: aiohttp.ClientSession,
    base_url: str,
    model: str,
    messages: list[dict],
    max_tokens: int,
    timeout_s: float,
    item: TraceItem,
) -> RequestResult:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    t_send = time.perf_counter()
    t_first: float | None = None
    t_last = t_send
    out_tokens = 0
    try:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=timeout_s)
        ) as resp:
            if resp.status != 200:
                body = (await resp.text())[:200]
                return RequestResult(item.conv_id, item.turn, 0, 0, 0,
                                     ok=False, is_primer=item.is_primer,
                                     error=f"HTTP {resp.status}: {body}")
            async for raw in resp.content:
                line = raw.decode("utf-8", "ignore").strip()
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices") or []
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        now = time.perf_counter()
                        if t_first is None:
                            t_first = now
                        t_last = now
                        out_tokens += 1  # xấp xỉ: 1 chunk ~ 1 token
                usage = chunk.get("usage")
                if usage and usage.get("completion_tokens"):
                    out_tokens = usage["completion_tokens"]  # con số chính xác nếu có
    except asyncio.TimeoutError:
        return RequestResult(item.conv_id, item.turn, 0, 0, out_tokens,
                             ok=False, is_primer=item.is_primer, error="timeout")
    except Exception as e:  # noqa: BLE001
        return RequestResult(item.conv_id, item.turn, 0, 0, out_tokens,
                             ok=False, is_primer=item.is_primer, error=repr(e))

    if t_first is None or out_tokens <= 0:
        return RequestResult(item.conv_id, item.turn, 0, 0, 0,
                             ok=False, is_primer=item.is_primer, error="0 token")

    ttft_ms = (t_first - t_send) * 1000.0
    gen_ms = (t_last - t_first) * 1000.0
    tpot_ms = gen_ms / max(1, out_tokens - 1)
    return RequestResult(item.conv_id, item.turn, ttft_ms, tpot_ms, out_tokens,
                         ok=True, is_primer=item.is_primer)


async def run(args) -> list[RequestResult]:
    items = load_trace(args.trace)
    print(f"[trace] {len(items)} request, "
          f"{sum(1 for i in items if i.is_primer)} primer (bỏ khi chấm)")

    convs_state: dict = {}
    results: list[RequestResult] = []
    tasks: list[asyncio.Task] = []
    t_start = time.perf_counter()

    connector = aiohttp.TCPConnector(limit=0)  # không giới hạn concurrency phía client
    async with aiohttp.ClientSession(connector=connector) as session:
        for item in items:
            # Chờ đến đúng thời điểm arrival (theo Poisson trong trace).
            target = item.arrival / args.speed
            while True:
                elapsed = time.perf_counter() - t_start
                if elapsed >= target:
                    break
                await asyncio.sleep(min(0.005, target - elapsed))

            messages = build_messages(convs_state, item)
            max_tokens = item.out_tokens or args.default_max_tokens

            async def _job(msgs=messages, mt=max_tokens, it=item):
                r = await _stream_one(session, args.base_url, args.model,
                                      msgs, mt, args.timeout, it)
                results.append(r)

            tasks.append(asyncio.create_task(_job()))

        await asyncio.gather(*tasks)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", default="bench/trace_grading_public.jsonl")
    ap.add_argument("--base-url", default="http://localhost:8000/v1")
    ap.add_argument("--model", default="LFM2.5-1.2B-Instruct")
    ap.add_argument("--timeout", type=float, default=30.0, help="timeout/request (s)")
    ap.add_argument("--speed", type=float, default=1.0,
                    help=">1 tua nhanh arrival; 1.0 = thời gian thật")
    ap.add_argument("--default-max-tokens", type=int, default=200)
    ap.add_argument("--out", default=None, help="đường dẫn lưu kết quả JSON")
    ap.add_argument("--name", default="run", help="tên cấu hình (ghi vào kết quả)")
    args = ap.parse_args()

    results = asyncio.run(run(args))
    stats = summarize(results)

    print("\n===== KẾT QUẢ ERS =====")
    print(f"cấu hình      : {args.name}")
    print(f"ERS           : {stats['ers']:.4f}")
    print(f"request chấm  : {stats['n_graded']}  (ok={stats.get('n_ok')}, fail={stats.get('n_fail')})")
    print(f"TTFT ms       : mean={stats.get('ttft_ms_mean'):.1f}  p50={stats.get('ttft_ms_p50'):.1f}  p95={stats.get('ttft_ms_p95'):.1f}")
    print(f"TPOT ms/token : mean={stats.get('tpot_ms_mean'):.2f}  p95={stats.get('tpot_ms_p95'):.2f}")

    fails = [r for r in results if not r.is_primer and not (r.ok and r.out_tokens > 0)]
    if fails:
        print(f"\n⚠️  {len(fails)} request FAIL (mỗi cái = 0 điểm). Ví dụ:")
        for r in fails[:5]:
            print(f"   {r.conv_id} turn{r.turn}: {r.error}")

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({
                "name": args.name,
                "model": args.model,
                "base_url": args.base_url,
                "speed": args.speed,
                "stats": stats,
                "requests": [vars(r) for r in results],
            }, f, ensure_ascii=False, indent=2)
        print(f"\n[saved] {args.out}")


if __name__ == "__main__":
    main()
