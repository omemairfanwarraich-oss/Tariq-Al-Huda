# Complete Technical & Functional Documentation: طريق الهدى (Tariq Al-Huda)

طريق الهدى (Path of Guidance) is a full-stack educational and spiritual web platform designed to manage, browse, and interact with structured study notes, documents, and community Q&A forums. It features a responsive **Midnight Blue & Gold** glassmorphism theme and provides separate, secure workflows for standard students and administrative staff.

---

## 1. System Architecture & Directory Layout

The project follows a clean, modular structure that separates backend routing, database connectors, data validation schemas, and frontend presentation assets:

```text
Tariq Al-Huda/
├── assets/
│   ├── css/
│   │   └── style.css            # Global styling, theme variables, and glassmorphism definitions
│   ├── images/                  # Platform logos and branding elements
│   └── js/
│       ├── auth.js              # Authentication and session management logic
│       ├── component-loader.js  # Dynamic header/footer injection helper
│       ├── main.js              # Core layout and interactive script handlers
│       ├── pdfs.js              # Document repository rendering and search logic
│       └── recent-pdfs.js       # Tracking and rendering user history tiles
├── backend/
│   ├── __pycache__/
│   ├── venv/                    # Python virtual environment
│   ├── .env                     # Environment variables (DB, JWT, Cloudinary)
│   ├── database.py              # MongoDB asynchronous client connection
│   ├── main.py                  # Core FastAPI application server & endpoints
│   ├── schemas.py               # Pydantic validation models
│   └── utils.py                 # Helper functions and utilities
├── components/
│   ├── footer.html              # Reusable footer layout template
│   └── header.html              # Reusable header layout template
├── admin-dashboard.html         # Administrative portal home
├── admin-faqs.html              # FAQ moderation interface for staff
├── admin-login.html             # Secure administrative login view
├── admin-upload.html            # PDF note uploading and reordering view
├── faqs.html                    # Public user Q&A desk and submission form
├── index.html                   # Main landing page
├── login.html                   # User login interface
├── pdfs.html                    # Public document and study note repository
├── register.html                # User registration portal
├── viewer.html                  # Integrated document reading view
└── requirement.txt              # Python package dependencies
```
## 2. Core Functional Modules

### PDF Document & Note Management
* **Structured Repository**: Allows users to search and filter through structured study materials and lesson records in real time.
* **Cloud Storage & Security**: Leverages Cloudinary for secure file storage, utilizing private download routes (`/api/pdfs/{pdf_id}/file`) to stream PDF content safely.
* **Recent Activity Tracking**: Automatically logs user interactions and presents recently viewed materials (`/api/recent-pdfs`) for quick navigation.
* **Administrative Control**: Authorized staff can upload new documents, edit metadata, delete entries, and dynamically reorder notes (`/api/admin/pdfs/reorder`).

### Knowledge Desk & Interactive Q&A
* **Categorized Inquiries**: Students can submit targeted questions categorized as general questions, note-specific inquiries, or technical issues.
* **Admin Moderation Desk**: Staff members can view un-answered and answered items via `admin-faqs.html`, publish immediate text replies, update existing resolutions, or remove inquiries.

### Contextual Discussion System
* **ID-Linked Chat Loops**: Discussion messages are bound directly to specific study materials, fostering collaborative peer discourse alongside administrator guidance.

### Role-Based Access Control & Security
* **Authentication Pipeline**: Secure password handling via bcrypt password hashing paired with JSON Web Tokens (JWT) for stateless session tracking.
* **Privilege Guardrails**: Protected administrative endpoints (`get_current_admin_user`) block unauthorized access, restricting management operations strictly to verified admin accounts.

---

## 3. Technology Stack

* **Backend Framework**: FastAPI (Python asynchronous framework) delivering high-performance API routing and automatic Swagger documentation (`/docs`).
* **Database Layer**: MongoDB (accessed via Motor and PyMongo) featuring flexible document schemas, unique indexing, and custom ID mapping.
* **Frontend Layer**: Vanilla JavaScript (ES6+), HTML5, and modular CSS3 variables utilizing grid layouts and glassmorphism visual styles.
* **Media Management**: Cloudinary API for secure cloud hosting, asset transformations, and media management.

---

## 4. Local Installation & Setup Guide

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/tariq-al-huda.git](https://github.com/your-username/tariq-al-huda.git)
   cd tariq-al-huda

## 4. Local Installation & Setup Guide

1. **Create and activate a Python virtual environment:**
   ```bash
   python -m venv backend/venv
   # On Windows:
   backend\venv\Scripts\activate
   # On macOS/Linux:
   source backend/venv/bin/activate
Install application dependencies:

Bash
pip install -r requirement.txt
Configure your environment variables:
Create a .env file inside the backend/ directory with your database and API keys:

Code snippet
MONGODB_URL=your_mongodb_connection_string
SECRET_KEY=your_secure_jwt_secret_key
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
Run the FastAPI development server:

Bash
uvicorn backend.main:app --reload
Open your browser and visit http://127.0.0.1:8000.

5. Production Deployment Instructions (Render Platform)
The application is fully compatible with free and paid tiers on Render as a Python Web Service. Configure your deployment settings as follows:

Environment / Runtime: Python 3

Build Command: pip install -r requirement.txt

Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

Environment Variables: Make sure to map all keys from your local .env file into the Environment settings tab of your Render service dashboard prior to launching.
