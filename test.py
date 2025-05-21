import time

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import db
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Schedule API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    max_retries = 5
    retry_delay = 2

    for i in range(max_retries):
        try:
            db.init_db()
            # Пробное обращение к методу
            db.get_classrooms()
            print("Database initialized successfully.")
            break
        except Exception as e:
            print(f"Database connection failed (attempt {i + 1}): {e}")
            if i == max_retries - 1:
                raise Exception(f"Failed to connect to database after {max_retries} attempts")
            time.sleep(retry_delay)

@app.get("/")
async def root():
    return {"message": "API is working"}

@app.get("/classrooms")
async def get_classrooms():
    return db.get_classrooms()

@app.get("/groups")
async def get_groups():
    return db.get_groups()

@app.get("/teachers")
async def get_teachers():
    return db.get_teachers()

@app.get("/schedule/group/{group_name}")
async def get_group_schedule(group_name: str):
    schedule = db.get_schedule_from_group(group_name)
    if not schedule:
        raise HTTPException(status_code=404, detail="Group not found")
    return schedule

@app.get("/schedule/classroom/{classroom_name}")
async def get_classroom_schedule(classroom_name: str):
    schedule = db.get_schedule_from_classroom(classroom_name)
    if not schedule:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return schedule

@app.get("/schedule/teacher/{teacher_name}")
async def get_teacher_schedule(teacher_name: str):
    schedule = db.get_schedule_from_teacher(teacher_name)
    if not schedule:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return schedule


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000)

