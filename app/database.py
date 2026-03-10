import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# This tells the code to find the link in your .env file
MONGO_URL = os.getenv("MONGO_URL") 
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.adaptive_testing

questions_collection = db.questions
sessions_collection = db.user_sessions