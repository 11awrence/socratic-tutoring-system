from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from socratic_tutor import process_student_turn  

app = FastAPI(title="Multi-Agent Math Tutor API")

class TurnRequest(BaseModel):
    student_input: str
    state: Dict[str, Any]        

class TurnResponse(BaseModel):
    response: str
    emotion: str
    affective_suggestion: str
    problem_solved: bool
    reflection_count: int
    debug_logs: List[str]
    current_problem: Optional[str]
    history: List[str]
    state: Dict[str, Any]       


# create POST http://localhost:8000/turn
@app.post("/turn")
def run_turn(req: TurnRequest):
    state = req.state
    state["student_input"] = req.student_input

    # Ensure required keys exist
    defaults = {
        "student_input": "",
        "student_emotion": "neutral",
        "progress": "beginning",
        "known_mistake": None,
        "history": [],
        "orchestrator_instruction": "",
        "affective_suggestion": "",
        "final_response": "",
        "problem_solved": False,
        "reflection_count": 0,
        "next_agent": None,
        "current_problem": None,
        "original_problem": None,
        "debug_logs": [],
        "math_tutor_reasoning": None,
        "metacognitive_strategy": None,
    }
    for k, v in defaults.items():
        if k not in state:
            state[k] = v

    result = process_student_turn(state, req.student_input)

    return {
        "response": result.get("response") or result.get("final_response", ""),
        "emotion": result.get("emotion", result.get("student_emotion", "neutral")),
        "affective_suggestion": result.get("affective_suggestion", ""),
        "problem_solved": result.get("problem_solved", False),
        "reflection_count": result.get("reflection_count", 0),
        "debug_logs": result.get("debug_logs", []),
        "current_problem": result.get("current_problem"),
        "history": result.get("history", []),
        "math_tutor_reasoning": result.get("math_tutor_reasoning"),
        "metacognitive_strategy": result.get("metacognitive_strategy"),
        "state": result.get("state", result),
    }
