import os
from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from datetime import datetime
from bson import ObjectId
from typing import List
import cloudinary
import cloudinary.uploader

from database import test_db_connection, user_collection, pdf_collection, discussion_collection
from schemas import UserCreate, UserResponse, PDFResponse, DiscussionCreate, DiscussionResponse

app = FastAPI(title="طريق الهدى API")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@app.on_event("startup")
async def startup_db_client():
    print("Checking MongoDB connection...")
    await test_db_connection()


@app.get("/")
async def root():
    return {"message": "Welcome to the طريق الهدى API - Backend is running!"}


# ==========================================
# 1. User Authentication / Registration Route
# ==========================================
@app.post("/api/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    existing_user = await user_collection.find_one({"$or": [{"email": user.email}, {"username": user.username}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered."
        )

    hashed_pwd = hash_password(user.password)
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    user_doc = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_pwd,
        "joined_date": current_time
    }

    result = await user_collection.insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "username": user.username,
        "email": user.email,
        "joined_date": current_time
    }


# ==========================================
# 2. PDF Document & Cloudinary Routes
# ==========================================
@app.get("/api/pdfs", response_model=List[PDFResponse])
async def get_all_pdfs():
    pdfs = []
    cursor = pdf_collection.find({})
    async for document in cursor:
        pdfs.append({
            "id": str(document["_id"]),
            "title": document["title"],
            "description": document["description"],
            "upload_date": document["upload_date"],
            "cloudinary_url": document["cloudinary_url"],
            "public_id": document.get("public_id")
        })
    return pdfs


@app.get("/api/pdfs/{pdf_id}", response_model=PDFResponse)
async def get_single_pdf(pdf_id: str):
    if not ObjectId.is_valid(pdf_id):
        raise HTTPException(status_code=400, detail="Invalid PDF ID format.")
    
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)})
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")
    
    return {
        "id": str(document["_id"]),
        "title": document["title"],
        "description": document["description"],
        "upload_date": document["upload_date"],
        "cloudinary_url": document["cloudinary_url"],
        "public_id": document.get("public_id")
    }


@app.post("/api/admin/upload-pdf", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...)
):
    if not file or not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        contents = await file.read()
        upload_result = cloudinary.uploader.upload(
            contents,
            resource_type="auto",
            folder="tariq_al_huda_pdfs"
        )
        
        secure_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        current_date = datetime.utcnow().strftime("%Y-%m-%d")

        pdf_doc = {
            "title": title,
            "description": description,
            "upload_date": current_date,
            "cloudinary_url": secure_url,
            "public_id": public_id
        }

        result = await pdf_collection.insert_one(pdf_doc)

        return {
            "id": str(result.inserted_id),
            "title": title,
            "description": description,
            "upload_date": current_date,
            "cloudinary_url": secure_url,
            "public_id": public_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")


# ==========================================
# 3. Discussion & Comment Routes (ID-Linked)
# ==========================================
@app.get("/api/discussions/{pdf_id}", response_model=List[DiscussionResponse])
async def get_pdf_discussions(pdf_id: str):
    discussions = []
    cursor = discussion_collection.find({"pdf_id": pdf_id}).sort("timestamp", -1)
    async for doc in cursor:
        discussions.append({
            "id": str(doc["_id"]),
            "pdf_id": doc["pdf_id"],
            "user_id": doc.get("user_id"),
            "user_name": doc["user_name"],
            "message": doc["message"],
            "timestamp": doc["timestamp"]
        })
    return discussions


@app.post("/api/discussions", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def post_discussion(comment: DiscussionCreate, user_name: str = Form("Anonymous"), user_id: str = Form(None)):
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    comment_doc = {
        "pdf_id": comment.pdf_id,
        "user_id": user_id,
        "user_name": user_name,
        "message": comment.message,
        "timestamp": current_time
    }

    result = await discussion_collection.insert_one(comment_doc)

    return {
        "id": str(result.inserted_id),
        "pdf_id": comment.pdf_id,
        "user_id": user_id,
        "user_name": user_name,
        "message": comment.message,
        "timestamp": current_time
    }