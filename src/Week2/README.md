[说明部分先暂时用中文了]
<br>Part 1: 阶段性最终结果对比
<br>Part 2: 文件格局说明
<br>Part N: 特殊说明/总结反思
---------------------------------
***Part 1***
<br>
| 方法    | Runtime(s) | Total tasks | Feasible | Average Score | Train time |
| :------ | :--------: | :---------: | :------: | :-----------: | :------------ |
| ORTools | 17.9       | 1000        | 998      | 14.233        | None          |
| POMO    | 9          | 1000        | 1000     | 32.1936       | ≈11h          |
| ORTools | 709.416    | 1000        | 998      | 25.002        | None          |
<br>
<br>数据集(问题设置):
<br>规模: 50用户 + 5充电站 + 1depot(随机)
<br>
<br>所有节点坐标均在 [0,1] × [0,1] 坐标系中随机采样。
<br>时间窗限制(只限制了客户时间窗):
<br>1.中心在 [0.5, 3.5] 均匀分布
<br>2.宽度在 [1.0, 4.0] 均匀分布
<br>客户服务时间: 0.05 ; 车辆速度: 1.0 (与坐标轴 1:1)
<br>电量限制:
<br>电池容量: 3.0 ; 能耗: 1.0 (每单位距离消耗 1单位电量)
<br>

------------------------------------
***Part 2***
<br>
```
Week2/
├── evrptw50_test_2.pt             #最终用来对比的数据集
├── test_data_readable_2.txt
├── ORTools/
│   ├── result/
│   ├── ortools_evrptw.py
│   ├── run_ortools.py
│   └── Env_requirements_ORTools_evrptw.txt
├── POMO/
│   ├── utils/
│   ├── result/
│   │   ├── Test/
│   │   └── Modelsave/
│   ├── test_evrptw_50.py
│   ├── EVRPTWTester.py
│   ├── EVRPTWProblemDef_wid.py
│   └── Env_requirements_POMO_evrptw.txt
├── GA/
│   ├── result/
│   ├── core_evrptw.py
│   ├── run_GA.py
│   ├── result_cal.py
│   └── Env_requirements_GA_evrptw.txt
├── requirements.txt
└── README.md
```

----------------------------------------
***Part N***
<br>
<br>1.一开始POMO那边ProblemDef限制得比较严，训练的时候也是用的严的一版进行的。结果用严版ProblemDef生成出来的数据集对时间窗的限制导致ortools整个暴死，单个场景的限制放到100s的前提下，（1000个场景）还是一个都跑不出来......所以虽然POMO能跑出来(结果是32.2276)，还是选择把时间窗限制调松重新生成了一版数据集(evrptw50_test_2.pt)。
<br>有点怀疑POMO模型的结果对比之下这么差: 一方面有从CVRP改过来改得很粗糙的原因（因为还不懂调参所以参数部分belike:能没动的就没动、能问AI的就先让AI填了），另一方面也有一开始训练背景太严格导致模型倾向于保守探索（先出解）的原因。
<br>（btw其实POMO训练的时候我为了快点跑好减了不少训练量。可能这也限制了策略发散吧。）
<br>
<br>2.总之结果是一个 [time] POMO < ORTools < GA ; [Outcome] POMO < GA < ORTools 的大状态
<br>  感觉ortools无论是第一周复现的时候还是这周加约束维度的时候确实还是要稳一点，但是POMO和GA本身可以调节的地方也更多，疑似纯粹是我个人知识储备限制了实现。（总之报告先写到这里，我再捣鼓捣鼓...）（那要捣鼓的东西很多了.JPG）
