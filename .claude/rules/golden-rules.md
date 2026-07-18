# Quy tắc VÀNG & Anti-cheating (KHÔNG BAO GIỜ VI PHẠM)

Vi phạm → BTC hủy kết quả. Nếu một thay đổi có nguy cơ chạm các luật này → **dừng lại, hỏi user trước** (xem [communication-and-done.md](communication-and-done.md) R6.4).

## Quy tắc VÀNG (R1)

| # | Luật | Vì sao |
|---|---|---|
| R1.1 | **Chỉ dùng vLLM.** Không thay framework (TGI, TensorRT-LLM, SGLang...). | Quy định đề bài. |
| R1.2 | **Không hardcode / pre-bake / dual-path / cache đáp án.** | Anti-cheating → hủy kết quả. |
| R1.3 | **Không network call ra ngoài** trong lúc serve. Weights phải nằm sẵn trong image. | Anti-cheating + môi trường chấm có thể không có internet. |
| R1.4 | **Không sửa tokenizer/weights trái phép.** Quantization hợp lệ; đổi nội dung thì không. | Anti-cheating. |
| R1.5 | **Không tráo image sau khi nộp.** Mỗi submission = 1 tag cố định, immutable. | Anti-cheating. |
| R1.6 | Giữ nguyên các dòng `#Don't change this to vllm-server` trong docker-compose (entrypoint dạng `python3 -m ...`). | Ràng buộc BTC. |
| R1.7 | Giữ `--served-model-name=LFM2.5-1.2B-Instruct`, `--host=0.0.0.0`, `--port=8000`. | BTC gọi endpoint theo đúng tên/cổng. |

## Các hành vi bị NGHIÊM CẤM (chi tiết)

Tuyệt đối tránh:
- ❌ **Pre-bake / hardcode kết quả**; cơ chế **dual-path** (chạy khác nhau lúc bench vs lúc thật); gaming phương pháp đo.
- ❌ **Gọi mạng ra ngoài** (external network calls) trong lúc serve.
- ❌ **Can thiệp trái phép** vào tokenizer hoặc weights của model.
- ❌ **Tráo Docker image** sau khi đã nộp.

**Yêu cầu cốt lõi:** phải serve LLM **trung thực** trên GPU BTC cấp. Quantization / KV cache optimization là hợp lệ; hardcode / cache đáp án là gian lận.
