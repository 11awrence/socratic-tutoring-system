# How it Works

This page walks through a typical tutoring session and shows what the system surfaces to the user.

## Typical tutoring session

1. The student submits a math problem.
2. The system detects a new problem and resets relevant state.
3. The Affective agent produces a lightweight emotion + suggestion signal.
4. The Orchestrator decides the next focus and routes to the MathTutor.
5. The MathTutor generates a Socratic micro-step.
6. The Final Response node polishes that step into a short student-facing message.
7. Once the problem is considered solved, the Metacognitive agent runs for up to two reflection turns.
8. The session closes with an invitation to try another problem.

<figure>
  <img src="../assets/close.png" alt="Chat close interface" width="600">
  <figcaption>Close of a tutoring session.</figcaption>
</figure>

### Starting a new problem

The system uses a simple heuristic to detect when the student has started a new problem (based on message length and certain request-style phrases). When this happens, relevant session state is reset. 

This is a pragmatic mechanism rather than a robust problem-segmentation model.


## Example interaction

A typical early exchange looks like this:

**Student:** How do I solve 2x + 3 = -2x - 6?

**Tutor:** Try adding 2x to both sides to group the variable terms. What does the equation look like after you do that?

The system continues with short Socratic prompts rather than full solutions, unless the student is reflecting after a completed answer.

<figure>
  <img src="../assets/main_chat.png" alt="Main chat interface" width="600">
  <figcaption>Main chat interface with learner interaction.</figcaption>
</figure>

## What the side panel shows

The Chainlit interface keeps the main chat focused on the tutoring dialogue.  
Additional information is available on demand through the side panel:

- **Session status** — current problem, reflection count, solved state
- **Affective state** — detected emotion and suggestion
- **Agent activity** — Orchestrator plan and specialist output
- **Debug** (optional) — recent internal logs

This separation keeps the learning interface relatively clean while still making the multi-agent behaviour inspectable.
<figure>
  <img src="../assets/side_panel1.png" alt="Side panel with agent activity" width="700">
  <figcaption>Side panel showing session status and affective state.</figcaption>
</figure>
<figure>
  <img src="../assets/side_panel2.png" alt="Side panel with agent activity" width="700">
  <figcaption>Side panel showing agent activity.</figcaption>
</figure>