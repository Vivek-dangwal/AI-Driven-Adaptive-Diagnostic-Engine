from pydantic import BaseModel, Field
from typing import List, Optional

# This is the blueprint for one GRE Question
class Question(BaseModel):
    text: str                       # The actual question text
    options: List[str]              # Multiple choice options
    correct_answer: str             # The right answer [cite: 19]
    difficulty: float = Field(..., ge=0.1, le=1.0) # Score from 0.1 to 1.0 [cite: 18]
    topic: str                      # e.g., Algebra or Vocabulary [cite: 19]
    tags: List[str]                 # Extra labels [cite: 19]

# This is the blueprint for a Student's Journey
class UserSession(BaseModel):
    user_id: str
    current_ability: float = 0.5    # Everyone starts at 0.5 [cite: 23]
    questions_answered: List[str] = [] # List of Question IDs they already saw
    score_history: List[dict] = []  # To track if they got them right or wrong