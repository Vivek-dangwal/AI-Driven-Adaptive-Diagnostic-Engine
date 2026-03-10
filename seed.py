import json
import asyncio
from app.database import questions_collection

async def seed_data():
    # 1. Open the box (read the JSON file)
    with open("data/questions.json", "r") as f:
        questions = json.load(f)
    
    # 2. Clear the shelf so we don't have duplicates
    await questions_collection.delete_many({})
    
    # 3. Put the new questions on the shelf
    if questions:
        await questions_collection.insert_many(questions)
        print(f"✅ Successfully added {len(questions)} questions to the database!")

if __name__ == "__main__":
    asyncio.run(seed_data())