# Cách tính điểm (chi tiết)

## ERS (vòng online)
```
ERS = (1/N) Σ S_request,i  ∈ [0, 1]
```
Với mỗi request:
```
S_request = 0                                 nếu lỗi / timeout / trả về 0 token
S_request = w·s_ttft + (1-w)·s_tpot           nếu thành công
```
```
s_ttft = [ clamp( (C_ttft - TTFT)      / (C_ttft - F_ttft), 0, 1 ) ]^γ
s_tpot = [ clamp( (C_tpot - TPOT_mean) / (C_tpot - F_tpot), 0, 1 ) ]^γ
```

**Tham số cấu hình:**

| Ký hiệu | Ý nghĩa | Giá trị |
|---|---|---|
| `F_ttft` | Floor TTFT | **10 ms** |
| `C_ttft` | Ceiling TTFT | **400 ms** |
| `F_tpot` | Floor TPOT | **1 ms** |
| `C_tpot` | Ceiling TPOT | **10 ms** |
| `γ` (gamma) | Hệ số lũy thừa | **2** |
| `w` | Trọng số TTFT | **0.5** |

**Ý nghĩa thực tế để tối ưu:**
- TTFT và TPOT **trọng số bằng nhau** (0.5 / 0.5).
- **TTFT:** đạt điểm tối đa khi ≤ 10ms, 0 điểm khi ≥ 400ms.
- **TPOT (mean):** đạt điểm tối đa khi ≤ 1ms/token, 0 điểm khi ≥ 10ms/token. → **Rất khắt khe.** 10ms/token = 100 tok/s; 1ms/token = 1000 tok/s. Phải đẩy tốc độ decode càng cao càng tốt.
- **γ=2** → hàm cong: mỗi ms cải thiện ở vùng nhanh có lãi kép. Ưu tiên đẩy sâu về floor.
- **Timeout / 0 token / lỗi = 0 điểm** cho request đó → **độ ổn định quan trọng**; không được đánh đổi để một số request fail.

## Accuracy Gate (sau online, GPQA full)
```
Δ = Accuracy_baseline - Accuracy_submission
```
```
f(Δ) = 1.0                        nếu Δ ≤ 0.10
f(Δ) = 1.0 - (Δ - 0.10)/0.06      nếu 0.10 < Δ < 0.16
f(Δ) = 0.0                        nếu Δ ≥ 0.16
```
- Baseline BF16 (mặc định 0.4).
- **Vùng an toàn tuyệt đối: Δ ≤ 0.10.** Đây là ngân sách chất lượng để đánh đổi lấy tốc độ (vd quantization).
- Chỉ chạy trên ≤ 5 submissions đội tự chọn sau vòng online (dùng `lm_eval` / `eval/bench-gpqa-diamond.sh`).

## Điểm cuối
```
Score = 100 × ERS × f(Δ)
```
Điểm đội = Score tốt nhất trong các bài còn hợp lệ.
