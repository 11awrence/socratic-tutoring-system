# How it Works

This page walks through a typical tutoring session and shows what the system surfaces to the user.

## Typical tutoring session (multi_verifier mode)

1. The student submits a math problem.
2. The system detects a new problem and resets relevant state.
3. The SymPy attempts to provide mathematical signal, if parsing fails, the solve/close will be decided by the Orchestrating Agent.
4. The Learner-support (Affective) Signal produces a lightweight emotion + suggestion signal.
5. The Orchestrating Agent decides the next focus and routes to the MathTutor.
6. The Math Reasoning Agent generates a Socratic micro-step.
7. The `FinalResponse` node polishes that step into a short student-facing message.
9. Once the problem is considered solved, the Metacognitive Support agent runs for up to two reflection turns.
10. The session closes with an invitation to try another problem.

### Starting a new problem

The system uses a simple heuristic to detect when the student has started a new problem (based on message length and certain request-style phrases). When this happens, relevant session state is reset. 

This is a pragmatic mechanism rather than a robust problem-segmentation model.

The "New Problem" button resets the state for demo purposes.


## Example interaction

Before the session starts, the student needs to select a mode from the chooser. The default is "multi_verifier"

<figure>
  <img src="../assets/mode_setting.png" alt="Mode Picker" width="600">
  <figcaption>Mode picker for ablation.</figcaption>
</figure>


A typical early exchange looks like this:

**Student:** How do I solve 3/4 - 1/6?

**Tutor:** To subtract these fractions, what is the smallest number that both 4 and 6 divide into evenly?

The system continues with short Socratic prompts rather than full solutions, unless the student is reflecting after a completed answer.

<figure>
  <img src="../assets/main_chat.png" alt="Main chat interface" width="600">
  <figcaption>Main chat interface with learner interaction.</figcaption>
</figure>

## What the side panel shows

The Chainlit interface keeps the main chat focused on the tutoring dialogue.  
Additional information is available on demand through the side panel:

- **Mode:** — `multi_verifier`/`multi`/`single`
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
<figure>
  <img src="../assets/close.png" alt="Chat close interface" width="600">
  <figcaption>Close of a tutoring session.</figcaption>
</figure>