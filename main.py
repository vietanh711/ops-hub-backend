
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prisma import Prisma
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Internal Ops Hub API")
db = Prisma()

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

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


class KnowledgeDocCreate(BaseModel):
    title: str
    category: str
    content: str

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
    
@app.get("/api/knowledge")
async def get_knowledge_docs():
    records = await db.knowledgedoc.find_many(
        order={"updated_at": "desc"}
    )
    return records

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


@app.get("/api/training")
async def get_training_qa():
    records = await db.trainingqa.find_many()
    return records

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

@app.get("/api/handovers")
async def get_handovers():
    records = await db.shifthandover.find_many(
        order={"shift_date": "desc"}
    )
    return records

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

@app.post("/api/auth/sync")
async def sync_microsoft_user(user: UserSync):
    existing_user = await db.user.find_unique(where={"email": user.email})
    if existing_user:
        return existing_user # Trả về info (kèm role) nếu đã tồn tại
    
    new_user = await db.user.create(
        data={
            "email": user.email,
            "name": user.name,
            "role": "member"
        }
    )
    return new_user

@app.get("/api/users")
async def get_all_users():
    return await db.user.find_many(
        where={
            "role": "member"
        },
        order={"name": "asc"}
    )

@app.get("/api/tasks/{user_email}")
async def get_my_tasks(user_email: str):
    return await db.task.find_many(where={"assignee_email": user_email})

@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    record = await db.task.create(
        data={
            "assignee_email": task.assignee_email,
            "content": task.content
        }
    )
    return record

@app.delete("/api/tasks/{task_id}")
async def complete_task(task_id: str):
    await db.task.delete(where={"id": task_id})
    return {"status": "success"}