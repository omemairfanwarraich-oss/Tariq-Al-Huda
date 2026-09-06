import os
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from bson import ObjectId
import cloudinary
import cloudinary.uploader

from database import test_db_connection, user_collection, pdf_collection, discussion_collection
from schemas import UserCreate, UserResponse, PDFResponse, DiscussionCreate, DiscussionResponse, UserLogin, Token, PasswordReset

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


@app.get("/api/admin/pdfs", response_model=List[PDFResponse])
async def get_admin_pdfs(admin: dict = Depends(get_current_admin_user)):
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
    custom_id: Optional[str] = Form(None),
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin_user)
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

        # If a custom ID is provided and is a valid ObjectId, use it
        if custom_id and custom_id.strip():
            if ObjectId.is_valid(custom_id.strip()):
                pdf_doc["_id"] = ObjectId(custom_id.strip())
            else:
                raise HTTPException(status_code=400, detail="Invalid custom ID format. Must be a valid 24-character hex string.")

        result = await pdf_collection.insert_one(pdf_doc)

        return {
            "id": str(result.inserted_id),
            "title": title,
            "description": description,
            "upload_date": current_date,
            "cloudinary_url": secure_url,
            "public_id": public_id
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
    if not ObjectId.is_valid(pdf_id):
        raise HTTPException(status_code=400, detail="Invalid PDF ID format.")
    
    document = await pdf_collection.find_one({"_id": ObjectId(pdf_id)})
    if not document:
        raise HTTPException(status_code=404, detail="PDF note not found.")

    public_id = document.get("public_id")
    if public_id:
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"Cloudinary deletion warning: {e}")

    result = await pdf_collection.delete_one({"_id": ObjectId(pdf_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Failed to delete PDF.")
    
    return {"message": "PDF deleted successfully."}


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
async def post_discussion(comment: DiscussionCreate, current_user: str = Depends(get_current_user)):
    user_doc = await user_collection.find_one({"username": current_user})
    user_id = str(user_doc["_id"]) if user_doc else None
    
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    comment_doc = {
        "pdf_id": comment.pdf_id,
        "user_id": user_id,
        "user_name": current_user,
        "message": comment.message,
        "timestamp": current_time
    }

    result = await discussion_collection.insert_one(comment_doc)

    return {
        "id": str(result.inserted_id),
        "pdf_id": comment.pdf_id,
        "user_id": user_id,
        "user_name": current_user,
        "message": comment.message,
        "timestamp": current_time
    }