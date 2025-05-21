import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import db
from fastapi.openapi.utils import get_openapi

api_db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    global api_db
    api_db = db.Database()

    # Проверка подключения к БД
    max_retries = 5
    retry_delay = 2

    for i in range(max_retries):
        try:
            api_db.get_classrooms()
            break
        except Exception as e:
            if i == max_retries - 1:
                raise Exception(f"Failed to connect to database after {max_retries} attempts")
            print(f"Database connection failed (attempt {i + 1}), retrying...")
            time.sleep(retry_delay)

    yield

    # Shutdown code
    if api_db:
        api_db.close()


app = FastAPI(
    title="Schedule API",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is working"}

@app.get("/classrooms")
async def get_classrooms():
    return api_db.get_classrooms()

@app.get("/groups")
async def get_groups():
    return api_db.get_groups()

@app.get("/teachers")
async def get_teachers():
    return api_db.get_teachers()

@app.get("/schedule/group/{group_name}")
async def get_group_schedule(group_name: str):
    schedule = api_db.get_schedule_from_group(group_name)
    if not schedule:
        raise HTTPException(status_code=404, detail="Group not found")
    return schedule

@app.get("/schedule/classroom/{classroom_name}")
async def get_classroom_schedule(classroom_name: str):
    schedule = api_db.get_schedule_from_classroom(classroom_name)
    if not schedule:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return schedule

@app.get("/schedule/teacher/{teacher_name}")
async def get_teacher_schedule(teacher_name: str):
    schedule = api_db.get_schedule_from_teacher(teacher_name)
    if not schedule:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return schedule


if __name__ == "__main__":
    import uvicorn
    api_db = db.Database()
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

