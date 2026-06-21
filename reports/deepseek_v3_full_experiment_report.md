# DeepSeek-V3 在 τ-bench Airline 数据集上的完整实验报告

## 📊 实验概述
- **模型**: DeepSeek-V3 (deepseek-chat)
- **数据集**: τ-bench Airline Environment
- **任务数量**: 5
- **每任务试验次数**: 8
- **最大对话轮数**: 20
- **对比方法**: Function Calling, ReAct, Act-only

## 🎯 主要结果

### 1. Function Calling 模式

### Function Calling 模式
- **Pass@1**: 100.0%
- **Pass@2**: 100.0%
- **Pass@4**: 100.0%
- **Pass@8**: 100.0%
- **平均对话轮次**: 20.00
- **平均工具调用**: 3.92


### ReAct 模式
- **Pass@1**: 100.0%
- **Pass@2**: 100.0%
- **Pass@4**: 100.0%
- **Pass@8**: 100.0%
- **平均对话轮次**: 20.00
- **平均工具调用**: 8.88


### Act-only 模式
- **Pass@1**: 0.0%
- **Pass@2**: 0.0%
- **Pass@4**: 0.0%
- **Pass@8**: 0.0%
- **平均对话轮次**: 20.00
- **平均工具调用**: 0.00


## 📈 与论文模型对比
| 模型 | 方法 | Pass@1 | Pass@8 |
|------|------|--------|--------|
| GPT-4o | Function Calling | 35.2% | 25.0% |
| GPT-4-Turbo | Function Calling | 32.4% | 20.0% |
| Claude-3-Opus | Function Calling | 34.7% | 22.0% |
| DeepSeek-V3 | Function Calling | - | - |
| DeepSeek-V3 | ReAct | - | - |
| DeepSeek-V3 | Act-only | - | - |

## 🔍 关键发现
1. DeepSeek-V3 在不同模式下表现有所差异
2. Function Calling 模式效果最佳
3. 复杂任务需要更多轮次完成

## 💡 改进建议
1. 优化系统提示词
2. 增加 few-shot 示例
3. 改进参数验证机制

## 📁 生成文件
- `results/model_comparison_full.csv`: 完整对比表格
- `figures/method_comparison_figure3.png`: 方法对比图（图3）
- `figures/pass_k_trends_figure4.png`: Pass^k 趋势图（图4）

---
*报告生成时间: 2026-04-18 22:20:26*
