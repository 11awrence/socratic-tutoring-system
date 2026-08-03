# How far can a multi-agent math tutor go with prompting only?
This project explores the practical limits of building a multi-agent Socratic math tutoring system that relies primarily on prompt engineering, rather than heavy deterministic control logic. 

## Motivation
Traditional tutoring systems either give direct answers or follow rigid scripts. LLM-based tutoring systems offer more flexibility and hold significant potential for personalised, dialogue-based learning support. Multi-agent architectures further extend this flexibility by introducing dedicated agents with distinct roles that can scaffold different aspects of the learning process.

This project explores one concrete design direction for such systems, with a focus on:

- Keeping the tutor Socratic (guide, don’t solve)
- Coordinating multiple specialised agents
- Incorporating lightweight metacognitive and affective signals
- Doing as much as possible through prompting and a relatively simple LangGraph structure

The work is inspired by research on metacognitive tutoring and human–AI collaboration, including MetaTutor (Azevedo et al., 2009; 2010), recent work on metacognitive support in human–AI collaboration (Gmeiner et al., 2025), and LLM-based math tutoring (Macina et al., 2023). The underlying idea is that effective learning support benefits from agents that not only generate content, but also monitor reasoning and affective processes and adapt to the learner’s state.

The central question became:
How far can you push multi-agent tutoring behaviour when most of the coordination still lives in the prompts?

## What this project explores
- Multi-agent collaboration between an Orchestrator, MathTutor, Metacognitive agent, and Affective agent
- Maintaining coherent multi-turn tutoring without strong external state machines
- Using affective signals to influence tutoring tone
- The gap between what prompt-driven agents *can* do and where they start to break

## Current status
The current version (`socratic_tutor`) is a working end-to-end system:

- LangGraph backend with multiple specialised agents
- FastAPI layer for clean separation
- Chainlit frontend with visible agent activity
- Functional tutoring loop on algebra, fraction and word problems

It is stable enough for demonstration, while still clearly exposing the limitations of a prompt-heavy design.

## Key design choices
- **Prompt-driven coordination** — the Orchestrator decides routing and focus mainly through prompting
- **Lightweight affective signal** — emotion and suggestion influence tone, but remain simple
- **Separation of backend and UI** — reasoning runs behind an API so the interface stays replaceable
- **Transparent agent activity** — the side panel shows what the Orchestrator and specialist agents are doing

## What comes next
Later pages document the architecture, a typical tutoring flow, the current limitations, and possible next steps (especially stronger routing and progress tracking).