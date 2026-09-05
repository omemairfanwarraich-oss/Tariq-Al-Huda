import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "islamic_notes_db")

client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]

# Collections
user_collection = database.get_collection("users")
pdf_collection = database.get_collection("pdfs")
discussion_collection = database.get_collection("discussions")
faq_collection = database.get_collection("faqs")
admin_collection = database.get_collection("admins")


async def test_db_connection():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB Atlas!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")