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
