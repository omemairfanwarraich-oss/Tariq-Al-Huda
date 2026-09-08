import os
from datetime import datetime, timedelta
from typing import Optional, List, Union
from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from bson import ObjectId
import cloudinary
import cloudinary.uploader
from cloudinary.utils import private_download_url
from urllib.request import urlopen

from database import test_db_connection, user_collection, pdf_collection, discussion_collection, faq_collection
from schemas import UserCreate, UserResponse, PDFResponse, DiscussionCreate, DiscussionResponse, UserLogin, Token, PasswordReset, FAQCreate, FAQResponse

app = FastAPI(title="طريق الهدى API")

# Resolve the root directory (Tariq Al-Huda) relative to backend/main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

# Mount static directories (CSS, JS, images, components)
app.mount("/assets", StaticFiles(directory=os.path.join(root_dir, "assets")), name="assets")
app.mount("/components", StaticFiles(directory=os.path.join(root_dir, "components")), name="components")

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

# JWT & Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_fallback_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_pdf_delivery_url(document: Optional[dict]) -> str:
    if not document:
        return ""
    public_id = document.get("public_id")
    if not public_id:
        return document.get("cloudinary_url", "")

    return private_download_url(
        public_id,
        format="pdf",
        resource_type=document.get("resource_type", "image"),
        type="upload",
        attachment=False
    )

def normalize_pdf_id(pdf_id: str) -> Union[ObjectId, int]:
    if pdf_id.isdigit():
        return int(pdf_id)
    if ObjectId.is_valid(pdf_id):
        return ObjectId(pdf_id)
    raise HTTPException(status_code=400, detail="Invalid document ID. Use a number or a 24-character hex ID.")

def pdf_query_id(pdf_id: str) -> dict:
    if pdf_id.isdigit():
        return {"document_id": int(pdf_id)}
    if ObjectId.is_valid(pdf_id):
        return {"_id": ObjectId(pdf_id)}
    raise HTTPException(status_code=400, detail="Invalid document ID.")

def serialize_pdf(document: Optional[dict]) -> dict:
    if not document:
        return {}
    return {
        "id": str(document.get("document_id", document.get("_id", ""))),
        "title": document.get("title", ""),
        "description": document.get("description", ""),
        "upload_date": document.get("upload_date", ""),
        "cloudinary_url": get_pdf_delivery_url(document),
        "public_id": document.get("public_id"),
        "file_name": document.get("file_name"),
        "sort_order": document.get("sort_order", 0)
    }

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

async def get_current_admin_user(token: str = Depends(oauth2_scheme)):
    username = await get_current_user(token)
    user = await user_collection.find_one({"username": username})
    if not user or not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have administrative privileges"
        )
    return user

@app.on_event("startup")
async def startup_db_client():
    print("Checking MongoDB connection...")
    await test_db_connection()
    cursor = pdf_collection.find({"document_id": {"$exists": False}}).sort("upload_date", 1)
    next_id = await pdf_collection.count_documents({"document_id": {"$exists": True}}) + 1
    async for document in cursor:
        await pdf_collection.update_one({"_id": document["_id"]}, {"$set": {"document_id": next_id}})
        next_id += 1
    async for document in pdf_collection.find({"document_id": {"$exists": True}}):
        await discussion_collection.update_many({"pdf_id": str(document["_id"])}, {"$set": {"pdf_id": str(document["document_id"])}})
    await pdf_collection.create_index("document_id", unique=True)


# ==========================================
# Dedicated HTML Page Route Handlers
# ==========================================
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(root_dir, "index.html"))

@app.get("/index")
async def serve_index_alt():
    return FileResponse(os.path.join(root_dir, "index.html"))

@app.get("/index.html")
async def serve_index_file():
    return FileResponse(os.path.join(root_dir, "index.html"))

@app.get("/pdfs")
async def serve_pdfs():
    return FileResponse(os.path.join(root_dir, "pdfs.html"))

@app.get("/pdfs.html")
async def serve_pdfs_file():
    return FileResponse(os.path.join(root_dir, "pdfs.html"))

@app.get("/viewer")
async def serve_viewer():
    return FileResponse(os.path.join(root_dir, "viewer.html"))

@app.get("/viewer.html")
async def serve_viewer_file():
    return FileResponse(os.path.join(root_dir, "viewer.html"))

@app.get("/login")
async def serve_login():
    return FileResponse(os.path.join(root_dir, "login.html"))

@app.get("/login.html")
async def serve_login_file():
    return FileResponse(os.path.join(root_dir, "login.html"))

@app.get("/register")
async def serve_register():
    return FileResponse(os.path.join(root_dir, "register.html"))

@app.get("/register.html")
async def serve_register_file():
    return FileResponse(os.path.join(root_dir, "register.html"))

@app.get("/faqs")
async def serve_faqs():
    return FileResponse(os.path.join(root_dir, "faqs.html"))

@app.get("/faqs.html")
async def serve_faqs_file():
    return FileResponse(os.path.join(root_dir, "faqs.html"))

@app.get("/admin-login")
async def serve_admin_login():
    return FileResponse(os.path.join(root_dir, "admin-login.html"))

@app.get("/admin-login.html")
async def serve_admin_login_file():
    return FileResponse(os.path.join(root_dir, "admin-login.html"))

@app.get("/admin-dashboard")
async def serve_admin_dashboard():
    return FileResponse(os.path.join(root_dir, "admin-dashboard.html"))

@app.get("/admin-dashboard.html")
async def serve_admin_dashboard_file():
    return FileResponse(os.path.join(root_dir, "admin-dashboard.html"))

@app.get("/admin-upload")
async def serve_admin_upload():
    return FileResponse(os.path.join(root_dir, "admin-upload.html"))

@app.get("/admin-upload.html")
async def serve_admin_upload_file():
    return FileResponse(os.path.join(root_dir, "admin-upload.html"))

@app.get("/admin-faqs")
async def serve_admin_faqs():
    return FileResponse(os.path.join(root_dir, "admin-faqs.html"))

@app.get("/admin-faqs.html")
async def serve_admin_faqs_file():
    return FileResponse(os.path.join(root_dir, "admin-faqs.html"))


# ==========================================
# 1. User Authentication & Registration Routes
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
        "joined_date": current_time,
        "is_admin": False
    }

    result = await user_collection.insert_one(user_doc)
    
    return {
        "id": str(result.inserted_id),
        "username": user.username,
        "email": user.email,
        "joined_date": current_time,
        "is_admin": False
    }


@app.post("/api/login", response_model=Token)
async def login(form_data: UserLogin):
    user = await user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password."
        )
    
    access_token = create_access_token(data={"sub": user["username"], "is_admin": user.get("is_admin", False)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
        "is_admin": user.get("is_admin", False)
    }


@app.post("/api/reset-password")
async def reset_password(data: PasswordReset):
    user = await user_collection.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found.")
    
    new_hashed_password = hash_password(data.new_password)
    await user_collection.update_one({"email": data.email}, {"$set": {"hashed_password": new_hashed_password}})
    return {"message": "Password updated successfully."}


# ==========================================
# 2. PDF Document & Cloudinary Routes
# ==========================================
@app.get("/api/pdfs", response_model=List[PDFResponse])
async def get_all_pdfs():
    pdfs = []
    cursor = pdf_collection.find({}).sort([("sort_order", 1), ("upload_date", 1)])
    async for document in cursor:
        pdfs.append(serialize_pdf(document))
    return pdfs


@app.get("/api/admin/pdfs", response_model=List[PDFResponse])
async def get_admin_pdfs(admin: dict = Depends(get_current_admin_user)):
    pdfs = []
    cursor = pdf_collection.find({}).sort([("sort_order", 1), ("upload_date", 1)])
    async for document in cursor:
        pdfs.append(serialize_pdf(document))
    return pdfs


@app.get("/api/pdfs/{pdf_id}", response_model=PDFResponse)
async def get_single_pdf(pdf_id: str):
    document = await pdf_collection.find_one(pdf_query_id(pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")
    
    return serialize_pdf(document)


@app.get("/api/faqs", response_model=List[FAQResponse])
async def get_faqs():
    faqs = []
    cursor = faq_collection.find({}).sort("timestamp", -1)
    async for document in cursor:
        faqs.append({
            "id": str(document["_id"]),
            "query_type": document.get("query_type", "general"),
            "note_reference": document.get("note_reference"),
            "heading": document.get("heading", document.get("question", "")),
            "details": document.get("details", document.get("question", "")),
            "answer": document.get("answer", ""),
            "answer_by": document.get("answer_by"),
            "user_name": document.get("user_name", "Anonymous"),
            "timestamp": document.get("timestamp", "")
        })
    return faqs


@app.post("/api/faqs", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(faq: FAQCreate, current_user: str = Depends(get_current_user)):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    faq_doc = {
        "query_type": faq.query_type,
        "note_reference": faq.note_reference,
        "heading": faq.heading,
        "details": faq.details,
        "answer": "",
        "user_name": current_user,
        "timestamp": timestamp
    }
    result = await faq_collection.insert_one(faq_doc)
    return {"id": str(result.inserted_id), **faq_doc}


@app.put("/api/admin/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(faq_id: str, answer: str = Form(...), admin: dict = Depends(get_current_admin_user)):
    if not ObjectId.is_valid(faq_id):
        raise HTTPException(status_code=400, detail="Invalid FAQ ID.")
    result = await faq_collection.update_one({"_id": ObjectId(faq_id)}, {"$set": {"answer": answer.strip(), "answer_by": admin.get("username", "Administrator")}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="FAQ not found.")
    document = await faq_collection.find_one({"_id": ObjectId(faq_id)})
    if not document:
        raise HTTPException(status_code=404, detail="FAQ not found.")
    return {
        "id": str(document["_id"]), "query_type": document.get("query_type", "general"),
        "note_reference": document.get("note_reference"), "heading": document.get("heading", ""),
        "details": document.get("details", ""), "answer": document.get("answer", ""),
        "user_name": document.get("user_name", "Anonymous"), "answer_by": document.get("answer_by"), "timestamp": document.get("timestamp", "")
    }


@app.delete("/api/admin/faqs/{faq_id}")
async def delete_faq(faq_id: str, admin: dict = Depends(get_current_admin_user)):
    if not ObjectId.is_valid(faq_id):
        raise HTTPException(status_code=400, detail="Invalid FAQ ID.")
    result = await faq_collection.delete_one({"_id": ObjectId(faq_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="FAQ not found.")
    return {"message": "FAQ deleted successfully."}


@app.get("/api/recent-pdfs", response_model=List[PDFResponse])
async def get_recent_pdfs(current_user: str = Depends(get_current_user)):
    user = await user_collection.find_one({"username": current_user})
    recent_ids = (user or {}).get("recent_pdf_ids", [])[:3]
    recent = []
    for recent_id in recent_ids:
        try:
            document = await pdf_collection.find_one(pdf_query_id(str(recent_id)))
        except HTTPException:
            document = None
        if document:
            recent.append(serialize_pdf(document))
    return recent


@app.post("/api/recent-pdfs/{pdf_id}")
async def record_recent_pdf(pdf_id: str, current_user: str = Depends(get_current_user)):
    document = await pdf_collection.find_one(pdf_query_id(pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")
    user = await user_collection.find_one({"username": current_user})
    existing = (user or {}).get("recent_pdf_ids", [])
    normalized_id = document["_id"]
    recent_ids = [item for item in existing if str(item) != str(normalized_id)]
    recent_ids.insert(0, normalized_id)
    await user_collection.update_one({"username": current_user}, {"$set": {"recent_pdf_ids": recent_ids[:3]}})
    return {"message": "Recent PDF recorded."}


@app.get("/api/pdfs/{pdf_id}/file")
async def get_pdf_file(pdf_id: str):
    document = await pdf_collection.find_one(pdf_query_id(pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")

    try:
        with urlopen(get_pdf_delivery_url(document)) as cloudinary_file:
            contents = cloudinary_file.read()
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Unable to load PDF file: {error}")

    file_name = os.path.basename(document.get("file_name") or f"{document['title']}.pdf")
    file_name = file_name.replace('"', "")
    return Response(
        content=contents,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{file_name}"'}
    )


@app.post("/api/admin/upload-pdf", response_model=PDFResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin_user)
):
    if not file or not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        contents = await file.read()
        upload_result = cloudinary.uploader.upload(
            contents,
            resource_type="image",
            folder="tariq_al_huda_pdfs",
            filename_override=os.path.basename(file.filename)
        )
        
        secure_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        current_date = datetime.utcnow().strftime("%Y-%m-%d")

        next_document_id = await pdf_collection.count_documents({"document_id": {"$exists": True}}) + 1
        while await pdf_collection.find_one({"document_id": next_document_id}):
            next_document_id += 1
        pdf_doc = {
            "document_id": next_document_id,
            "title": title,
            "description": description,
            "upload_date": current_date,
            "cloudinary_url": secure_url,
            "public_id": public_id,
            "file_name": os.path.basename(file.filename),
            "resource_type": "image",
            "sort_order": await pdf_collection.count_documents({})
        }

        result = await pdf_collection.insert_one(pdf_doc)

        return {
            "id": str(next_document_id),
            "title": title,
            "description": description,
            "upload_date": current_date,
            "cloudinary_url": get_pdf_delivery_url(pdf_doc),
            "public_id": public_id,
            "file_name": os.path.basename(file.filename)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {str(e)}")


@app.delete("/api/admin/pdfs/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    admin: dict = Depends(get_current_admin_user)
):
    document = await pdf_collection.find_one(pdf_query_id(pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")

    public_id = document.get("public_id")
    if public_id:
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Cloudinary deletion warning: {e}")

    result = await pdf_collection.delete_one(pdf_query_id(pdf_id))
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Failed to delete PDF.")

    document_id = str(document.get("document_id", document["_id"]))
    await discussion_collection.delete_many({"pdf_id": document_id})
    
    return {"message": "PDF deleted successfully."}


@app.put("/api/admin/pdfs/reorder")
async def reorder_pdfs(ordered_ids: List[str], admin: dict = Depends(get_current_admin_user)):
    for order, pdf_id in enumerate(ordered_ids):
        await pdf_collection.update_one(pdf_query_id(pdf_id), {"$set": {"sort_order": order}})
    return {"message": "PDF order updated successfully."}


@app.put("/api/admin/pdfs/{pdf_id}", response_model=PDFResponse)
async def update_pdf(
    pdf_id: str,
    title: str = Form(...),
    description: str = Form(...),
    file: Optional[UploadFile] = File(None),
    admin: dict = Depends(get_current_admin_user)
):
    document = await pdf_collection.find_one(pdf_query_id(pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")

    updates = {"title": title.strip(), "description": description.strip()}
    if file and file.filename:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        contents = await file.read()
        upload_result = cloudinary.uploader.upload(
            contents,
            resource_type="image",
            folder="tariq_al_huda_pdfs",
            filename_override=os.path.basename(file.filename)
        )
        old_public_id = document.get("public_id")
        if old_public_id:
            cloudinary.uploader.destroy(old_public_id)
        updates.update({
            "cloudinary_url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id"),
            "file_name": os.path.basename(file.filename),
            "resource_type": "image"
        })

    await pdf_collection.update_one(pdf_query_id(pdf_id), {"$set": updates})
    updated = await pdf_collection.find_one(pdf_query_id(pdf_id))
    return serialize_pdf(updated)


# ==========================================
# 3. Discussion & Comment Routes (ID-Linked)
# ==========================================
@app.get("/api/discussions/{pdf_id}", response_model=List[DiscussionResponse])
async def get_pdf_discussions(pdf_id: str, current_user: str = Depends(get_current_user)):
    document = await pdf_collection.find_one(pdf_query_id(pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")
    canonical_pdf_id = str(document.get("document_id", document["_id"]))
    discussions = []
    cursor = discussion_collection.find({"pdf_id": canonical_pdf_id}).sort("timestamp", 1)
    async for doc in cursor:
        discussions.append({
            "id": str(doc["_id"]),
            "pdf_id": doc["pdf_id"],
            "user_id": doc.get("user_id"),
            "user_name": doc["user_name"],
            "is_admin": doc.get("is_admin", False),
            "message": doc["message"],
            "timestamp": doc["timestamp"]
        })
    return discussions


@app.post("/api/discussions", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def post_discussion(comment: DiscussionCreate, current_user: str = Depends(get_current_user)):
    document = await pdf_collection.find_one(pdf_query_id(comment.pdf_id))
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")

    canonical_pdf_id = str(document.get("document_id", document["_id"]))

    user_doc = await user_collection.find_one({"username": current_user})
    user_id = str(user_doc["_id"]) if user_doc else None
    
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    comment_doc = {
        "pdf_id": canonical_pdf_id,
        "user_id": user_id,
        "user_name": current_user,
        "is_admin": user_doc.get("is_admin", False) if user_doc else False,
        "message": comment.message,
        "timestamp": current_time
    }

    result = await discussion_collection.insert_one(comment_doc)

    return {
        "id": str(result.inserted_id),
        "pdf_id": canonical_pdf_id,
        "user_id": user_id,
        "user_name": current_user,
        "is_admin": comment_doc["is_admin"],
        "message": comment.message,
        "timestamp": current_time
    }


@app.delete("/api/discussions/{discussion_id}")
async def delete_discussion(discussion_id: str, admin: dict = Depends(get_current_admin_user)):
    if not ObjectId.is_valid(discussion_id):
        raise HTTPException(status_code=400, detail="Invalid chat ID.")

    result = await discussion_collection.delete_one({"_id": ObjectId(discussion_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat message not found.")

    return {"message": "Chat message deleted successfully."}