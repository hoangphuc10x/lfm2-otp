# Rebuild NHANH: chỉ thêm file config lên image sub-01 đã có (không tải lại weights).
# Dùng khi chỉ đổi vllm_config.yaml.
#
#   docker build -f Dockerfile.spec -t hoangphuc109/lfm2-otp:sub-03 .
#   docker push hoangphuc109/lfm2-otp:sub-03
#
FROM hoangphuc109/lfm2-otp:sub-01
COPY vllm_config.yaml /vllm_config.yaml
