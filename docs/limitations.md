# Limitations

This prototype was designed to test how far a multi-agent Socratic tutoring system can go when coordination still depends heavily on prompting. The system works, but several limitations became clear during development and testing.

## Prompt-driven routing

Most routing decisions are made by the Orchestrator through prompting rather than by deterministic control logic.  
This keeps the system flexible, but also makes behaviour less predictable once conversations become long or multi-step. Small changes in wording can lead to different routing choices.

## Unreliable solve detection

Detecting when a student has actually solved the problem remains brittle.  
The system cannot fully trust the Orchestrator’s `problem_solved` judgement on its own. In practice, the Metacognitive phase and hard close rules act as safety mechanisms that prevent sessions from drifting indefinitely.

## Weak multi-step tracking

Performance degrades on longer multi-step problems, especially:

- word problems
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

- new-problem detection relies on simple heuristics
- progress / current-step tracking is limited
- some intermediate values were easy to lose across nodes

As a result, the system can occasionally carry context incorrectly between turns or fail to reset cleanly.

## Incomplete error detection

When a student makes multiple mistakes in a single step, the system often catches only one of them.  
Algebraic sign errors, distribution mistakes, and conceptual slips are not always diagnosed together.

## No LaTeX in student-facing responses

For more complex algebra, LaTeX would be useful.  
In practice, model outputs were inconsistent: sometimes valid markup, sometimes broken, sometimes mixed with plain text.

To keep responses stable, the system forces plain text and strips LaTeX if it appears. This improves reliability, but removes a helpful representation for advanced math.

## Lightweight affective modelling

The affective agent runs on a small local model.  
It can produce a basic emotion label and suggestion, but the quality of those signals is limited. Larger models improved suggestion quality in isolation, but were not practical here because of memory constraints.

## Forced session close

The final close of a tutoring round is rule-based rather than freely decided by the Orchestrator.  
Once two reflection turns are completed, the system ends the session. This stabilises behaviour, but reduces flexibility.

## Limited verification

An earlier verification layer was removed because it conflicted with fluent tutoring behaviour.  
The current system therefore relies mainly on prompt-level judgements rather than an independent check of final answers.

## Reflection

The prototype suggests that a multi-agent architecture is a meaningful direction for dialogue-based tutoring. Separating Socratic guidance, metacognitive reflection, and affective signalling already creates a more structured learning interaction than a single undifferentiated tutor model.

At the same time, the project shows the limits of relying heavily on prompting for coordination. Routing, phase tracking, and error diagnosis all became fragile once problems required multiple dependent steps. In several cases, stability was achieved only by adding hard constraints, such as delaying metacognitive support until after a solve and forcing session closure after two reflection turns.

The system also highlights the need for stronger grounding. Without an independent verification layer, the tutor can accept or build on incorrect intermediate conclusions. Local model capacity further constrained mid-process support: the architecture can be demonstrated with smaller models, but more reliable guidance likely requires stronger models or better structured control.

Making agent activity visible through the side panel was valuable not only for end users, but also for understanding system failures during development. Likewise, the clean separation between backend, API, and UI made debugging and iteration much easier than working inside a single mixed script.

Overall, the work indicates that multi-agent tutoring is promising, but robust behaviour will depend on a better balance between prompt-driven agency and explicit control over task flow.