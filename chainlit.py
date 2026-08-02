import chainlit as cl
import requests

API_URL = "http://localhost:8000/turn"


def get_initial_state():
    return {
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


def call_tutor(user_input: str, current_state: dict) -> dict:
    payload = {
        "student_input": user_input,
        "state": current_state,
    }
    r = requests.post(API_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


async def open_details_sidebar(state: dict, result: dict = None, show_debug: bool = False):
    emotion = (result or {}).get("emotion") or state.get("student_emotion", "neutral")
    suggestion = (result or {}).get("affective_suggestion") or state.get("affective_suggestion") or "-"
    current_problem = state.get("current_problem") or state.get("original_problem") or "None"
    reflection = state.get("reflection_count", 0)
    solved = "Yes" if state.get("problem_solved") else "No"
    next_agent = state.get("next_agent") or "-"

    specialist = (
        state.get("math_tutor_reasoning")
        or state.get("metacognitive_strategy")
        or next_agent
        or "-"
    )

    orch = "-"
    logs = (result or {}).get("debug_logs") or state.get("debug_logs") or []
    for log in logs:
        if "Orchestrator (plan)" in log or '"next_agent"' in log:
            orch = log[:450] + ("..." if len(log) > 450 else "")
            break

    content = (
        "### Session Status\n"
        f"**Current Problem:** {current_problem}\n"
        f"**Reflection count:** {reflection}\n"
        f"**Solved:** {solved}\n\n"
        "### Affective State\n"
        f"**Emotion:** {emotion}\n"
        f"**Suggestion:** {suggestion}\n\n"
        "### Agent Activity\n"
        f"**Orchestrator:**\n{orch}\n\n"
        f"**Specialist:**\n{specialist}\n"
    )

    if show_debug:
        # Filter out Orchestrator plan lines (already shown in Agent Activity)
        filtered_logs = [
            log for log in logs
            if "Orchestrator (plan)" not in log and '"next_agent"' not in log
            ]
        debug_text = "\n".join(filtered_logs[-8:]) if filtered_logs else "No debug logs."
        content += (
            "\n### Debug\n"
            "```text\n"
            f"{debug_text}\n"
            "```\n"
        )

    await cl.ElementSidebar.set_title("Multi-agent details")
    await cl.ElementSidebar.set_elements([
        cl.Text(name="details", content=content, display="side")
    ])


@cl.on_chat_start
async def start():
    state = get_initial_state()
    cl.user_session.set("state", state)
    cl.user_session.set("last_result", None)
    cl.user_session.set("show_debug", False)

    actions = [
        cl.Action(name="new_problem", payload={"value": "new"}, label="🔄 New Problem")
    ]

    await cl.Message(
        content="Hi! I'm your multi-agent math tutor. What would you like to work on?",
        actions=actions,
    ).send()


@cl.action_callback("new_problem")
async def on_new_problem(action):
    state = get_initial_state()
    cl.user_session.set("state", state)
    cl.user_session.set("last_result", None)

    actions = [
        cl.Action(name="new_problem", payload={"value": "new"}, label="🔄 New Problem")
    ]

    await cl.Message(
        content="Session cleared. Ready for a new problem! What would you like to work on?",
        actions=actions,
    ).send()


@cl.action_callback("show_details")
async def on_show_details(action):
    state = cl.user_session.get("state")
    result = cl.user_session.get("last_result")
    show_debug = cl.user_session.get("show_debug", False)
    await open_details_sidebar(state, result, show_debug=show_debug)


@cl.action_callback("toggle_debug")
async def on_toggle_debug(action):
    current = cl.user_session.get("show_debug", False)
    cl.user_session.set("show_debug", not current)

    state = cl.user_session.get("state")
    result = cl.user_session.get("last_result")
    await open_details_sidebar(state, result, show_debug=not current)


@cl.on_message
async def main(message: cl.Message):
    state = cl.user_session.get("state")

    thinking = await cl.Message(content="Thinking…", author="Tutor").send()
    await thinking.send()

    try:
        result = call_tutor(message.content, state)
        state = result["state"]
        cl.user_session.set("state", state)
        cl.user_session.set("last_result", result)

        response = result.get("response") or "Sorry, I couldn't generate a response."

        thinking.content = response
        await thinking.update()

        actions = [
            cl.Action(name="new_problem", payload={"value": "new"}, label="🔄 New Problem"),
            cl.Action(name="show_details", payload={"value": "details"}, label="🧠 Multi-agent details"),
            cl.Action(name="toggle_debug", payload={"value": "debug"}, label="🛠️ Toggle Debug"),
        ]
        await cl.Message(content="", actions=actions).send()

    except Exception as e:
        thinking.content = f"An error occurred: {str(e)}"
        await thinking.update()
