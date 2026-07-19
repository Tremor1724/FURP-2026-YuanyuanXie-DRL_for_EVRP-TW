# Report for Week4&5

## PART I - What did I do

### 1.算法方面：调整我的Improved-POMO-baseline，使之更适配我所选取的Schneider数据集研究场景。
(1)单个车辆->在单个车辆无法完成任务的情况下可选择多车辆方案（增加了vehicle_num相关变量+相关奖惩约束）；
(2)对Improved-POMO-baseline中非常粗暴的reward和penalty参数进行了调整，使之相对于我原有的baseline method而言变得更加灵活一些；

### 2.规模适配度方面：我尝试了将原有的n5训练简单缩放到n15，但是因为Schneider数据集的变量较多而我之前的方案很暴力模拟，所以训练耗时较长、对问题的求解效果也不太好。所以我选择先退回n5，进行上面提到的对算法的改善，先追求稳定性。

### 3.上述目标大体实现。（将在第II部分附上此次调整后对Schneider数据集里n5规模实例的测试结果）

将在第 II 部分附上此次调整后对 Schneider 数据集里 n5 规模实例的测试结果。

---

## PART II - New Report Data

我将在下表中比较四种方法在 n5 规模实例中的表现：

| Label | Method | Description |
|---|---|---|
| A | CPLEX | Schneider 等人使用的基准数据 |
| B | VNS/TS Distance | data from Schneider 等人，重要基准 |
| C | Improved POMO baseline | My old Improved method，用于体现优化部分 |
| D | Improved POMO 2.0 | Nearly Improved POMO method，当前方案 |

---

### Table 1. CPLEX, VNS/TS, Old Improved POMO and Improved POMO 2.0 Comparison

| Instance | CPLEX Distance | CPLEX Runtime | VNS/TS Distance | VNS/TS Runtime | Old Improved-POMO Distance | Old Status | Old Runtime | Improved POMO 2.0 Distance | New Gap vs VNS/TS | POMO 2.0 Vehicles | POMO 2.0 Station Visits | POMO 2.0 Runtime | New Status |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| c101C5 | 257.75 | 81s | 257.75 | 0.21s | N/A | No feasible solution | 0.071s | 299.36 | +16.14% | 3 | 4 | 0.204s | Feasible |
| c103C5 | 176.05 | 5s | 176.05 | 0.12s | 204.50 | Feasible | 0.750s | 187.11 | +6.28% | 2 | 4 | 1.897s | Feasible |
| c206C5 | 242.55 | 518s | 242.55 | 0.14s | 261.67 | Feasible | 0.080s | 336.66 | +38.80% | 1 | 4 | 0.202s | Feasible |
| c208C5 | 158.48 | 15s | 158.48 | 0.11s | 244.44 | Feasible | 0.071s | 275.47 | +73.82% | 1 | 4 | 0.157s | Feasible |
| r104C5 | 136.69 | 1s | 136.69 | 0.13s | N/A | No feasible solution | 0.071s | 192.96 | +41.17% | 3 | 4 | 0.228s | Feasible |
| r105C5 | 156.08 | 3s | 156.08 | 0.11s | N/A | No feasible solution | 0.071s | 253.08 | +62.15% | 3 | 4 | 0.195s | Feasible |
| r202C5 | 128.78 | 1s | 128.78 | 0.11s | 204.71 | Feasible | 0.071s | 187.71 | +45.76% | 2 | 4 | 0.228s | Feasible |
| r203C5 | 179.06 | 5s | 179.06 | 0.15s | N/A | No feasible solution | 0.080s | 237.97 | +32.90% | 1 | 4 | 0.250s | Feasible |
| rc105C5 | 241.30 | 764s | 241.30 | 0.14s | N/A | No feasible solution | 0.080s | 277.93 | +15.18% | 3 | 4 | 0.274s | Feasible |
| rc108C5 | 253.93 | 311s | 253.93 | 0.17s | N/A | No feasible solution | 0.080s | 322.04 | +26.82% | 2 | 4 | 0.232s | Feasible |
| rc204C5 | 176.39 | 54s | 176.39 | 0.15s | 186.48 | Feasible | 0.080s | 276.44 | +56.72% | 1 | 4 | 0.197s | Feasible |
| rc208C5 | 167.98 | 21s | 167.98 | 0.13s | 174.38 | Feasible | 0.071s | 222.73 | +32.59% | 1 | 4 | 0.219s | Feasible |

---

### Table 2. Overall Summary

| Method | Number of Tested Instances | Number of Feasible Solutions | Feasible Rate | Average Distance | Average Vehicle Count | Average Station Visits | Total Runtime | Avg Runtime per Instance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CPLEX | 12 | 12 | 100.00% | 189.59 | N/A | N/A | 1779.00s | 148.25s |
| VNS/TS | 12 | 12 | 100.00% | 189.59 | N/A | N/A | 1.67s | 0.139s |
| Improved-POMO baseline | 12 | 6 | 50.00% | 212.70 over feasible cases | N/A | N/A | 1.598s | 0.133s |
| Improved POMO 2.0 | 12 | 12 | 100.00% | 255.79 | 1.92 | 4.00 | 4.315s | 0.360s |

---

### Table 3. Old Improved POMO vs Improved POMO 2.0 Overall Comparison

| Aspect | Old Improved POMO | Improved POMO 2.0 | Comparison |
|---|---:|---:|---|
| Tested instances | 12 | 12 | Same test set |
| Feasible instances | 6 | 12 | Improved POMO 2.0 is better |
| Feasible rate | 50.00% | 100.00% | Improved POMO 2.0 solves all tested instances feasibly |
| Average distance reported by raw output | 5106.35 | 255.79 | Old value is distorted by infeasible `10000.0` placeholders |
| Average distance over feasible cases only | 212.70 | 255.79 | Old Improved POMO has shorter routes when it succeeds |
| Total runtime | 1.598s | 4.315s | Old Improved POMO is faster |
| Avg runtime per instance | 0.133s | 0.360s | Improved POMO 2.0 costs more runtime |
| Vehicle-count information | Not reported | Avg. 1.92 vehicles | Improved POMO 2.0 provides more route-structure information |
| Station-visit information | Not reported | Avg. 4.00 visits | Improved POMO 2.0 tracks charging behavior explicitly |

---

### Table 4. Instance-Level Comparison Between Old Improved POMO and Improved POMO 2.0

| Instance | Old Improved POMO Distance | Old Status | Improved POMO 2.0 Distance | New Status | Better Method |
|---|---:|---|---:|---|---|
| c101C5 | N/A | No feasible solution | 299.36 | Feasible | Improved POMO 2.0 |
| c103C5 | 204.50 | Feasible | 187.11 | Feasible | Improved POMO 2.0 |
| c206C5 | 261.67 | Feasible | 336.66 | Feasible | Old Improved POMO |
| c208C5 | 244.44 | Feasible | 275.47 | Feasible | Old Improved POMO |
| r104C5 | N/A | No feasible solution | 192.96 | Feasible | Improved POMO 2.0 |
| r105C5 | N/A | No feasible solution | 253.08 | Feasible | Improved POMO 2.0 |
| r202C5 | 204.71 | Feasible | 187.71 | Feasible | Improved POMO 2.0 |
| r203C5 | N/A | No feasible solution | 237.97 | Feasible | Improved POMO 2.0 |
| rc105C5 | N/A | No feasible solution | 277.93 | Feasible | Improved POMO 2.0 |
| rc108C5 | N/A | No feasible solution | 322.04 | Feasible | Improved POMO 2.0 |
| rc204C5 | 186.48 | Feasible | 276.44 | Feasible | Old Improved POMO |
| rc208C5 | 174.38 | Feasible | 222.73 | Feasible | Old Improved POMO |

---

## PART III - Simple Summary

### 1. Main advantages of Improved POMO 2.0

#### 1.1 Feasibility is significantly improved

旧 Improved POMO 在 12 个实例中只有 6 个可行，另外 6 个返回 `10000.0`，说明没有找到可行解。Improved POMO 2.0 在 12 个实例中全部可行，说明多车辆机制和新的 penalty 设计确实提高了模型稳定性。

#### 1.2 Constraint handling is more complete

Improved POMO 2.0 显式考虑了 vehicle count、station visits、energy violation、lateness、capacity violation、infeasible termination 等信息。旧版本虽然速度快，但对不可行情形的处理更粗糙。

#### 1.3 Result interpretation is better

Improved POMO 2.0 不只输出 distance，还输出车辆数、充电站访问次数、是否返回 depot、是否有 lateness / energy / capacity violation。这些指标更适合写进报告，因为它们能说明模型为什么可行或不可行。

---

### 2. Main disadvantages of Improved POMO 2.0

#### 2.1 Distance quality is not consistently better

在两种方法都找到可行解的 6 个实例里，Improved POMO 2.0 只有 2 个实例距离更短，另外 4 个实例距离更长。这说明当前版本主要解决的是可行性问题，不是路径最优性问题。

#### 2.2 Charging strategy may be too conservative

Improved POMO 2.0 平均每个实例访问充电站 `4.00` 次。这会降低 energy violation 风险，但也会增加额外路径距离，导致总距离变长。

#### 2.3 Runtime increases

旧 Improved POMO 总运行时间为 `1.598s`，Improved POMO 2.0 为 `4.315s`。虽然两者都很快，但新版本为了获得更稳定的可行解，付出了更多推理时间。

---

## PART IV - Projected Work

### 1. 使模型找到的解能够更加接近/等于Schneider提供的最优解
		主要打算从下面两个方面入手：
		(1) 继续优化调参——调出更合理的差异化参数or在训练模型的过程中让模型学会动态调整不同约束条件中的奖惩系数（先读相关论文。）
		(2) 我的模型在训练阶段依靠的是随机数据，而这些随机训练场景虽然被我调成了较为宽松的，却也还是无法避免（匀下来大概是）40~50%的无解场景，我认为是导致我的模型训	练到后期会存在大量噪音的主要原因。所以我打算借鉴TS等启发式方法，在生成随机训练场景时先进行对场景可行性的粗略判断，提前减少噪音污染模型导致后期退化的可能性。

### 2. 拓展模型到n15，甚至是Schneider论文中更加复杂、更加现实化的场景中。（不过这个只能算是远大目标。总之先放在这里吧。。）
