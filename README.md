# DeepSeek-Agent-ToolCalling-Benchmark

> 基于 τ-bench 框架的 DeepSeek 智能体工具调用评估实验

## 项目简介

本项目在 τ-bench 航空客服数据集（Airline Domain）上，集成了 **DeepSeek V3** 大语言模型，实现了基于 Function Calling（工具调用）的 Agent 系统。系统能够理解用户自然语言需求，自动调用航班查询、预订、改签、退票等业务工具，完成复杂的多轮对话任务。

## 核心能力

- Function Calling 实现：完整实现工具调用流程（意图识别 → 参数提取 → 工具执行 → 结果处理）
- Agent 智能体：基于 τ-bench 框架构建，支持多轮对话状态管理
- 标准化评测：在 Airline 数据集子集上完成系统评估，支持 Pass@1 / Pass@k 指标计算
- 对比实验：对比 Function Calling、ReAct、Act-only 三种方法的性能表现，分析工具调用失败案例

## 实验说明

本实验基于 τ-bench 航空客服数据集中抽取的部分任务样本进行测试，针对 DeepSeek V3 在 Function Calling、ReAct、Act-only 三种方法下的表现进行评估。由于测试样本为数据集的子集，结果仅反映该子集上的表现，不代表模型在完整数据集或更广泛场景下的真实能力，后续可扩大样本量以提升结果可靠性。

## 实验结果

| 方法 | Pass@1 | Pass@8 |
|------|--------|--------|
| DeepSeek V3 - Function Calling | 100.0% | 100.0% |
| DeepSeek V3 - ReAct | 100.0% | 100.0% |
| DeepSeek V3 - Act-only | 0.0% | 0.0% |

## 核心指标解读

- **Pass@1**：单次尝试即成功完成任务的比例，反映模型的"一次成功率"，越高代表模型越稳定可靠
- **Pass@8**：8次独立尝试中有任意一次成功的比例，反映模型的"潜在最佳能力"，越高代表模型具备完成任务的能力，但可能存在随机性

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.12 | 编程语言 |
| DeepSeek API | 大模型推理 |
| τ-bench | Agent 评测框架 |
| Function Calling | 工具调用机制 |
| Matplotlib / Seaborn | 结果可视化 |
| Pandas / NumPy | 数据分析 |

## 快速开始

### 1. 克隆项目
```bash   ”“bash   “bash”;“bash
git clone https://github.com/mbabmmmm/DeepSeek-Agent-ToolCalling-Benchmark.git
cd DeepSeek-Agent-ToolCalling-Benchmark
```

### 2. 安装依赖
```bash   ”“bash   “bash”;“bash
pip install -r requirements.txt
```

### 3. 配置 API Key
在 `experiments/run.py` 中替换你的 DeepSeek API Key：
```python   ”“python      “python”;“pyhon
API_KEY = "your_deepseek_api_key"
```
或者在环境变量中设置：   
```bash   ”“bash   “bash”;“bash
export DEEPSEEK_API_KEY="your_api_key"
```

### 4. 运行实验
```bash   ”“bash   “bash”;“bash
python experiments/run.pypython实验/ run.py
```

### 5. 生成分析结果
```bash   ”“bash   “bash”;“bash
python run.py
```

## 开发者

- GitHub: [mbabmmmm](https://github.com/mbabmmmm)
