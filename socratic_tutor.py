
import functools
import re
import json
from typing import TypedDict, List, Optional

from langgraph.graph import StateGraph, END
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

# ====================== MODELS ======================
# Heavy agents on Qwen3.5-122B class (native API, thinking disabled)
ORCHESTRATOR_MODEL = "/Users/lenaaoyama/qwen3.5-122b"
MATH_TUTOR_MODEL = "/Users/lenaaoyama/qwen3.5-122b"
METACOGNITIVE_MODEL = "/Users/lenaaoyama/qwen3.5-122b"

# Affective stays light
AFFECTIVE_MODEL = "/Users/lenaaoyama/qwen2.5-3b"

@functools.lru_cache(maxsize=4)
def get_model_tokenizer(model_path: str):
    return load(model_path)

def run_mlx(model_path: str, prompt: str, max_tokens=600) -> str:
    model, tokenizer = get_model_tokenizer(model_path)
    messages = [{"role": "user", "content": prompt}]
    prompt_text = tokenizer.apply_chat_template(
        messages, 
        add_generation_prompt=True, 
        enable_thinking=False
    )

    sampler = make_sampler(temp=0.7, top_p=0.9)
    response = generate(
        model, 
        tokenizer, 
        prompt_text, 
        sampler=sampler,
        max_tokens=max_tokens, 
    )
    return response.strip()

# ====================== STATE ======================
class TutorState(TypedDict):
    student_input: str
    student_emotion: str
    progress: str
    known_mistake: Optional[str]
    history: List[str]
    orchestrator_instruction: str
    affective_suggestion: str
    final_response: str
    problem_solved: bool
    reflection_count: int
    next_agent: Optional[str]
    current_problem: Optional[str]
    original_problem: Optional[str]
    debug_logs: List[str]

# ====================== HELPERS ======================

def log_debug(state: dict, message: str):
    if "debug_logs" not in state:
        state["debug_logs"] = []
    state["debug_logs"].append(message)
    print(message)  # Keep printing for terminal during testing


def get_synthetic_emotion_and_suggestion(student_input: str, problem_solved: bool, reflection_count: int) -> tuple[str, str]:
    text = student_input.lower()
    if any(w in text for w in ["don't understand", "confused", "stuck", "hard", "difficult"]):
        return "frustrated", "Student is frustrated. Reduce difficulty, give direct guidance."
    elif any(w in text for w in ["got it", "easy", "understand", "clear"]):
        return "happy", "Student is confident. Increase challenge or move to reflection."
    elif problem_solved:
        return "neutral", "Problem solved. One short reflection only."
    else:
        return "neutral", "Neutral. Normal guided explanation."


# ====================== NODES ======================

def state_manager_node(state: TutorState):
    state["history"].append(f"Student: {state['student_input']}")
    if len(state["history"]) > 8:
        state["history"] = state["history"][-8:]
    if "correct" in state.get("orchestrator_instruction", "").lower():
        state["progress"] = "advancing"

    # === Improved reset condition ===
    strong_new_problem_starters = [
        "i need help with", "how do i solve", "how can i simplify",
        "solve the following", "the following question", "a set of"
    ]

    looks_like_new_problem = (
        len(state["student_input"]) > 15 and
        any(phrase in state["student_input"].lower() for phrase in strong_new_problem_starters)
    )

    is_different_problem = state.get("current_problem") != state["student_input"]

    if looks_like_new_problem and is_different_problem:
        log_debug(state, "[StateManager] New problem detected → forcing full reset")
        state["current_problem"] = state["student_input"]
        state["original_problem"] = state["current_problem"]
        state["problem_solved"] = False
        state["reflection_count"] = 0
        state["history"] = [f"Student: {state['student_input']}"]
        return state

    return state

def affective_node(state: TutorState):
    student_input = state["student_input"]
    
    try:
        prompt = f"""You are a sharp, no-bullshit emotion detector for a Socratic math tutor.

Student just said: "{student_input}"

Analyze their emotional state and how the tutor should adjust.

Respond ONLY with valid JSON in this exact format:
{{
  "emotion": "frustrated" | "confused" | "confident" | "neutral" | "discouraged",
  "intensity": "low" | "medium" | "high",
  "suggestion": "one short, actionable instruction for the orchestrator (max 15 words)"
}}

JSON:"""
        
        response = run_mlx(AFFECTIVE_MODEL, prompt, max_tokens=80)
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            affective_data = json.loads(json_match.group(0))
            state["student_emotion"] = affective_data.get("emotion", "neutral")
            state["affective_suggestion"] = affective_data.get("suggestion", "")
            log_debug(state, f"[Affective DEBUG] LLM SUCCESS → emotion={state['student_emotion']}, suggestion=\"{state['affective_suggestion']}\"")
        else:
            # JSON parse failed → fallback
            log_debug(state, "[Affective DEBUG] LLM returned invalid JSON, falling back to synthetic")
            emotion, suggestion = get_synthetic_emotion_and_suggestion(
                student_input, state.get("problem_solved", False), state.get("reflection_count", 0)
            )
            state["student_emotion"] = emotion
            state["affective_suggestion"] = suggestion
            
    except Exception as e:
        log_debug(state, f"[Affective DEBUG] LLM call failed ({e}), falling back to synthetic")
        emotion, suggestion = get_synthetic_emotion_and_suggestion(
            student_input, state.get("problem_solved", False), state.get("reflection_count", 0)
        )
        state["student_emotion"] = emotion
        state["affective_suggestion"] = suggestion

    return state

def orchestrator_node(state: TutorState):
    history_str = "\n".join(state["history"][-8:])

    current_count = state.get("reflection_count", 0)
    current_solved = state.get("problem_solved", False)
    log_debug(state, f"[Orchestrator DEBUG] At start of node - solved={current_solved}, reflection_count={current_count}")

    if current_count >= 2:
        log_debug(state, "\n[Orchestrator] HARD FORCED close after 2 reflections")
        return {
            "orchestrator_instruction": "Session complete after 2 reflections.",
            "next_agent": "FinalResponse",
            "final_response": "Great job! You solved it. Want to try another problem?",
            "problem_solved": True,
        }


    prompt = f"""You are the Orchestrator Brain. Your primary responsibility is to maintain coherence and continuity across the entire tutoring session.
You must track what has already been correctly established in previous turns and prevent unnecessary regression to earlier steps.

CURRENT PROBLEM (NEVER CHANGE THIS): {state.get('current_problem', 'None')}

You have access to two important references:
- CURRENT PROBLEM: The original full question.
- History: The recent conversation turns.

CURRENT PROGRESS SUMMARY (you must maintain and update this):
Keep a short mental note of what has already been correctly calculated in this session.

KNOWN_MISTAKE (you must maintain and update this):
Keep track of the most recent or recurring mistake the student has made.

Before writing any instruction to MathTutor, you must check the CURRENT PROBLEM, History, CURRENT PROGRESS SUMMARY, and KNOWN_MISTAKE, then answer:
- What has the student already correctly completed?
- What is the current phase of the problem (who is working right now)?
- Has the student already calculated the thing I am about to ask for?
- Is there a recurring or relevant mistake I should remind the student about?

If something was already correctly done, do NOT ask the student to redo it. Move forward instead.

Affective guidance (follow this when choosing tone and difficulty): {state.get('affective_suggestion', 'Normal Socratic guidance')}

ABSOLUTE RULE - NO HALLUCINATION OF THE EXPRESSION:
- You must preserve the EXACT order of operations from the original problem the student gave.
- When writing instructions to MathTutor, always restate the current remaining part of the expression accurately based on what the student has already completed.
- Never invent or assume operations that are not part of the original expression.
- Always track what part of the original problem still needs to be solved.

Current state: solved={state.get('problem_solved', False)}, reflections={state.get('reflection_count', 0)}, emotion={state['student_emotion']}, progress={state['progress']}, known_mistake={state.get('known_mistake', 'None')}

Student just said: {state['student_input']}
History: {history_str}

CRITICAL ASSESSMENT:
FOCUS ONLY ON THE CURRENT PROBLEM. The student must complete the ENTIRE original expression or problem — NEVER treat any sub-result or partial progress as the final answer.

You must maintain a clear mental model of the overall problem structure, including any changing conditions (e.g. who is working together or alone at each stage of the timeline). When the conversation becomes long or the student shows confusion, periodically re-anchor to the original problem statement and current phase before giving the next instruction.

CRITICAL RULES - DO NOT VIOLATE:
- Before writing any instruction to MathTutor, you must first analyze the student's latest response and **explicitly list all errors** present (sign errors, distribution errors, conceptual mistakes, wrong setup, etc.). Do not proceed until you have identified every visible error.
- When the student makes multiple errors in one response, address the most fundamental or structural errors first. Do not only correct the first mistake you notice.
- When the student performs an algebraic manipulation (especially distributing or moving terms), you MUST verify the signs and results on **both sides** of the equation before continuing.
- Before deciding the next step, actively consult the CURRENT PROGRESS SUMMARY and History and answer:
  - What has the student already correctly completed or calculated?
  - Has the student already done the calculation I am about to ask for?
  If something was already correctly completed, do NOT ask the student to redo it.
- Never regress to earlier steps that were already correctly completed unless the student explicitly shows they no longer understand them.

 Rules for agent routing:
1. Not solved → MathTutor (give ONE precise next advancing step)
2. Just solved + count==0 → Metacognitive for initial reflection
3. solved + count==1 → Metacognitive to EVALUATE the previous reflection
4. count >= 2 → FinalResponse (close)

CRITICAL RULE FOR problem_solved:
- Only set problem_solved = true if the student has given a numerically reasonable final answer that is consistent with the calculations shown in the History.
- If the student gives a clearly wrong numerical answer (even if they sound confident), do NOT set problem_solved = true yet. Continue guiding them instead.
- When generating a FinalResponse, double-check that the proposed final answer matches the calculations done in the session. If there is inconsistency, do not output the answer.

CRITICAL RULE FOR INSTRUCTIONS:
- NEVER write the actual numerical result or simplified answer in your instruction to MathTutor.
- Only give guiding questions or point out what the student did wrong. Let the student discover the result themselves.

When the student transforms an equation (for example, moving terms from one side to the other), always check the signs carefully before accepting the new equation.
If you see a potential sign error, ask the student to verify that specific step instead of continuing.

Before outputting the final JSON, you must complete this internal reasoning step (do not output this reasoning to the user):

Step 1: Error Detection
- Explicitly list ALL errors you can detect in the student’s latest response (sign errors, distribution errors, conceptual mistakes, wrong setup, etc.).
- If there are errors on both sides of an equation or in multiple parts of the working, list them all.

Step 2: State Check
- Check CURRENT PROGRESS SUMMARY and History: What has the student already correctly completed?
- Check KNOWN_MISTAKE: Is the student repeating a previous mistake?

Step 3: Decision
- Based on the errors found and what has already been done, decide the next_agent and write the instruction.
- If you are considering setting problem_solved = true:
  - Verify that the student has given a numerically reasonable final answer that is consistent with the calculations shown in the History.
  - If the proposed final answer looks incorrect, inconsistent, or incomplete, do NOT set problem_solved = true. Continue with MathTutor instead and point out the issue.
  - Only set problem_solved = true when both the error check and the final answer consistency check pass.

Only after finishing this internal check, output the JSON.

Respond with pure JSON only:
{{
  "next_agent": "MathTutor" or "Metacognitive" or "FinalResponse",
  "instruction": "precise single advancing content focus",
  "final_response": "",
  "problem_solved": true/false
}}"""
    decision = run_mlx(ORCHESTRATOR_MODEL, prompt, 600)
    log_debug(state, f"\nOrchestrator (plan): {decision}")

    json_match = re.search(r'\{.*\}', decision, re.DOTALL)
    json_str = json_match.group(0) if json_match else decision.strip()
    try:
        d = json.loads(json_str)
        result = {
            "orchestrator_instruction": d.get("instruction", ""),
            "next_agent": d.get("next_agent", "MathTutor"),
            "final_response": d.get("final_response", "Let's continue."),
            "problem_solved": d.get("problem_solved", False),
        }


        # Hard force meta reflection on first solve (count == 0)
        if result.get("problem_solved") and current_count == 0:
            result["next_agent"] = "Metacognitive"
            result["instruction"] = "Ask ONE sharp reflection question on the key insight from solving this problem."

        # Hard force evaluation when count==1
        if current_solved and current_count == 1:
            result["next_agent"] = "Metacognitive"
            result["instruction"] = "EVALUATE the student's answer to the previous reflection. Point out misconceptions or give short summary + general strategy."
            result["problem_solved"] = True

        if result.get("problem_solved") and current_count >= 2:
            result["next_agent"] = "FinalResponse"
            result["final_response"] = "Great job! Want to try another problem?"
        return result
    except Exception as e:
        log_debug(state, f"JSON parse error: {e}")
        return {
            "orchestrator_instruction": "Guide the student with one step",
            "next_agent": "MathTutor",
            "final_response": "Let's continue.",
            "problem_solved": False,
        }


def math_tutor_node(state: TutorState):
    history_str = "\n".join(state["history"][-6:])
    prompt = f"""You are the Math Content Assassin. PURE SURGICAL CONTENT FOCUS ONLY. 

CURRENT PROBLEM (NEVER CHANGE THIS — the student must finish the FULL original expression):
{state.get('current_problem', 'None')}

Recent conversation:
{history_str}

Student just said: {state['student_input']}
Orchestrator instruction: {state['orchestrator_instruction']}
Current emotion: {state['student_emotion']}

CRITICAL RULE: Never treat any sub-result (parentheses, intermediate fraction, etc.) as the final answer. Only guide toward completing the ORIGINAL expression above. Do not stop early.

Output ONLY this exact format:

Gap: [one sentence]
Next content focus: [one sentence]"""
    message = run_mlx(MATH_TUTOR_MODEL, prompt, 400)
    return {"math_tutor_reasoning": message}

def metacognitive_node(state: TutorState):
    history_str = "\n".join(state["history"][-6:])
    log_debug(state, f"[Meta DEBUG] History last 3 entries: {state['history'][-3:]}")
    log_debug(state, f"[Meta DEBUG] Previous meta question in history? {'(Meta)' in ' '.join(state['history'][-2:]) if len(state['history']) >= 2 else False}")
    prompt = f"""You are the Vicious Socratic Drill Sergeant.

CURRENT PROBLEM (NEVER CHANGE THIS): {state.get('current_problem', 'None')}

Recent conversation:
{history_str}

Student just said: {state['student_input']}
Current emotion: {state['student_emotion']}
Orchestrator instruction: {state['orchestrator_instruction']}

EVALUATE against the current_problem.
- If there WAS a previous reflection question from you marked as (Meta), then EVALUATE the student's reflection critically:
- If the reflection is incomplete, superficial, or misses key points: Clearly state what is missing or incorrect first, then briefly clarify.
- If the reflection shows good insight: Acknowledge it directly, then give a SHORT summary of the approach + ONE generalizable strategy.
Be direct and honest in your judgment. Do not be overly gentle.

Output ONLY the message to the student."""
    message = run_mlx(METACOGNITIVE_MODEL, prompt, 350)
    return {"metacognitive_strategy": message}

def final_response_node(state: TutorState):
    reflection_count = state.get("reflection_count", 0)
    close_msg = state.get("final_response", "")

    # Always force clean close once we reach 2 reflections (orchestrator hard close or normal path)
    if reflection_count >= 2 or "Want to try another problem" in close_msg:
        final = close_msg or "Great job! You solved it. Want to try another problem?"
        print("System:", final)
        return {
            "final_response": final,
            "reflection_count": reflection_count,
            "math_tutor_reasoning": "",
            "metacognitive_strategy": "",
            "next_agent": None,
        }
    if state.get("math_tutor_reasoning") or state.get("metacognitive_strategy"):
        specialist_output = state.get("math_tutor_reasoning") or state.get("metacognitive_strategy")
        history_str = "\n".join(state["history"][-8:])
        prompt = f"""Polish into EXACTLY ONE short student message (1-2 sentences).

Recent conversation:
{history_str}

Specialist internal output:
{specialist_output}

Student's last message: {state['student_input']}
Emotion: {state['student_emotion']}

Rules: When the problem is solved, keep the message SHORT. Only confirm the result or close. Do NOT give full step-by-step verification unless the student specifically asks for it. ONE guiding question or sharp reflection. No full solutions. No LaTeX. Concise.

When polishing MathTutor output:
- NEVER reveal the actual step, conversion, or result (e.g. do not say "convert to 6/8" or "you get 5/8").
- Only turn the "Next content focus" into a question that forces the student to discover it themselves.
- Keep it short and Socratic. If it starts sounding like you're giving the answer, rewrite it.

ABSOLUTE RULE - ZERO TOLERANCE FOR LATEX:
NEVER use $, \\(, \\[, or any LaTeX/math formatting. Write everything in plain text.
If any LaTeX appears, you must rewrite the entire response in plain text before outputting.

Output ONLY the polished message."""
        final = run_mlx(ORCHESTRATOR_MODEL, prompt, 400)
    else:
        final = state.get("final_response", "Let's continue.")

    old_count = state.get("reflection_count", 0)
    next_agent_at_final = state.get("next_agent")
    new_count = old_count
    if next_agent_at_final == "Metacognitive":
        new_count += 1

    log_debug(state, f"[FinalResponse DEBUG] next_agent={next_agent_at_final}, old_count={old_count}, new_count={new_count}")

    # Final LaTeX safety net (expanded to catch more leakage variants)
    import re
    final = re.sub(r'\$.*?\$', '', final)
    final = re.sub(r'\\\(.*?\\\)', '', final)
    final = re.sub(r'\\\[.*?\\\]', '', final)
    final = re.sub(r'\\frac\{[^}]*\}\{[^}]*\}', '', final)
    final = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', final)
    final = re.sub(r'\\\[.*?\\\]', '', final, flags=re.DOTALL)

    print("System:", final)

    if next_agent_at_final == "Metacognitive":
        state["history"].append(f"System (Meta): {final}")
    else: 
        state["history"].append(f"System: {final}")
    if len(state["history"]) > 8:
        state["history"] = state["history"][-8:]

    # Force clean close when reflection loop is done (prevents long summaries and extra meta)
    if old_count >= 2 or next_agent_at_final == "FinalResponse":
        final = "Great job! You solved it. Want to try another problem?"

    return {
        "final_response": final,
        "reflection_count": new_count,
        "math_tutor_reasoning": "",
        "metacognitive_strategy": "",
        "next_agent": None,
    }

# ====================== GRAPH ======================
workflow = StateGraph(TutorState)
workflow.add_node("StateManager", state_manager_node)
workflow.add_node("Affective", affective_node)
workflow.add_node("Orchestrator", orchestrator_node)
workflow.add_node("MathTutor", math_tutor_node)
workflow.add_node("Metacognitive", metacognitive_node)
workflow.add_node("FinalResponse", final_response_node)

workflow.set_entry_point("StateManager")
workflow.add_edge("StateManager", "Affective")
workflow.add_edge("Affective", "Orchestrator")

workflow.add_conditional_edges(
    "Orchestrator",
    lambda state: "FinalResponse" if (state.get("problem_solved", False) and state.get("reflection_count", 0) >= 2)
    else state.get("next_agent", "MathTutor"),
    {
        "MathTutor": "MathTutor",
        "Metacognitive": "Metacognitive",
        "Affective": "Affective",
        "FinalResponse": "FinalResponse",
    }
)

workflow.add_edge("MathTutor", "FinalResponse")
workflow.add_edge("Metacognitive", "FinalResponse")
workflow.add_edge("FinalResponse", END)

graph = workflow.compile()

# ====================== INTERACTIVE ======================

def process_student_turn(current_state: dict, user_input: str) -> dict:
    """
    Clean wrapper around the LangGraph.
    Returns structured output for the UI.
    """
    current_state["student_input"] = user_input
    
    # Run the graph
    result = graph.invoke(current_state)
    current_state.update(result)
    
    # Collect debug logs
    debug_logs = current_state.get("debug_logs", [])
    
    return {
        "response": current_state.get("final_response", ""),
        "emotion": current_state.get("student_emotion", "neutral"),
        "affective_suggestion": current_state.get("affective_suggestion", ""),
        "problem_solved": current_state.get("problem_solved", False),
        "reflection_count": current_state.get("reflection_count", 0),
        "next_agent": current_state.get("next_agent"),
        "debug_logs": debug_logs,
        "current_problem": current_state.get("current_problem"),
        "history": current_state.get("history", []),
    }

if __name__ == "__main__":
    print("Math Tutoring System (v8 - Orchestrator improved) Started. Type 'quit' to exit.\n")
    state: TutorState = {
        "student_input": "", "student_emotion": "neutral", "progress": "beginning",
        "known_mistake": None, "history": [], "orchestrator_instruction": "",
        "math_tutor_reasoning": "", "metacognitive_strategy": "",
        "final_response": "", "problem_solved": False, "reflection_count": 0, "next_agent": None, "current_problem": None
    }
    while True:
        user_input = input("Student: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        state["student_input"] = user_input
        result = graph.invoke(state)
        state.update(result)
    print("Session ended.")
