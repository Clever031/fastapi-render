from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

user_name = quote_plus('Watcharasak')
pw = quote_plus('clever_1234')

uri = f'mongodb+srv://{user_name}:{pw}@cluster0.utow1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = AsyncIOMotorClient(uri)
db = client['regist']  
collection = db['new_students']  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    apply: int
    department: str
    level: str
    plan: int
    save_data: datetime  

@app.get('/students')
async def get_students():
    std = await collection.find().to_list(100)
    for s in std:
        s['_id'] = str(s['_id'])
    return std

@app.post('/students')
async def create_student(student: Student):
    student_dict = student.dict()
    new_student = await collection.insert_one(student_dict)
    return {"message": "Student added", "id": str(new_student.inserted_id)}

from bson import ObjectId

@app.put('/students/{student_id}')
async def update_student(student_id: str, student: Student):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(status_code=400, detail="Invalid student_id format")

    student_oid = ObjectId(student_id)  
    existing_student = await collection.find_one({"_id": student_oid})

    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    updated_data = {key: value for key, value in student.dict().items() if value is not None}

    await collection.update_one({"_id": student_oid}, {"$set": updated_data})

    return {"message": "Student updated successfully"}

@app.delete('/students/{student_id}')
async def delete_student(student_id: str):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(status_code=400, detail="Invalid student_id format")

    student_oid = ObjectId(student_id)  
    delete_result = await collection.delete_one({"_id": student_oid})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}

