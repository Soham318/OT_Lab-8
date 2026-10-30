# AI Tool Comparison Study & Protocol

> **Requirement**: Section 8 of Assignment 8 Specification  
> **Mandate**: Compare at least two AI tools on one concrete task, noting correctness, hallucinations, speed, and the number of prompt iterations needed.  
> **Status**: Protocol Defined; Baseline Established with Antigravity AI; Secondary Tool Comparison Scheduled for Track E.

---

## 1. AI Tools Actually Used Record

| Tool Name | Model & Engine | Active Period | Tracks / Tasks | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Antigravity AI** | Gemini 3.8 Flash (High) / Pro | Oct 30 – Oct 31, 2026 | Architecture, Environment Verification, Planning, Checklists | **Active & Verified** |
| **Claude** | Claude 3.7 Sonnet | Scheduled (Phase 2) | Track E Railway Formulation Comparison | *Pending Execution* |
| **GitHub Copilot** | GPT-4o / Codex engine | Scheduled (Phase 3) | Track G / H In-editor assistance | *Pending Execution* |

---

## 2. Benchmark Task Specification

* **Task**: Mathematical formulation and solver implementation of the **Railway Route and Transfer Optimization Problem (Track E)** on a time-expanded timetable network.
* **Input Prompt**: Standardized formulation prompt defining passenger stations, timetable train segments, minimum transfer buffers, and multi-objective criteria ($\min \alpha \cdot \text{journey} + \beta \cdot \text{wait} + \gamma \cdot \text{transfers}$).

---

## 3. Evaluation Dimensions

When comparing the primary AI tool (Antigravity AI) against the secondary AI tool (Claude), the following empirical metrics will be tracked:
1. **Mathematical Correctness**: Does the formulation respect flow conservation and timetable consistency without non-linear hacks or invalid big-$M$ relaxations?
2. **Hallucinations & False Claims**: Does the tool invent non-existent API parameters (e.g. invalid arguments in `scipy.optimize.milp`) or make false claims about algorithmic guarantees (e.g. claiming static Dijkstra solves dynamic timetable transfer buffers directly)?
3. **Prompt Iteration Count**: How many conversational rounds and prompt revisions are required before reaching a verified, working implementation?
4. **Wall-Clock Latency**: Response generation time per prompt.
5. **Code Maintainability & Cleanliness**: Use of vectorized operations, docstrings, type annotations, and unit testability.

---

## 4. Initial Baseline Assessment (Antigravity AI)

* **Formulation Generated**: Pure 0-1 Binary Integer Linear Program using time-expanded network edges ($x_e \in \{0, 1\}$) and transfer indicators ($y_{s, k_1, k_2} \in \{0, 1\}$).
* **Constraints Defined**: Flow conservation on time-expanded nodes, timetable buffer satisfaction pre-filtered during graph construction, transfer count limits.
* **Integrations**: Direct compatibility with `scipy.optimize.milp` (HiGHS solver).
* **Iterations**: 1 prompt iteration.
* **Hallucinations Observed**: None. Correctly noted that static Dijkstra cannot handle dynamic transfer delays without graph expansion.

*(The secondary comparison with Claude will be executed and recorded under this section during Track E implementation).*
