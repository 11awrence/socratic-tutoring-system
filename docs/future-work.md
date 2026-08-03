# Future Work

The current system is best understood as a prototype for studying prompt-driven multi-agent tutoring.  
Future work falls into two levels: near-term improvements to the existing system, and longer-term research directions.

## Near-term improvements

These are practical next steps that stay close to the current architecture:

- Stronger deterministic routing, so fewer control decisions depend on free LLM judgement
- Better progress and current-step tracking across multi-turn problems
- More reliable solve detection and session closure
- Improved affective adaptation within the limits of the current model setup
- Cleaner support for mathematical notation, including controlled LaTeX use
- Reducing reliance on hard-coded close rules so sessions can end more naturally

## Longer-term research directions

The prototype also points toward broader questions:

- How to balance free agent decisions with explicit control in complex tutoring flows
- Whether models can be trained or adapted specifically for collaborative multi-agent tutoring
- Using stronger cloud-hosted models to test how much of the current brittleness is architectural versus capacity-related
- Experimental evaluation of metacognitive and affective scaffolding with real learners
- Richer learner modelling, including longer-term knowledge tracking across sessions
- Multimodal extension, such as diagram-based geometry support and non-text affect sensing
- More socially present interfaces, for example a live tutor avatar

## Design stance

The near-term work is about making the current prototype more robust.  
The longer-term directions are about testing whether multi-agent tutoring can move from a prompt-engineered demo to a more reliable learning system.