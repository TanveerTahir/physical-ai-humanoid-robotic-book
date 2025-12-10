<!-- SYNC IMPACT REPORT
Version change: N/A -> 1.0.0
List of modified principles: N/A (new constitution)
Added sections: All principles and sections for Physical AI & Humanoid Robotics project
Removed sections: Template placeholder sections
Templates requiring updates: N/A
Follow-up TODOs: None
-->

# Physical AI & Humanoid Robotics AI-Native Book + Platform Constitution

## Core Principles

### I. Mission & Purpose
This project creates an AI-Native textbook on Physical AI & Humanoid Robotics using Docusaurus. The book will be deployed publicly on GitHub Pages, supported with a backend and an AI RAG chatbot. The platform will support personalization and Urdu translation. Deliverables include both high-quality educational content and a production-grade technical ecosystem.

### II. Audience Definition
This textbook must be accessible to four learner categories: Beginners in robotics, Intermediate AI developers, University-level engineering learners, and Professionals entering robotics. Every chapter must support scalable learning paths, from introductory to advanced.

### III. Pedagogical Philosophy (NON-NEGOTIABLE)
Teaching methodology: Hybrid → Theory + Code + Simulation + Hands-on work. Content must guide the reader from conceptual understanding to practical physical AI implementation. The course must gradually build competence toward conversational humanoid robotics.

### IV. Style & Tone
The writing tone is mixed: practical engineering + conversational teaching clarity. Complex robotics and AI concepts must be simplified without loss of depth. Analogies, diagrams, and stepwise reasoning are encouraged.

### V. Structural Requirements for the Book
Every chapter must: Be GPU/Jetson clear (indicate computing requirements), include diagrams or flow-based visual representations where applicable, contain real code relevant to the robotics stack (ROS, Gazebo, Isaac, VLA, etc.), have embedded URDF examples wherever required, support RAG-friendly modular chunking (atomic logical segments), and include a capstone-style mini-project at the end of each module.

### VI. Technical Platform Standards
The frontend is Docusaurus. The backend uses FastAPI + Neon + Qdrant + OpenAI Agents. Content embeddings must be generated chapter-by-chapter. Content retrieval must support: a) full-book queries, b) selected-text locality queries, c) personalization-context queries.

## Additional Constraints

### Content Clarity Requirements
Every concept must be anchored to simulation or physical execution. No oversimplification at the cost of correctness. When ambiguity exists in robotics tradeoffs, clarity must be favored over abstraction.

### Hardware Transparency Requirements
Every major algorithm or concept must specify if: It can run on workstation only, It can be tested in Isaac Cloud, It can run on Jetson (and with what limitations). This protects learners from wasted time.

### AI Agent Framework Rules
Whenever a complex learner-centered task arises, reusable Claude Code Subagents must be preferred. Examples of reusable intelligence: Quiz generator, Personalization agent, Translation agent, Vision-SLAM explainer, ROS debugging agent. Agents must not hallucinate beyond book content.

## Development Workflow

### Engineering Process Rules
Spec-driven development must be strictly followed: /sp.specify → /sp.plan → /sp.task → /sp.implement. Code or text must never be generated without a prior specification. All assets must be version-controlled via GitHub. All documentation must be placed inside the repo under /docs.

### Assessment Philosophy
Capstone-style mini-projects conclude every major module. Small exercises guide students toward the final humanoid-capstone. Projects must be reproducible locally or in cloud via recommended configurations.

### RAG and Knowledge Retrieval Quality Rules
Textbook content must be chunked logically for precise retrieval. No chapter may exceed retrieval granularity constraints. The chatbot must always prioritize grounded responses from the book.

## Governance

Personalization requires stored learner metadata (using BetterAuth at signup). Urdu translation is performed dynamically (caching allowed). Both features must be triggered via button UI in chapters. Deployment rules: Book must be deployed publicly using GitHub Pages or Vercel. Backend must expose documented endpoints for: auth, embeddings, RAG, personalization, translation. Environment variables must be managed securely. Code must be readable and documented. Diagrams, schemas, and URDF snippets must be included openly where possible. Readers should be able to replicate the entire learning process.

**Version**: 1.0.0 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-10