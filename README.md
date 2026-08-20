# Ops Hub Backend

Backend API của hệ thống **Internal Ops Hub**, được xây dựng bằng FastAPI, Prisma và MongoDB, cung cấp các dịch vụ cho ứng dụng quản trị nội bộ của Operation Team.

Backend chịu trách nhiệm xử lý dữ liệu và nghiệp vụ cho các chức năng quản lý ca trực, bàn giao sự cố, kho kiến thức, đào tạo nội bộ, task cá nhân và đồng bộ người dùng.

## Tính năng chính

* **Quản lý ca trực và bàn giao:** lưu trữ và cập nhật thông tin sự cố, công việc và trạng thái xử lý.
* **Quản lý kho kiến thức:** tạo, cập nhật, tra cứu và xóa tài liệu nghiệp vụ.
* **Đào tạo và hỏi đáp:** quản lý bộ câu hỏi, đáp án và các tag kiến thức.
* **Quản lý người dùng:** đồng bộ thông tin người dùng từ Microsoft và phân quyền theo vai trò.
* **Quản lý task:** tạo và theo dõi checklist công việc theo từng thành viên.
* **REST API:** cung cấp API cho frontend Internal Ops Hub.

## Công nghệ sử dụng

* Python
* FastAPI
* Uvicorn
* Prisma
* MongoDB
* Pydantic
* Docker

## Kiến trúc tổng quan

```text
Frontend React
      ↓
   REST API
      ↓
FastAPI Backend
      ↓
   Prisma
      ↓
   MongoDB
```

Backend được thiết kế tách biệt với frontend và chịu trách nhiệm xử lý nghiệp vụ, xác thực dữ liệu và giao tiếp với cơ sở dữ liệu.

## Cấu trúc project

```text
ops-backend/
├── .github/
│   └── workflows/
│       └── backend-cicd.yml
├── main.py
├── schema.prisma
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Cấu hình môi trường

Tạo file `.env` dựa trên `.env.example` và cấu hình chuỗi kết nối MongoDB:

```env
DATABASE_URL="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>"
```

Các thông tin nhạy cảm không được commit vào repository.

## Chạy project local

### 1. Tạo môi trường Python

```bash
python -m venv .venv
```

Trên Windows:

```bash
.venv\Scripts\activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate Prisma Client

```bash
prisma generate
```

### 4. Khởi chạy backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Sau khi khởi chạy, API có thể được kiểm tra tại:

```text
http://localhost:8000
```

Swagger API:

```text
http://localhost:8000/docs
```

## Docker

Backend được đóng gói bằng Docker để phục vụ quá trình triển khai.

### Build image

```bash
docker build -t ops-backend .
```

### Chạy container

```bash
docker run -p 80:80 --env-file .env ops-backend
```

## CI/CD

Backend sử dụng **GitHub Actions** để tự động hóa quá trình build và phát hành Docker image.

Quy trình triển khai tổng quát:

```text
GitHub
   ↓
GitHub Actions
   ↓
Docker Image
   ↓
Azure Container Registry
   ↓
Azure App Service
```

Pipeline được cấu hình tại:

```text
.github/workflows/backend-cicd.yml
```

Khi mã nguồn được cập nhật, workflow thực hiện quá trình build image và push image lên Azure Container Registry.

## Database

Backend sử dụng **MongoDB** làm cơ sở dữ liệu và **Prisma** để quản lý schema và truy cập dữ liệu.

Các nhóm dữ liệu chính của hệ thống gồm:

* Người dùng
* Công việc
* Ca trực và bàn giao
* Tài liệu kiến thức
* Câu hỏi và đáp án đào tạo

## Trạng thái

Backend đã hoàn thiện các chức năng nghiệp vụ chính và được tích hợp với frontend Internal Ops Hub, đồng thời hỗ trợ đóng gói Docker và triển khai thông qua quy trình CI/CD trên Azure.
