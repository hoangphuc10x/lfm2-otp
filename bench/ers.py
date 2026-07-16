"""
Tính điểm ERS đúng theo công thức đề bài (xem CLAUDE.md mục 3).

    ERS = (1/N) * sum(S_request)                              in [0, 1]

    S_request = 0                          nếu lỗi / timeout / trả về 0 token
              = w*s_ttft + (1-w)*s_tpot    nếu thành công

    s_ttft = clamp((C_ttft - TTFT)/(C_ttft - F_ttft), 0, 1) ** gamma
    s_tpot = clamp((C_tpot - TPOT )/(C_tpot - F_tpot), 0, 1) ** gamma

Đơn vị thời gian dùng nội bộ: MILLISECOND (ms).
    - TTFT: thời gian tới token đầu tiên (ms).
    - TPOT_mean: trung bình thời gian giữa các token (ms/token).
"""
from __future__ import annotations

from dataclasses import dataclass

# --- Tham số chấm điểm cố định của BTC (KHÔNG tự đổi — xem RULES.md R3.2) ---
F_TTFT = 10.0    # ms  -> điểm tối đa khi TTFT <= 10ms
C_TTFT = 400.0   # ms  -> điểm 0 khi TTFT >= 400ms
F_TPOT = 1.0     # ms/token -> điểm tối đa khi TPOT <= 1ms (1000 tok/s)
C_TPOT = 10.0    # ms/token -> điểm 0 khi TPOT >= 10ms (100 tok/s)
GAMMA = 2.0
W_TTFT = 0.5


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def s_ttft(ttft_ms: float) -> float:
    x = _clamp((C_TTFT - ttft_ms) / (C_TTFT - F_TTFT))
    return x ** GAMMA


def s_tpot(tpot_ms: float) -> float:
    x = _clamp((C_TPOT - tpot_ms) / (C_TPOT - F_TPOT))
    return x ** GAMMA


def request_score(ttft_ms: float, tpot_ms: float, ok: bool, out_tokens: int) -> float:
    """Điểm 1 request. Lỗi / timeout / 0 token => 0 (RULES.md R2.2)."""
    if (not ok) or out_tokens <= 0:
        return 0.0
    return W_TTFT * s_ttft(ttft_ms) + (1.0 - W_TTFT) * s_tpot(tpot_ms)


@dataclass
class RequestResult:
    """Kết quả đo 1 request. Set ok=False nếu lỗi/timeout."""
    conv_id: str
    turn: int
    ttft_ms: float
    tpot_ms: float
    out_tokens: int
    ok: bool = True
    is_primer: bool = False          # request warmup -> không tính điểm
    error: str | None = None

    @property
    def score(self) -> float:
        return request_score(self.ttft_ms, self.tpot_ms, self.ok, self.out_tokens)


def _pct(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def summarize(results: list[RequestResult]) -> dict:
    """Tính ERS + các chỉ số phụ trên các request ĐƯỢC CHẤM (bỏ primer)."""
    graded = [r for r in results if not r.is_primer]
    n = len(graded)
    if n == 0:
        return {"ers": 0.0, "n_graded": 0, "note": "không có request được chấm"}

    scores = [r.score for r in graded]
    ok = [r for r in graded if r.ok and r.out_tokens > 0]
    fails = [r for r in graded if not (r.ok and r.out_tokens > 0)]
    ttfts = [r.ttft_ms for r in ok]
    tpots = [r.tpot_ms for r in ok]

    return {
        "ers": sum(scores) / n,
        "n_graded": n,
        "n_ok": len(ok),
        "n_fail": len(fails),
        "ttft_ms_mean": sum(ttfts) / len(ttfts) if ttfts else float("nan"),
        "ttft_ms_p50": _pct(ttfts, 0.50),
        "ttft_ms_p95": _pct(ttfts, 0.95),   # tie-break (RULES.md R2.3)
        "tpot_ms_mean": sum(tpots) / len(tpots) if tpots else float("nan"),
        "tpot_ms_p95": _pct(tpots, 0.95),
        "n_primer_skipped": len(results) - n,
    }
