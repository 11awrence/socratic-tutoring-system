# Limitations

This prototype was designed to test how far a multi-agent Socratic tutoring system can go when coordination still depends heavily on prompting. The system works, but several limitations became clear during development and testing.

## Prompt-driven routing

Most routing decisions are made by the Orchestrator through prompting rather than by deterministic control logic.  
This keeps the system flexible, but also makes behaviour less predictable once conversations become long or multi-step. Small changes in wording can lead to different routing choices.

## Unreliable solve detection

Detecting when a student has actually solved the problem remains brittle due to the limitations of the SymPy verification.

The SymPy parsing often fails (`parseable = True` with `error_type = problem_unparseable`) or the math expression never enters the solver. So solve and session-close stay orchestrator-driven. The `problem_solved` flag cannot be trusted on its own. 

In practice, the Metacognitive phase and hard close rules act as safety mechanisms that prevent sessions from drifting indefinitely.


## Weak multi-step tracking

Performance degrades on longer multi-step problems, especially:

- multi-step fraction calculations
- exponent / algebra manipulations

In these cases the system may lose track of the current phase, regress to earlier steps, or drift away from the original problem statement.

## Restricted metacognitive support

Metacognitive reflection is only triggered after a problem is considered solved, and only for up to two turns.  

This restriction was introduced for stability. Allowing the Orchestrator to call the Metacognitive agent freely led to early interruptions and unstable reflection loops — for example, the metacognitive agent could jump in before the student had made any real progress. The trade-off is that the system cannot offer mid-process metacognitive support when a student is stuck.

## Variable metacognitive quality

Even when the Metacognitive agent is triggered at the right time, the usefulness of its reflection prompts can vary across sessions. Some turns produce focused process questions; others are generic or only loosely connected to the student’s actual solution path.

## Fragile state management

Several parts of session state are only weakly controlled:

- state reset (new problem detection) and final answer detection are key-word based in the current system.
- progress / current-step tracking is limited
- some intermediate values were easy to lose across nodes

As a result, the system can occasionally carry context incorrectly between turns or fail to reset cleanly.

## Incomplete error detection

When a student makes multiple mistakes in a single step, the system sometimes catches only one of them.  
Algebraic sign errors, distribution mistakes, and conceptual slips are not always diagnosed together.

## No LaTeX in student-facing responses

For more complex algebra, LaTeX would be useful.  
In practice, model outputs were inconsistent: sometimes valid markup, sometimes broken, sometimes mixed with plain text.

To keep responses stable, the system forces plain text and strips LaTeX if it appears. This improves reliability, but removes a helpful representation for advanced math.

## Lightweight affective modelling

The affective agent runs on a small local model (Qwen2.5-3B).  
It can produce a basic emotion label and suggestion, but the quality of those signals is limited. Larger models improved suggestion quality in isolation, but were not practical here because of memory constraints.

## Forced session close

The final close of a tutoring round is rule-based rather than freely decided by the Orchestrator.  
Once two reflection turns are completed, the system ends the session. This stabilises behaviour, but reduces flexibility.

## Limited question type

The current SymPy verification only handles short arithmetic, algebra and fractions expressions. 
Word problems are not supported by the current system, even after the parsing is fixed.


## Hardware limitation

The reported system uses local MLX models on Apple Silicon. An OpenAI/mock provider switch exists in .env but was not used for the ablation.

## Reflection

The prototype suggests that a multi-agent architecture is a meaningful direction for dialogue-based tutoring. Multi-agent tutors with a separation in math guidance, metacognitive support, and affective signalling surpass a single-agent baseline tutor in error recall, mathematical guidance, metacognitive prompt timing and session close, however, multi-agent tutors are less Socratic and produce more premature answers between steps in comparison to single-agent tutor.

At the same time, the project shows the limits of relying heavily on prompting for coordination.  Routing, phase tracking, and error diagnosis all became fragile once problems required multiple dependent steps. In several cases, stability was achieved only by adding hard constraints, such as delaying metacognitive support until after a solve and forcing session closure after two reflection turns.

The system also highlights the need for stronger grounding. Without a functional verification layer, the decisions are still made by LLM therefore the tutor can accept or build on incorrect intermediate conclusions. Local model capacity further constrained mid-process support: the architecture can be demonstrated with smaller models, but more reliable guidance likely requires stronger models or better structured control.

Making agent activity visible through the side panel was valuable not only for end users, but also for understanding system failures during development. Likewise, the clean separation between backend, API, and UI made debugging and iteration much easier than working inside a single mixed script.

Overall, the work indicates that multi-agent tutoring is promising, but robust behaviour will depend on a better balance between prompt-driven agency and explicit control over task flow.