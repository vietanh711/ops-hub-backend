# main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from pydantic import BaseModel
from typing import Optional

# 1. Khởi tạo ứng dụng và Database
app = FastAPI(title="Internal Ops Hub API")
db = Prisma()

# Cấu hình CORS để Frontend (React) có thể gọi được API mà không bị chặn
# Cấu hình CORS chuẩn để Frontend gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "https://opshub-frontend-webapp-ercrgfa9czbfbpd5.japaneast-01.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối DB khi server khởi động
@app.on_event("startup")
async def startup():
    await db.connect()

# Ngắt kết nối khi tắt server
@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# ==========================================
# 2. Định nghĩa Pydantic Models (Kiểm tra dữ liệu đầu vào)
# ==========================================

# Model cho Knowledge Base
class KnowledgeDocCreate(BaseModel):
    title: str
    category: str
    content: str

# Model cho Training & QA
class TrainingQACreate(BaseModel):
    question: str
    answer: str
    tags: list[str] = []
    
class HandoverCreate(BaseModel):
    assignee: str
    issue_title: str
    handover_note: Optional[str] = None

class HandoverUpdate(BaseModel):
    status: str
    handover_note: Optional[str] = None

class UserSync(BaseModel):
    email: str
    name: str

class TaskCreate(BaseModel):
    assignee_email: str
    content: str
    
# Lấy danh sách tài liệu
@app.get("/api/knowledge")
async def get_knowledge_docs():
    records = await db.knowledgedoc.find_many(
        order={"updated_at": "desc"}
    )
    return records

# Thêm tài liệu mới
@app.post("/api/knowledge")
async def create_knowledge_doc(doc: KnowledgeDocCreate):
    record = await db.knowledgedoc.create(
        data={
            "title": doc.title,
            "category": doc.category,
            "content": doc.content
        }
    )
    return record

# ==========================================
# 5. API Routes cho Module Training & QA
# ==========================================

# Lấy danh sách Q&A
@app.get("/api/training")
async def get_training_qa():
    records = await db.trainingqa.find_many()
    return records

# Thêm câu hỏi Q&A mới
@app.post("/api/training")
async def create_training_qa(qa: TrainingQACreate):
    record = await db.trainingqa.create(
        data={
            "question": qa.question,
            "answer": qa.answer,
            "tags": qa.tags
        }
    )
    return record

# Lấy danh sách toàn bộ ca trực và công việc bàn giao
@app.get("/api/handovers")
async def get_handovers():
    # Sắp xếp công việc mới nhất lên đầu
    records = await db.shifthandover.find_many(
        order={"shift_date": "desc"}
    )
    return records

# Tạo một ghi chú giao ca mới
@app.post("/api/handovers")
async def create_handover(handover: HandoverCreate):
    record = await db.shifthandover.create(
        data={
            "assignee": handover.assignee,
            "issue_title": handover.issue_title,
            "handover_note": handover.handover_note,
            "status": "Pending" # Mặc định công việc mới sẽ là Pending
        }
    )
    return record

# Cập nhật trạng thái công việc (Ví dụ: Ca sau vào fix xong thì đổi thành Resolved)
@app.put("/api/handovers/{id}")
async def update_handover(id: str, handover: HandoverUpdate):
    try:
        record = await db.shifthandover.update(
            where={"id": id},
            data={
                "status": handover.status,
                "handover_note": handover.handover_note
            }
        )
        return record
    except Exception as e:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")
    
    # --- Bổ sung cho Module Knowledge Base ---

@app.put("/api/knowledge/{doc_id}")
async def update_knowledge_doc(doc_id: str, doc: KnowledgeDocCreate):
    record = await db.knowledgedoc.update(
        where={"id": doc_id},
        data={
            "title": doc.title,
            "category": doc.category,
            "content": doc.content
        }
    )
    return record

@app.delete("/api/knowledge/{doc_id}")
async def delete_knowledge_doc(doc_id: str):
    record = await db.knowledgedoc.delete(
        where={"id": doc_id}
    )
    return record

# --- Bổ sung cho Module Training & QA ---

@app.put("/api/training/{qa_id}")
async def update_training_qa(qa_id: str, qa: TrainingQACreate):
    record = await db.trainingqa.update(
        where={"id": qa_id},
        data={
            "question": qa.question,
            "answer": qa.answer,
            "tags": qa.tags
        }
    )
    return record

@app.delete("/api/training/{qa_id}")
async def delete_training_qa(qa_id: str):
    record = await db.trainingqa.delete(
        where={"id": qa_id}
    )
    return record

# 1. Đồng bộ User khi đăng nhập Microsoft
@app.post("/api/auth/sync")
async def sync_microsoft_user(user: UserSync):
    # Kiểm tra xem user đã có trong DB chưa
    existing_user = await db.user.find_unique(where={"email": user.email})
    if existing_user:
        return existing_user # Trả về info (kèm role) nếu đã tồn tại
    
    # Nếu là lần đầu đăng nhập, tạo tài khoản mới với role mặc định
    new_user = await db.user.create(
        data={
            "email": user.email,
            "name": user.name,
            "role": "member"
        }
    )
    return new_user

# 2. Lấy danh sách Member (cho Lead giao việc)
@app.get("/api/users")
async def get_all_users():
    # Thêm điều kiện lọc chỉ lấy những tài khoản có role là "member"
    return await db.user.find_many(
        where={
            "role": "member"
        },
        order={"name": "asc"}
    )

# 3. Lấy Checklist của một người
@app.get("/api/tasks/{user_email}")
async def get_my_tasks(user_email: str):
    return await db.task.find_many(where={"assignee_email": user_email})

# 4. Lead tạo Checklist mới
@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    record = await db.task.create(
        data={
            "assignee_email": task.assignee_email,
            "content": task.content
        }
    )
    return record

# 5. Member tick hoàn thành -> Xóa task
@app.delete("/api/tasks/{task_id}")
async def complete_task(task_id: str):
    await db.task.delete(where={"id": task_id})
    return {"status": "success"}