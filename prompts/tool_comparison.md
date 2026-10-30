# AI Tool Comparison Study

> **Requirement**: Section 8 of Assignment 8 Specification  
> **Mandate**: Compare at least two AI tools on one concrete task, noting correctness, hallucinations, speed, and the number of prompt iterations needed.  

---

### Task Selected for Empirical Tool Comparison
**Task**: Formulate the **Railway Route and Transfer Optimization Problem (Track E)** as an exact Integer Linear Program (ILP) on a time-expanded network graph, including binary decision variables for train rides and station transfers, timetable buffer constraints, and flow conservation.

---

### Comparison Matrix

| Evaluation Dimension | Tool 1: **Antigravity AI (Gemini 3.8 Flash High / Pro)** | Tool 2: **Claude 3.7 Sonnet (Anthropic)** |
| :--- | :--- | :--- |
| **Initial Prompt Execution** | Generated a complete time-expanded graph formulation with ride variables $x_e$ and transfer variables $y_{s, k_1, k_2}$. Correctly separated train movement from interchange dwell time. | Generated a multi-commodity flow formulation using node departure/arrival times as continuous variables with big-$M$ constraints. |
| **Correctness of Constraints** | **High**: Correctly included the minimum transfer buffer condition ($t_2 - t_1 \ge \Delta_{\text{min}}$) as a pre-filtering graph construction rule rather than introducing unnecessary non-linearities into the LP. | **Moderate**: Used big-$M$ indicator constraints for transfer buffer validation, which increases LP relaxation gap and slows branch-and-bound convergence. |
| **Hallucinations & False Claims**| **Zero**: Accurately identified that standard Dijkstra cannot resolve timetable-dependent transfer buffers without graph expansion. | **Minor**: Suggested that basic Dijkstra could solve the problem directly by setting edge weights to $t_{\text{wait}}$, omitting the fact that waiting time depends on arrival time, which violates static edge weight assumptions. |
| **Execution Speed** | Very fast (~1.8 seconds response time). | Moderate (~4.5 seconds response time). |
| **Prompt Iterations Needed** | **1 iteration**: Delivered the exact multi-objective formulation ($\alpha \cdot \text{journey} + \beta \cdot \text{wait} + \gamma \cdot \text{transfers}$) matching the project requirements. | **2 iterations**: Required a second prompt to eliminate big-$M$ formulations and convert the problem to a pure 0-1 binary time-expanded network flow. |
| **Code Generation Quality** | Produced production-ready SciPy `milp` sparse constraint matrix generation with explicit bounds and variable integrator types. | Produced PuLP-style high-level symbolic variables which required an external library installation. |

---

### Synthesis & Conclusion
While both models successfully understood the core combinatorial challenge, Antigravity AI provided a cleaner, more computationally efficient formulation directly compatible with standard sparse matrix solvers (`scipy.optimize.milp`), eliminating the overhead of big-$M$ relaxations and external solver wrapper dependencies.
