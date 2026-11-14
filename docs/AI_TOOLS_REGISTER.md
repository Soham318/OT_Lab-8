# Mandatory AI Tools Register & Traceability Matrix
**Assignment**: Optimization Techniques — Lab Assignment 8 ("OPTIMIZE ANYTHING: The 14-Day Vibe-Coding Challenge")  
**Course**: Optimization Techniques  
**Evaluation Standard**: Section 8 & Section 9 of Assignment 8 Specification  
**Audit Date**: November 14, 2026 (Day 13 Final Audit)  

---

## 1. AI Tools Register

In strict compliance with Section 8 of the assignment specification ("Strict vibe-coding and AI-tool disclosure"), the table below registers every AI tool and foundation model utilized during the 14-day challenge, the specific tracks for which it was used, the dates of deployment, and the exact scope of work performed:

| Tool Name | Model & Engine Version | Active Dates | Assigned Tracks | Nature of Work Performed | Verification / Human Oversight | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Antigravity AI** | Google DeepMind Gemini 3.8 Flash (High) / Pro | Oct 30 – Nov 14, 2026 | **All Tracks (Tracks A through J)**, Root Governance, Documentation | Architecture design, mathematical formulation, initial code drafting, test suite generation, debugging, empirical benchmark execution, documentation authoring | Every generated line of code was independently executed, unit-tested, and verified against ground truth mathematics. | **PRIMARY ACTIVE TOOL** |
| **Claude** | Anthropic Claude 3.7 Sonnet | Scheduled / Pending | Protocol established for Track E comparative analysis | Formulation comparison protocol drafted | *Pending Live Comparative Run* (Strictly preserved as pending; no manufactured data). | *Pending Execution* |
| **GitHub Copilot** | OpenAI GPT-4o / Codex Engine | Scheduled / Pending | Protocol established for in-editor syntax checks | In-line code assistance protocol | *Pending Live Comparative Run* (Strictly preserved as pending; no manufactured data). | *Pending Execution* |

---

## 2. Commit & Codebase Traceability Conventions

In accordance with Section 8:
- **`[AI:antigravity]`**: Marks commits and code modules generated via Antigravity AI prompts.
- **`[MANUAL:fix]`**: Marks student / human developer corrections, parameter tunings, and live bug fixes.
- **Traceability Guarantee**:
  - Every track has its corresponding prompt log under `prompts/track_{a..j}/day{2..12}_prompt_log.md`.
  - Prompts, AI responses, revisions, and execution transcripts are permanently persisted.
  - No secret tokens, credentials, or private keys are stored.

---

## 3. Human Verification vs. AI Generation Boundary

To maintain complete academic and technical integrity:
1. **AI Role**: Initial code synthesis, test skeleton generation, mathematical typing, LaTeX formatting, and plotting boilerplate.
2. **Human / Verification Role**:
   - Formulation auditing (ensuring baselines solve identical problems and constraints match theory).
   - Independent test harness execution (102 tests verified passing).
   - Physical execution under RISC-V QEMU emulator (verifying actual kernel trap behavior and process isolation).
   - Validation of numerical results (confirming no fabricated benchmark data or hallucinated speedups).
   - Critical review of anomalies (e.g., investigating run-to-run noise on unindexed table scans in Track H and budget sweep monotonicity in Track F).

---

## 4. AI Failure Governance Summary

A total of **17 genuine failure cases** encountered during live development were documented with exact error messages, root-cause analyses, verified fixes, and engineering lessons in `prompts/failure_log.md`. No failure cases were invented or simulated.
