# Weekly Plan & Progress Report — Week 03

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Nov 15, 2026 – Nov 21, 2026  
**Status:** In Progress / Ready for Execution  
**Milestone:** Phase 3 — LangGraph Multi-Agent Architecture & Conversational Query Agent  

---

## 1. Objectives & Scope
1. Implement the request-scoped **LangGraph Supervisor** (`agents/supervisor/`) managing shared `AgentState`.
2. Connect multi-provider LLM gateway (`agents/common/llm_client.py`) supporting **Groq**, **Google Gemini**, **Ollama**, and **Anthropic**.
3. Enforce **live date/time injection** across system prompts and state so agents resolve relative queries ('today', 'tomorrow', 'next class') deterministically.
4. Ground all Query Agent responses strictly in SQLite `data/campus.db` (zero hallucination / never answering from LLM memory).

---

## 2. 5-Member Team Work Division

| Teammate | Focus Area | Planned Deliverables |
|---|---|---|
| **S1 (Architect)** | LangGraph Supervisor | StateGraph compile, conditional edge dispatch, request-scoped context. |
| **S2 (Operations)** | Query Tools | Academic calendar, syllabus, and course instructor lookup tools. |
| **S3 (Agent & NLP)** | Query Agent Node | Multi-provider tool-call loop, prompt engineering, grounded response formatting. |
| **S4 (Facilities)** | Room Query Tools | Room/lab details, campus facility inventory, availability lookups. |
| **S5 (QA & Eval)** | Query Test Suite | 30 test queries spanning student, faculty, and administrator personas. |

---

## 3. Key Milestone Deliverables
- [ ] `agents/supervisor/agent.py` compiled StateGraph routing between Query Agent and polite exit.
- [ ] `agents/common/llm_client.py` operational with Groq/Gemini/Ollama/Anthropic fallbacks.
- [ ] Verified responses for student queries ("What is my next class?", "Where is LAB-101?").
- [ ] Automated regression tests in `tests/agents/test_query_agent.py`.

