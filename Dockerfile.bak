# Dùng môi trường Python gọn nhẹ
FROM python:3.10-slim

# Chuyển thư mục làm việc vào /app
WORKDIR /app

# BỔ SUNG: Cài đặt thư viện lõi hệ thống mà Prisma yêu cầu
RUN apt-get update && apt-get install -y libatomic1

# Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Prisma schema và khởi tạo client
COPY schema.prisma .
RUN prisma generate

# Copy toàn bộ code còn lại
COPY . .

EXPOSE 80

# Chạy server FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]