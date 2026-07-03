 # Report for Week3 Task

## Topic

1. Using Improved-POMO method to deal with small scale E(C)VRP-TW tasks

2. Comparing results with reliable baseline methods

---

## Part I. Overview

1. Methods which I tested: Improved-POMO method (DRL)

2. Baseline

   a) Baseline-Method: VNS/TS method (a hybrid metaheuristic method)

   _(Detail shows at: https://www.jstor.org/stable/43666939)_

   b) Test data (noticed in the journal above):

   _(Can be Downloaded at: https://data.mendeley.com/datasets/h3mrm5dhxw/1)_

3. Main differences between these 2 methods:

   There are huge differences. The most different one should be their thinking/inference method logic:

   VNS/TS will find an initial answer at first, then using calculations to change the initial answer; Improved-POMO, as a DRL type method, will do lots of searching work during the training period, changing its moving attitude based on defined award/function, and finally produces some task-solving models.

4. What question I want to answer:

   How well could Improved-POMO method do in strict Question-Def situation.

   3 comment perspectives:

   a) Ability to find a solution (answer the requirements)

   b) Ability to find nearly paths

   c) Researching speed

   _(Reasons: In Week2, I used my simple EVRPTW question define & easy-solving data to compare the ability of simple-improved OR-Tools, POMO, and GA methods. The result of Improved-POMO seemed not good, especially in the distance aspect. However, for 2 situations that Improved-OR-Tools and Improved-GA couldn’t solve, Improved-POMO came up with solutions. So, I decided to research on the ability of POMO further.)_

---

## Part II. Experiment

Due to the current ability of my Improved-POMO method, this report only compares results on small-scale E(C)VRP-TW instances. Larger-scale models are not stable enough at the current stage.

The baseline method is VNS/TS, and the tested method is Improved-POMO. The comparison focuses on three aspects: solution feasibility, route distance, and average runtime.

**Runtime note:** The runtime of Improved-POMO is measured in batch inference mode and averaged over the instances in the same batch. Therefore, the reported POMO runtime should be understood as average runtime per instance, not strictly independent single-instance runtime.

### Table 1. Comparison between VNS/TS and Improved-POMO

| Instance | VNS/TS Distance | Improved-POMO Distance | Gap `((POMO - VNS/TS) / VNS/TS)` | VNS/TS Runtime | POMO Avg Runtime | Status |
|---|---:|---:|---:|---:|---:|---|
| c103C5 | 176.05 | 204.50 | +16.16% | 0.12s | 0.75s | Feasible |
| c208C5 | 158.48 | 244.44 | +54.24% | 0.11s | 0.071s | Feasible |
| r202C5 | 128.78 | 204.71 | +59.24% | 0.11s | 0.071s | Feasible |
| rc208C5 | 167.98 | 174.39 | +3.82% | 0.13s | 0.071s | Feasible |
| c206C5 | 242.55 | 261.67 | +7.88% | 0.11s | 0.080s | Feasible |
| r203C5 | 179.06 | N/A | N/A | 0.15s | 0.080s | No feasible solution |
| rc108C5 | 253.93 | N/A | N/A | 0.17s | 0.080s | No feasible solution |
| rc204C5 | 176.39 | 186.48 | +5.72% | 0.15s | 0.080s | Feasible |

---

## Part III. Analysis

From the results, Improved-POMO successfully generated feasible solutions for 6 out of 8 tested instances. This indicates that the method has a certain ability to handle strict E(C)VRP-TW constraints in small-scale cases. However, it failed on `r203C5` and `rc108C5`, which suggests that the current model is still not stable enough under different instance structures.

In terms of solution quality, VNS/TS clearly outperforms Improved-POMO in most cases. Among the feasible POMO results, the distance gap ranges from +3.82% to +59.24%. The best relative performance appears on `rc208C5` and `rc204C5`, where the gaps are only +3.82% and +5.72%. However, on `c208C5` and `r202C5`, the gaps are larger than 50%, showing that the learned policy still has difficulty producing near-optimal routes for some instances.

In terms of runtime, Improved-POMO is competitive on several instances after batch inference averaging. For most cases, its average inference time is around 0.07s to 0.08s per instance. However, because the VNS/TS runtime and POMO runtime may be measured under different experimental settings, the runtime comparison should be treated as a rough reference rather than a strict hardware-level comparison.

Overall, Improved-POMO shows potential in quickly generating feasible solutions for small-scale E(C)VRP-TW problems, but its solution quality and robustness are still weaker than the VNS/TS baseline. The current results suggest that future work should focus on improving constraint handling, reward design, and generalization across different instance types.

---

## Part IV. Conclusion

The experiment shows that Improved-POMO can solve most of the selected small-scale E(C)VRP-TW instances and can produce solutions quickly during inference. However, compared with the VNS/TS baseline, its route distances are usually longer and it still fails on some instances.

Therefore, Improved-POMO is currently more suitable as a fast learning-based solver candidate, but it still requires further improvement before it can match strong metaheuristic baselines in solution quality and robustness.

In short, Improved-POMO is able to generate feasible solutions for most tested small-scale instances, but it does not yet outperform the VNS/TS baseline. Its main advantage is fast inference after training, while its main weaknesses are solution quality and robustness under strict constraints.

I think DRL is a strong method, but maybe it cann't work alone in the background of E(C)VRPTW task.
