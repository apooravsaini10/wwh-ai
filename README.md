# WWH Framework — Artificial General Intelligence

> *"True intelligence is not defined by what it knows. It is defined by how deeply it understands — and how wisely it responds."*
> — Apoorav Saini, 2026

---

## What Is This?

The WWH Framework is an original theoretical architecture for Artificial General Intelligence, conceived and built by **Apoorav Saini** (Independent Researcher, India) in May 2026.

Unlike current AI systems that operate through statistical pattern matching, the WWH Framework is built on the three fundamental questions that underpin all human cognition:

- **WHAT** — What is this? (Identity and understanding)
- **WHY** — Why does this exist? (Cause and meaning)
- **HOW** — How does this work? (Process and mechanism)

---

## The Core Idea

Current AI stores knowledge as data.
WWH stores knowledge as **understanding.**

Current AI responds to words.
WWH responds to **intent.**

Current AI requires retraining to improve.
WWH **teaches itself.**

---

## Features

- ✅ **Stage 0 — Identity Layer** — The AI knows what it is, why it exists, and how it thinks before learning anything
- ✅ **Stage 1 — WWH Thinking Engine** — Every response structured through What, Why, How
- ✅ **Stage 2 — Self Validation** — Validates its own answers against real world data automatically
- ✅ **Intent Recognition Engine** — Reads the purpose behind every question, not just the words
- ✅ **Persistent Memory** — Remembers everything permanently using a knowledge graph (Neo4j)
- ✅ **Self Improving Loop** — Compares new answers to old ones, keeps the better knowledge
- ✅ **Stage 3 — Autonomous Learning** — Finds its own knowledge gaps and teaches itself without being asked

---

## Architecture
Input
↓
Intent Recognition — reads purpose behind the question
↓
Memory Recall — applies relevant past learnings
↓
WWH Thinking — What / Why / How structured reasoning
↓
Self Validation — checks answer against real world data
↓
Self Improvement — keeps the better answer permanently
↓
Persistent Memory — stores everything in knowledge graph
↓
Output
---

## Quick Start

### Requirements
- Python 3.11+
- Neo4j Desktop
- Groq API key (free at console.groq.com)

### Installation

```bash
git clone https://github.com/apooravsaini10/wwh-ai.git
cd wwh-ai
python3 -m venv wwh_env
source wwh_env/bin/activate
pip3 install groq requests python-dotenv rich wikipediaapi neo4j flask
```

### Setup

Create a `.env` file:
GROQ_API_KEY="your_groq_api_key"
INTENT_THRESHOLD=0.7
Start Neo4j Desktop and create a database called `wwh_memory` with your password.

Update the password in `wwh_ai.py` and `memory_map.py`.

### Run

```bash
python3 wwh_ai.py
```

### Commands

| Command | Action |
|---|---|
| Ask anything | Full WWH thinking + validation |
| `learn` | 3 cycles of autonomous learning |
| `learn 5` | Custom cycles of autonomous learning |
| `memory` | View all past learnings |
| `exit` | Shutdown |

---

## The Four Stages

| Stage | Name | Status |
|---|---|---|
| Stage 0 | Identity Establishment | ✅ Complete |
| Stage 1 | Guided Learning | ✅ Complete |
| Stage 2 | Validated Independent Thinking | ✅ Complete |
| Stage 3 | Autonomous Intelligence | ✅ Complete |

---

## Research Paper

The full theoretical concept paper is available at:
**[Internet Archive — WWH Framework Apoorav Saini 2026](https://archive.org/details/wwh-framework-apoorav-saini-2026)**

---

## License

This project is licensed under **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International.**

- ✅ You may view and study this work
- ✅ You must credit Apoorav Saini in any reference
- ❌ You may not use this commercially without permission
- ❌ You may not modify and redistribute this work

© Apoorav Saini, 2026. All rights reserved.

---

## Author

**Apoorav Saini**
Student & Independent Researcher
India, 2026

*This framework was conceived entirely through independent reasoning and original thought.*

---

## Contact

For licensing, collaboration, or research inquiries — raise an issue on this repository.