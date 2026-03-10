from fastapi import FastAPI, HTTPException, Body
from app.database import questions_collection, sessions_collection
from app.engine import update_ability
from dotenv import load_dotenv
import os
from openai import OpenAI
import uuid
import random

# Load the secret notebook (.env)
load_dotenv()

app = FastAPI(title="AI-Driven Adaptive Diagnostic Engine")

# --- AI SETUP ---
# We get the key, but we don't let the app crash if it's missing
API_KEY = os.getenv("OPENAI_API_KEY")
if API_KEY:
    client = OpenAI(api_key=API_KEY)
else:
    client = None
    print("⚠️ Warning: OPENAI_API_KEY not found. AI Insights will run in 'Mock Mode'.")

# --- 1. THE STARTING POINT ---
@app.get("/")
def home():
    return {"message": "AI Adaptive Engine is Running!"}

@app.post("/start-session")
async def start_session():
    """Starts a new test and sets the baseline difficulty to 0.5."""
    session_id = str(uuid.uuid4())
    new_session = {
        "session_id": session_id,
        "current_ability": 0.5, # Starts at 0.5 as required [cite: 23]
        "answered_questions": [],
        "history": []
    }
    await sessions_collection.insert_one(new_session)
    return {"session_id": session_id, "message": "Test Started!"}

# --- 2. THE QUESTION PICKER ---
@app.get("/next-question/{session_id}")
async def get_next_question(session_id: str):
    """Dynamically selects a question based on current proficiency."""
    session = await sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    ability = session["current_ability"]
    already_seen = session["answered_questions"]

    # Limit the test to 10 questions as per Phase 3 requirements [cite: 29]
    if len(already_seen) >= 10:
        return {"message": "Test Complete! You have answered 10 questions.", "done": True}

    # Find a question near the student's ability level
    query = {
        "difficulty": {"$gte": ability - 0.2, "$lte": ability + 0.2},
        "text": {"$nin": already_seen}
    }
    
    questions = await questions_collection.find(query).to_list(length=10)
    
    if not questions:
        questions = await questions_collection.find({"text": {"$nin": already_seen}}).to_list(length=1)

    if not questions:
        return {"message": "No more questions available.", "done": True}

    question = random.choice(questions)
    return {
        "question_text": question["text"],
        "options": question["options"],
        "difficulty": question["difficulty"],
        "topic": question["topic"]
    }

# --- 3. THE GRADER (IRT Logic) ---
@app.post("/submit-answer/{session_id}")
async def submit_answer(session_id: str, payload: dict = Body(...)):
    """Grades the answer and updates the Ability Score[cite: 26]."""
    question_text = payload.get("question_text")
    user_answer = payload.get("answer")

    session = await sessions_collection.find_one({"session_id": session_id})
    question = await questions_collection.find_one({"text": question_text})

    if not session or not question:
        raise HTTPException(status_code=404, detail="Session or Question not found")

    is_correct = (user_answer == question["correct_answer"])

    # Update Ability Score using IRT logic [cite: 26]
    new_ability = update_ability(
        current_ability=session["current_ability"],
        difficulty=question["difficulty"],
        is_correct=is_correct
    )

    await sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {"current_ability": new_ability},
            "$push": {
                "answered_questions": question_text,
                "history": {
                    "topic": question["topic"],
                    "difficulty": question["difficulty"],
                    "correct": is_correct
                }
            }
        }
    )

    return {
        "is_correct": is_correct,
        "new_ability_score": new_ability,
        "correct_answer": question["correct_answer"] if not is_correct else "Correct!"
    }

# --- 4. AI INSIGHTS ---
@app.post("/get-insights/{session_id}")
async def get_insights(session_id: str):
    """Generates a 3-step study plan using AI[cite: 30]."""
    session = await sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    history = session.get("history", [])
    missed_topics = list(set([item["topic"] for item in history if not item["correct"]]))
    
    if not missed_topics:
        return {"plan": "Perfect score! You're ready for the real GRE."}

    # If AI key is present, use it. Otherwise, use a backup plan.
    if client:
        try:
            prompt = f"The student missed questions in: {', '.join(missed_topics)}. Provide a 3-step study plan[cite: 30]."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_plan = response.choices[0].message.content
        except Exception as e:
            ai_plan = f"AI Error. Manually suggested plan: 1. Review {missed_topics[0]} 2. Practice more. 3. Re-test."
    else:
        # Mock mode fallback
        ai_plan = f"Step 1: Focus on {missed_topics[0]}. Step 2: Study {len(missed_topics)} related topics. Step 3: Practice mock tests[cite: 30]."

    return {"personalized_study_plan": ai_plan}