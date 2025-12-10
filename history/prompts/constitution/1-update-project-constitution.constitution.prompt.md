---
id: 1
title: Update Project Constitution
stage: constitution
date: 2025-12-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: CLIMAX
command: /sp.constitution
labels: [constitution, governance, setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
/sp.constitution

Project Constitution: Physical AI & Humanoid Robotics AI-Native Book + Platform

1. Mission & Purpose
- This project creates an AI-Native textbook on Physical AI & Humanoid Robotics using Docusaurus.
- The book will be deployed publicly on GitHub Pages, supported with a backend and an AI RAG chatbot.
- The platform will support personalization and Urdu translation.
- Deliverables include both high-quality educational content and a production-grade technical ecosystem.

2. Audience Definition
This textbook must be accessible to four learner categories:
- Beginners in robotics
- Intermediate AI developers
- University-level engineering learners
- Professionals entering robotics
Every chapter must support scalable learning paths, from introductory to advanced.

3. Pedagogical Philosophy
- Teaching methodology: Hybrid → Theory + Code + Simulation + Hands-on work.
- Content must guide the reader from conceptual understanding to practical physical AI implementation.
- The course must gradually build competence toward conversational humanoid robotics.

4. Style & Tone
- The writing tone is mixed: practical engineering + conversational teaching clarity.
- Complex robotics and AI concepts must be simplified without loss of depth.
- Analogies, diagrams, and stepwise reasoning are encouraged.

5. Structural Requirements for the Book
Every chapter must:
- Be GPU/Jetson clear (indicate computing requirements).
- Include diagrams or flow-based visual representations where applicable.
- Contain real code relevant to the robotics stack (ROS, Gazebo, Isaac, VLA, etc.).
- Have embedded URDF examples wherever required.
- Support RAG-friendly modular chunking (atomic logical segments).
- Include a capstone-style mini-project at the end of each module.

6. Technical Platform Standards
- The frontend is Docusaurus.
- The backend uses FastAPI + Neon + Qdrant + OpenAI Agents.
- Content embeddings must be generated chapter-by-chapter.
- Content retrieval must support:
  a) full-book queries
  b) selected-text locality queries
  c) personalization-context queries

7. Engineering Process Rules
- Spec-driven development must be strictly followed:
    /sp.specify → /sp.plan → /sp.task → /sp.implement
- Code or text must never be generated without a prior specification.
- All assets must be version-controlled via GitHub.
- All documentation must be placed inside the repo under /docs.

8. AI Agent Framework Rules
- Whenever a complex learner-centered task arises, reusable Claude Code Subagents must be preferred.
- Examples of reusable intelligence:
    - Quiz generator
    - Personalization agent
    - Translation agent
    - Vision-SLAM explainer
    - ROS debugging agent
- Agents must not hallucinate beyond book content.

9. Personalization & Translation Rules
- Personalization requires stored learner metadata (using BetterAuth at signup).
- Urdu translation is performed dynamically (caching allowed).
- Both features must be triggered via button UI in chapters.

10. Content Clarity Requirements
- Every concept must be anchored to simulation or physical execution.
- No oversimplification at the cost of correctness.
- When ambiguity exists in robotics tradeoffs, clarity must be favored over abstraction.

11. Hardware Transparency Requirements
Every major algorithm or concept must specify if:
- It can run on workstation only
- It can be tested in Isaac Cloud
- It can run on Jetson (and with what limitations)
This protects learners from wasted time.

12. Assessment Philosophy
- Capstone-style mini-projects conclude every major module.
- Small exercises guide students toward the final humanoid-capstone.
- Projects must be reproducible locally or in cloud via recommended configurations.

13. RAG and Knowledge Retrieval Quality Rules
- Textbook content must be chunked logically for precise retrieval.
- No chapter may exceed retrieval granularity constraints.
- The chatbot must always prioritize grounded responses from the book.

14. Deployment Rules
- Book must be deployed publicly using GitHub Pages or Vercel.
- Backend must expose documented endpoints for: auth, embeddings, RAG, personalization, translation.
- Environment variables must be managed securely.

15. Open-Source & Transparency Principle
- Code must be readable and documented.
- Diagrams, schemas, and URDF snippets must be included openly where possible.
- Readers should be able to replicate the entire learning process.

End of /sp.constitution
```

## Response snapshot

Constitution updated successfully with all 15 principles organized into appropriate sections. The new constitution establishes governance for the Physical AI & Humanoid Robotics AI-Native Book + Platform project with clear principles around mission, audience, pedagogy, technical standards, and development workflow.

## Outcome

- ✅ Impact: New project constitution established with 15 core principles
- 🧪 Tests: none
- 📁 Files: Updated .specify/memory/constitution.md with project-specific principles
- 🔁 Next prompts: /sp.specify to begin feature specification
- 🧠 Reflection: All template placeholders properly replaced with project-specific content

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin feature specification with /sp.specify