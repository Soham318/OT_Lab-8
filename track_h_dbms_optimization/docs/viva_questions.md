# Track H: Comprehensive Academic Viva Questions & Answers

## 1. Relational Database Internals & Access Paths

### Q1: What is the fundamental structural difference between a clustered index and a secondary (unclustered) index in SQLite?
**Answer**:
In SQLite, every regular table is implemented as a B* Tree ordered by a 64-bit signed integer key termed the `rowid` (or the column defined as `INTEGER PRIMARY KEY`). This is the *clustered index*, meaning the actual row data (the tuple payload) resides directly within the leaf pages of this B-tree.

In contrast, a *secondary index* is a separate, auxiliary B-tree structure where the search key consists of the indexed column values, appended with the corresponding table rowid. Leaf pages of secondary index B-trees store keys and rowids, not the complete table rows. Therefore, evaluating a query using a secondary index requires a two-stage lookup:
1. Traverse the secondary index B-tree ($O(\log M)$ page reads) to locate matching rowids.
2. For each matching rowid, perform a point lookup seek on the clustered table B-tree ($O(\log N)$ page reads) to retrieve the remaining columns requested by the `SELECT` clause.

### Q2: What is a "covering index", and why does it represent the theoretical maximum speedup for a secondary index?
**Answer**:
A covering index is a secondary index that contains all columns referenced by a query—including columns in the `WHERE`, `JOIN`, `SELECT`, `GROUP BY`, and `ORDER BY` clauses.

When a query's projection and filtering can be satisfied entirely from the index B-tree keys, SQLite executes an *index-only scan*. The database engine completely bypasses the secondary seek on the table B-tree. This halves the number of logical page reads and eliminates random I/O, resulting in the maximum achievable retrieval speedup.

### Q3: What is the "left-prefix rule" for composite indexes, and how does it restrict query acceleration?
**Answer**:
A composite index on columns $(A, B, C)$ stores entries sorted first by $A$, then by $B$ for identical values of $A$, and finally by $C$.
According to the left-prefix rule:
- A query filtering on $(A)$ or $(A, B)$ or $(A, B, C)$ can utilize the index for range and equality searches because the leading columns form a sorted contiguous search interval.
- A query filtering solely on $(B)$ or $(C)$ cannot perform a binary seek on the index B-tree, because records with the same $B$ or $C$ value are scattered across the tree under different $A$ keys. At best, the engine can perform a full index scan, but not a logarithmic seek.

### Q4: What does the SQLite `ANALYZE` command do, and why was it mandatory in our benchmark methodology?
**Answer**:
The `ANALYZE` command scans all database tables and indexes, computing distribution statistics that it stores in internal catalog tables (`sqlite_stat1` and `sqlite_stat4`).

Without `ANALYZE`, SQLite's cost-based query planner relies on default heuristics (e.g., assuming an index equality match reduces candidate rows to $1/10$ or $1/50$ of the table). With `ANALYZE`, the planner knows the exact average number of rows per distinct key prefix. Without running `ANALYZE` after index creation, the query optimizer may make sub-optimal decisions, such as refusing to utilize an advantageous index because it overestimates the cost of index lookups.

---

## 2. Query Optimization & Execution Plans

### Q5: How do you interpret SQLite's `EXPLAIN QUERY PLAN` output, and what is the difference between `SCAN` and `SEARCH`?
**Answer**:
`EXPLAIN QUERY PLAN` returns a high-level textual representation of the plan selected by the query optimizer:
- **`SCAN <table>`**: Represents a full sequential table scan. The VDBE traverses every page of the table B-tree from beginning to end ($O(N)$ complexity).
- **`SEARCH <table> USING INDEX <index_name>`**: Indicates that the engine traverses a B-tree index using binary search down the interior nodes to a leaf page, locating specific candidate rows in logarithmic time ($O(\log N)$ complexity).
- **`SEARCH <table> USING INTEGER PRIMARY KEY (rowid=?)`**: Direct point seek on the clustered table B-tree.
- **`USE TEMP B-TREE FOR ORDER BY / GROUP BY`**: The planner must materialize intermediate rows into an ephemeral in-memory or on-disk B-tree and sort them because the chosen access path did not deliver rows in the requested sort order.

### Q6: What is a Bloom filter in SQLite query execution (observed in Q2)?
**Answer**:
Introduced in modern SQLite versions, a Bloom filter is a space-efficient probabilistic data structure created during multi-table join processing. In queries such as Q2 (`passengers` joined to `tickets` and `bookings`), SQLite constructs a transient Bloom filter on foreign keys (e.g., `booking_id`). When scanning outer table rows, candidate keys are probed against the Bloom filter in $O(1)$ CPU time. If the filter returns false, the row is discarded immediately without incurring expensive B-tree lookups or table seeks.

---

## 3. Mathematical Optimization & Integer Programming

### Q7: Why is the Index Selection Problem (ISP) NP-hard?
**Answer**:
The Index Selection Problem can be shown to be NP-hard through a polynomial-time reduction from the classic **0-1 Knapsack Problem** (or the Maximum Coverage Problem):
- Given a set of items with weights $w_i$ and values $v_i$, and a knapsack capacity $W$:
- Map each item to a candidate database index with storage cost $c_i = w_i$.
- Construct independent queries $q_i$ such that index $i$ accelerates only query $q_i$ with benefit $b_i = v_i$.
- Setting storage budget $S_{\max} = W$, finding the index set that maximizes workload benefit is strictly equivalent to solving the 0-1 Knapsack Problem, which is known to be NP-complete. When index interactions and multi-query sharing are introduced, the problem generalizes to Set Packing / Maximum Submodular Coverage under a knapsack constraint.

### Q8: Why are index benefits non-additive, and how is this non-linearity linearized in our ILP?
**Answer**:
Index benefits are non-additive because a database query planner selects at most one primary access path for scanning a given table occurrence. If index $A$ yields 50 ms latency reduction and index $B$ yields 60 ms latency reduction on query $Q$, deploying both indexes does not yield $50 + 60 = 110$ ms reduction; the optimizer simply selects index $B$, yielding 60 ms. The benefit function is submodular:
$$
B(q, X) = \max_{i \in C_q} (b_{q,i} x_i)
$$
To linearize this non-linear $\max$ operator:
1. We introduce auxiliary selection decision variables $y_{q,i} \in \{0, 1\}$ representing whether index $i$ is assigned to query $q$.
2. We enforce coupling constraints:
   $$
   y_{q,i} \le x_i \quad \forall q, i \quad \text{(an unbuilt index cannot be assigned)}
   $$
   $$
   \sum_{i \in C_q} y_{q,i} \le 1 \quad \forall q \quad \text{(at most one index provides primary benefit)}
   $$
3. The objective becomes linear:
   $$
   \max \sum_{q \in \mathcal{Q}} \sum_{i \in C_q} w_q b_{q,i} y_{q,i}
   $$

### Q9: Why did the Greedy heuristic fall into a sub-optimal trap at budget $S_{\max} = 3.0$ MB?
**Answer**:
At budget 3.0 MB, both Greedy and ILP picked `IDX_02` (1.5 MB), leaving 1.5 MB remaining.
Greedy evaluates candidates based on the local marginal benefit-to-cost ratio $\frac{\Delta B_i}{c_i}$.
- Candidate `IDX_09` had cost 0.8 MB and gain 1,425 (ratio = 1,781.25).
- Candidate `IDX_07` had cost 1.4 MB and gain 2,350 (ratio = 1,678.57).

Because $1,781.25 > 1,678.57$, Greedy selected `IDX_09`. However, this left only $1.5 - 0.8 = 0.7$ MB of budget remaining, making it impossible to select `IDX_07` (1.4 MB). Greedy was forced to settle for `IDX_10` (0.6 MB, gain 440), ending with a total score of $6,520$.

In contrast, Exact ILP solved the global combinatorial problem simultaneously, recognizing that picking `IDX_07` (1.4 MB) alone delivered higher total value ($2,350$) than the pair `IDX_09 + IDX_10` ($1,425 + 440 = 1,865$). ILP achieved a total score of $7,005$, proving an authentic **$6.92\%$ optimality gap** in the heuristic.

### Q10: What is the theoretical approximation guarantee of the Greedy heuristic for this problem class?
**Answer**:
When the objective function is a monotone submodular set function subject to a cardinality or knapsack constraint, Nemhauser, Wolsey, and Fisher (1978) proved that the standard greedy heuristic achieves an approximation ratio of:
$$
\alpha \ge 1 - \frac{1}{e} \approx 63.2\%
$$
Under modified greedy variants that consider both ratio-based selection and single high-value items, the guarantee is $(1 - 1/e)$. In our experimental sweep, the greedy heuristic performed substantially better than the theoretical worst-case bound, achieving between **$93.08\%$ and $100.00\%$** of the global optimum across all 14 evaluated budgets.

---

## 4. Empirical Evaluation & Experimental Controls

### Q11: Why is cryptographic SHA-256 result hashing essential when evaluating database indexing?
**Answer**:
Adding or removing secondary indexes must *never* alter the semantic result set returned by a SQL query; indexes are purely physical performance optimizations. By computing the SHA-256 hash over the sorted, serialized tuple results of all 8 queries across Baseline, Greedy, and ILP databases:
1. We formally prove zero semantic corruption (100% result equivalence).
2. We detect subtle bugs, such as implicit ordering changes or NULL handling divergences that can occur when the query planner switches from a table scan to an index traversal.

### Q12: Why did Q8 exhibit an 11.45x speedup under ILP, while Q7 exhibited virtually no speedup?
**Answer**:
- **Query Q8 (Transactional PNR Lookup)**: Filters on a high-cardinality unique attribute (`pnr_number = 'PNR-2026-004281'`) in a 36,000-row table. Under Baseline and Greedy, the absence of an index on PNR forced SQLite to scan all 36,000 records (1.26 ms). Under ILP, `IDX_07` provided an immediate B-tree point seek directly to the matching leaf node in $O(\log N)$, cutting latency to **0.11 ms** (**11.45x speedup**).
- **Query Q7 (Monthly Demographics & Occupancy)**: Involves a multi-table analytical aggregation scanning nearly 90,000 ticket rows and grouping by age category and travel class. Because the query processes a massive fraction of the table rows, scanning secondary index pages and performing random seeks back into the table pages is slower than a contiguous sequential scan of the table pages. SQLite's cost planner recognized this and correctly chose a sequential scan in all configurations.

### Q13: What are the negative trade-offs of creating secondary indexes in transactional production databases?
**Answer**:
1. **DML Write Amplification**: Every `INSERT`, `UPDATE` (of indexed columns), or `DELETE` statement must update not only the table B-tree, but also every secondary index B-tree covering the modified columns. For high-throughput write workloads, excessive indexing degrades insertion throughput.
2. **Buffer Pool Pollution**: Secondary index pages compete with active table pages for residency in the database cache (RAM), potentially evicting frequently accessed data pages.
3. **Storage Bloat**: In our experiment, adding 2.9 MB of indexes to a 9.46 MB database increased the physical storage footprint by **30.7%**.

### Q14: How does the HiGHS solver in SciPy guarantee global optimality for the ILP?
**Answer**:
SciPy's `scipy.optimize.milp` interfaces with the state-of-the-art C++ HiGHS optimization library. HiGHS utilizes the **Branch-and-Cut** algorithm:
1. It solves the continuous LP relaxation using the dual simplex or interior point method.
2. It generates valid cutting planes (Gomory cuts, mixed integer rounding cuts) to tighten the feasible polytope without removing integer solutions.
3. It performs branch-and-bound on fractional variables, using primal heuristics to find strong upper/lower bounds.
4. When the integrality gap closes to within the numerical tolerance ($\epsilon < 10^{-6}$), the solution is mathematically proven to be the global optimum. We verified this 100% against brute-force exhaustive enumeration ($2^{12} = 4096$ subsets).

### Q15: How does Track H connect with the broader optimization themes in Tracks A, B, C, D, and E?
**Answer**:
- **Track A (Continuous)**: Uses gradient-based continuous search; in Track H, continuous LP relaxation provides the bounding foundation for branch-and-cut.
- **Track B (Discrete)**: Explored combinatorial knapsack and branch-and-bound; Track H applies discrete knapsack formulation to enterprise DBMS physical tuning.
- **Track C (Quantum / QUBO)**: Modeled quadratic unconstrained binary optimization; index selection with pairwise mutual exclusion or synergy can be directly mapped to QUBO matrix formulations.
- **Track D (Parallel & Submodular)**: Investigated submodular greedy maximization; Track H demonstrates submodular diminishing returns in query access path selection.
- **Track E (Network Routing)**: Found shortest paths in railway transit graphs; Track H uses that railway domain to build a transactional and analytical database workload.

