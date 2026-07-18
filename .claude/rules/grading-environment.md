# Hạ tầng & Môi trường chấm

| Thành phần | Giá trị |
|---|---|
| GPU | 1 instance MiG **H200** (**18GB VRAM**) |
| CPU | **3 core** |
| RAM | **8GB** |
| OS (host) | Ubuntu 24.04 LTS |
| Driver | NVIDIA 590.x (CUDA 13.x) |
| Model | `LiquidAI/LFM2.5-1.2B-Instruct` (weights: https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct) |

⚠️ **Ràng buộc bộ nhớ chặt:** 8GB RAM host + 18GB VRAM. CPU offloading bị giới hạn bởi RAM nhỏ. `shm_size` mặc định mẫu là `2g`.

→ Test ở mức tài nguyên tương đương; cẩn thận CPU/NVMe offloading vì RAM chỉ 8GB (xem [optimization-discipline.md](optimization-discipline.md) R2.7).
