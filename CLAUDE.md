# CLAUDE.md — LLM Inference Optimization Challenge (Phase 1)

> File này là "bộ nhớ đề bài". Đọc file này trước mọi thao tác để hiểu nhanh & đúng mục tiêu.
> Ngôn ngữ làm việc: tiếng Việt (thuật ngữ kỹ thuật giữ nguyên tiếng Anh).
> ⚠️ **Luật thực thi khi làm việc:** xem [RULES.md](RULES.md) — đọc kèm file này.

---

## ★ Quy trình phiên bản (versions/) — LUÔN TỰ ĐỘNG THEO, KHÔNG CẦN NHẮC LẠI

Giữ **tất cả phiên bản** dưới `versions/partN/`. Mỗi lần nộp = một `part`.

**Cấu trúc mỗi part:**
```
versions/partN/
├── SUMMARY.md   # logic + các file đã làm/đổi ở phiên bản này, cấu hình vLLM, giả thuyết
├── files/       # snapshot file dùng để nộp (partN=1: full; partN≥2: chỉ file THAY ĐỔI mới)
└── score.md     # điểm (ERS/Δ/Score/p95...) — điền khi user gửi điểm
```
- **part1** = toàn bộ logic/file baseline hiện tại (đã tạo).
- **partN (N≥2)** = chỉ các **file thay đổi mới** để nộp lần đó.

**KHI USER GỬI ĐIỂM (một con số ERS / Score / Δ…) → tự động làm các bước sau, KHÔNG hỏi lại:**
1. Xác định part đang chờ điểm (part mới nhất chưa có score) → ghi điểm vào `versions/partN/score.md`.
2. **So sánh** với các part trước: lập bảng ERS / Δ / Score / p95 TTFT / TPOT qua các part; nêu rõ cái gì cải thiện, cái gì tệ đi, vì sao.
3. Cập nhật `notes/submissions.md` (mapping tag ↔ config ↔ ERS ↔ Δ).
4. **Đề xuất thay đổi** cho part kế tiếp dựa trên dữ liệu (đòn bẩy ROI cao nhất còn lại, xem RULES.md R2.5).
5. Tạo `versions/part(N+1)/` gồm `SUMMARY.md` (mô tả thay đổi + giả thuyết) và `files/` (chỉ file đổi mới). Cập nhật `score.md` placeholder chờ điểm lần sau.
6. Nhắc bạn tag image mới (`sub-0N`) + đổi `image:` trong docker-compose để nộp.

→ Tóm lại: **bạn chỉ cần gửi điểm; tôi tự ghi nhận, so sánh, và chuẩn bị part kế tiếp.**

---

## 0. TL;DR (đọc cái này trước)

- **Mục tiêu số 1 (vòng online):** tối đa hóa **ERS** (điểm tốc độ, dựa trên TTFT + TPOT). Đây là thứ leaderboard chấm mỗi lần nộp.
- **Ràng buộc số 1 (sau online):** giữ **accuracy** không tụt quá `Δ ≤ 0.10` so với baseline BF16, nếu không sẽ bị phạt điểm (`f(Δ)`), tụt `Δ ≥ 0.16` → 0 điểm.
- **Framework bắt buộc:** chỉ được dùng **vLLM**. Không được đổi framework khác.
- **Hardware chấm:** 1 MiG H200 slice — **18GB VRAM, 3 CPU core, 8GB RAM**. Nhỏ → phải tiết kiệm bộ nhớ.
- **Model:** `LiquidAI/LFM2.5-1.2B-Instruct` (nhỏ, 1.2B). Bottleneck thực tế nghiêng về **latency/scheduling**, không phải throughput thô.
- **Nộp bài:** đóng gói Docker image → push public lên Docker Hub → nộp `docker-compose.yml` lên Portal BTC.
- **Điểm cuối:** `Score = 100 × ERS × f(Δ)`. Điểm đội = Score tốt nhất trong ≤ 5 bài tự chọn còn hợp lệ.

Công thức cần luôn nhớ khi tinh chỉnh: **ERS là hàm bậc 2 (γ=2)** của mức độ "nhanh". Cải thiện latency ở vùng gần floor cho điểm cận biên rất lớn.

---

## 1. Nhiệm vụ & Workload

Triển khai + tối ưu một **LLM inference server** cho `LFM2.5-1.2B-Instruct`, xử lý một **trace multi-turn** mô phỏng traffic production.

Đặc điểm workload:
- **70 hội thoại** đến theo phân phối **Poisson**.
- Tổng **330 request được chấm** (sau **15 hội thoại primer** warmup — không tính điểm).
- **Context input tối đa ~4k token (~12k ký tự)**.
- **Output tối đa 200 token**.
- Multi-turn → có **prefix chung giữa các turn** → **prefix caching cực kỳ có giá trị**.

BTC benchmark **trực tiếp** vào endpoint của thí sinh (OpenAI-compatible API, port 8000).

### Trace công khai
- File: `trace_grading_public.jsonl` (bản đã lược prompt — chỉ có `arrival` + số token in/out mỗi lượt).
- BTC giữ bản đầy đủ có prompt thật để chấm. → **Không được** dựa vào nội dung prompt cụ thể; chỉ dùng trace để mô phỏng timing/tải khi tự benchmark.

---

## 2. Hạ tầng & Môi trường chấm

| Thành phần | Giá trị |
|---|---|
| GPU | 1 instance MiG **H200** (**18GB VRAM**) |
| CPU | **3 core** |
| RAM | **8GB** |
| OS (host) | Ubuntu 24.04 LTS |
| Driver | NVIDIA 590.x (CUDA 13.x) |
| Model | `LiquidAI/LFM2.5-1.2B-Instruct` (weights: https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct) |

⚠️ **Ràng buộc bộ nhớ chặt:** 8GB RAM host + 18GB VRAM. CPU offloading bị giới hạn bởi RAM nhỏ. `shm_size` mặc định mẫu là `2g`.

---

## 3. Cách tính điểm (chi tiết)

### 3.1 ERS (vòng online)
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

### 3.2 Accuracy Gate (sau online, GPQA full)
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
- Chỉ chạy trên ≤ 5 submissions đội tự chọn sau vòng online (dùng `lm_eval` / `bench-gpqa-diamond.sh`).

### 3.3 Điểm cuối
```
Score = 100 × ERS × f(Δ)
```
Điểm đội = Score tốt nhất trong các bài còn hợp lệ.

---

## 4. Không gian tối ưu (chỉ dùng vLLM)

Các hướng được phép/khuyến khích:

1. **Quantization** — Online Quantization (vd FP8 weights/activations). Đánh đổi với ngân sách `Δ ≤ 0.10`.
2. **KV Cache & Memory** — Paged Attention; KV cache quant (FP8/INT8); **Prefix caching** (rất quan trọng vì multi-turn); Semantic caching; Offloading CPU/NVMe (cẩn thận RAM 8GB).
3. **Serving & Scheduling** — Continuous/Dynamic batching; **Speculative decoding**; Memory-aware scheduling.
4. **System & Runtime** — Custom CUDA/Triton kernels; Fused attention (FlashAttention / FlashInfer); Memory layout; **CUDA Graphs**.

**Ưu tiên đề xuất (heuristic ban đầu, cần benchmark xác nhận):**
- Bật `--enable-prefix-caching` (multi-turn → hit rate cao → giảm TTFT mạnh).
- Bật CUDA Graphs (giảm TTFT overhead cho batch nhỏ).
- Model chỉ 1.2B → thử FP8 online quant để tăng tốc decode (kiểm accuracy Δ).
- Speculative decoding: cân nhắc — có thể giảm TPOT nếu draft tốt, nhưng thêm rủi ro & bộ nhớ.
- `max-model-len` chỉ cần ~4k+200; **không cần 32768** như mẫu → giảm để tiết kiệm KV cache & tăng concurrency.

---

## 5. Quy trình nộp bài

1. **Develop & Package** — code giải pháp + tối ưu → đóng gói thành **1 Docker Image**.
2. **Push Image** — đẩy lên Docker Hub cá nhân/tổ chức, để **Public**.
3. **Submit** — nộp `docker-compose.yml` (khai báo chính xác đường dẫn image + lệnh chạy) lên Portal BTC.
4. **Automated Evaluation** — hệ thống pull image → dựng container trên MiG H200 → healthcheck → chạy benchmark ERS (KHÔNG chạy GPQA mỗi lượt).
5. **Leaderboard** — cập nhật theo ERS.
6. **Sau online** — chọn ≤ 5 submissions → BTC hậu kiểm hợp lệ → chạy GPQA full → chốt Score.

### Baseline image
`vllm/vllm-openai:v0.22.1`

### docker-compose.yml mẫu (BTC cung cấp)
Các dòng có comment `#Don't change this to vllm-server` **phải giữ nguyên entrypoint/command dạng module** (`python3 -m vllm.entrypoints.openai.api_server`), không đổi sang lệnh `vllm-server`.

```yaml
services:
  model:
    image: vllm/vllm-openai:v0.22.1
    entrypoint:
      - python3                                    #Don't change this to vllm-server
      - -m                                         #Don't change this to vllm-server
      - vllm.entrypoints.openai.api_server         #Don't change this to vllm-server
    command:
      - --model=/model                             #Don't change this to vllm-server
      - --served-model-name=LFM2.5-1.2B-Instruct   #Don't change this to vllm-server
      - --host=0.0.0.0                             #Don't change this to vllm-server
      - --port=8000                                #Don't change this to vllm-server
      - --max-model-len=32768
      - --gpu-memory-utilization=0.95
      - --tensor-parallel-size=1
      - --enable-prefix-caching
    ports:
      - "8000:8000"
    shm_size: "2g"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Lưu ý cấu hình để tối ưu (so với mẫu):**
- `--served-model-name=LFM2.5-1.2B-Instruct` — giữ nguyên tên này (BTC gọi endpoint theo tên).
- `--model=/model` — weights nằm ở path `/model` trong container.
- `--max-model-len` có thể giảm mạnh (~4300) để tiết kiệm KV cache.
- `--gpu-memory-utilization` có thể đẩy cao (nhưng chừa VRAM cho CUDA graph/activation).
- `--port=8000`, `--host=0.0.0.0` — giữ nguyên.

---

## 6. Anti-cheating — CÁC HÀNH VI BỊ NGHIÊM CẤM

Vi phạm → BTC hủy kết quả. Tuyệt đối tránh:

- ❌ **Pre-bake / hardcode kết quả**; cơ chế **dual-path** (chạy khác nhau lúc bench vs lúc thật); gaming phương pháp đo.
- ❌ **Gọi mạng ra ngoài** (external network calls) trong lúc serve.
- ❌ **Can thiệp trái phép** vào tokenizer hoặc weights của model.
- ❌ **Tráo Docker image** sau khi đã nộp.

**Yêu cầu cốt lõi:** phải serve LLM **trung thực** trên GPU BTC cấp. Quantization / KV cache optimization là hợp lệ; hardcode / cache đáp án là gian lận.

---

## 7. Tie-break & Khiếu nại

Khi điểm sát nhau (≤ 1–2 điểm, trong biên nhiễu), xếp hạng theo thứ tự:
1. Mức độ suy giảm accuracy (Δ nhỏ hơn thắng).
2. **p95 TTFT** thấp hơn.
3. Tốc độ sinh văn bản (TPOT) nhanh hơn.
4. Thời điểm nộp sớm hơn.

→ **Hệ quả tối ưu:** đừng chỉ tối ưu mean; **p95 TTFT** cũng là tiêu chí phụ → cần giảm tail latency (tránh queueing spikes).

Khiếu nại: trong 24h kể từ email thông báo kết quả dự kiến. BTC có quyền chấm lại lấy trung vị nhiều lần chạy.

---

## 8. Quy ước thư mục (folder rules)

> Cập nhật mục này khi cấu trúc project đổi. Trạng thái hiện tại: **khung code đã dựng xong.**

```
LLM-otp/
├── CLAUDE.md                 # đề bài & quy định
├── RULES.md                  # luật thực thi khi làm việc (R1–R7)
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
└── versions/                 # LƯU MỌI PHIÊN BẢN (xem "★ Quy trình phiên bản")
    ├── part1/{SUMMARY.md, files/, score.md}
    └── part2/...             # tạo dần mỗi lần nộp
```

**Quy trình chuẩn (end-to-end):**
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

**Nguyên tắc làm việc:**
- Mọi thay đổi cấu hình phải **đo ERS cục bộ** trước khi nộp (mô phỏng trace + tính TTFT/TPOT theo đúng công thức mục 3).
- Mỗi cấu hình đáng cân nhắc → lưu số liệu vào `bench/results/` để so sánh.
- Trước khi chốt bài nộp: kiểm accuracy để đảm bảo `Δ ≤ 0.10` (an toàn) hoặc ít nhất `< 0.16`.
- Không hardcode, không dual-path, không network calls (mục 6).
- Giữ nguyên các dòng `#Don't change this to vllm-server` trong docker-compose.

---

## 9. Checklist trước khi nộp mỗi submission

- [ ] Container khởi động & healthcheck pass trên cấu hình gần giống MiG (18GB VRAM).
- [ ] Endpoint OpenAI-compatible tại `:8000`, `served-model-name=LFM2.5-1.2B-Instruct`.
- [ ] Không có request nào timeout / trả 0 token dưới tải trace (mọi fail = 0 điểm).
- [ ] Đã đo ERS cục bộ, ghi lại số + cấu hình vào `bench/results/`.
- [ ] Không vi phạm anti-cheating (mục 6).
- [ ] Image đã push Public lên Docker Hub, tag cố định (không mutable `latest` mơ hồ).
- [ ] `docker-compose.yml` trỏ đúng image + tag đã push.
- [ ] (Trước khi chọn 5 bài cuối) đã kiểm Δ accuracy.
```
