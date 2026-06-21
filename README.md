# DeepSeek-Agent-ToolCalling-Benchmark

> 基于 τ-bench 框架的 DeepSeek 智能体工具调用评估实验

 项目简介

本项目在 τ-bench 航空客服数据集（Airline Domain）上，集成了 **DeepSeek V3** 大语言模型，实现了基于 Function Calling（工具调用）的 Agent 系统。系统能够理解用户自然语言需求，自动调用航班查询、预订、改签、退票等业务工具，完成复杂的多轮对话任务。

 核心能力

- Function Calling 实现：完整实现工具调用流程（意图识别 → 参数提取 → 工具执行 → 结果处理）
- Agent 智能体：基于 τ-bench 框架构建，支持多轮对话状态管理
- 标准化评测：在 Airline 数据集上完成系统评估，支持 Pass@1 / Pass@k 指标计算
- 对比实验：对比不同方法的性能表现，分析工具调用失败案例

实验结果

| 模型 | 方法 | Pass@1 | Pass@8 |
|------|------|--------|--------|
| GPT-4o | Function Calling | 35.2% | 25.0% |
| GPT-4-Turbo | Function Calling | 32.4% | 20.0% |
| claude-3-opus | Function Calling | 34.7% | 22.0% |
| DeepSeek V3| Function Calling | 100.0% | 100.0% |
| DeepSeek V3| ReAct | 100.0% | 100.0% |
| DeepSeek V3| Act-only | 0.0% | 0.0% |

核心指标解读

- Pass@1：单次尝试即成功完成任务的比例，反映模型的“一次成功率”
- Pass@8：8次尝试中有任意一次成功的比例，反映模型的“潜在能力”

 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.8+ | 编程语言 |
| DeepSeek API | 大模型推理 |
| τ-bench | Agent 评测框架 |
| Function Calling | 工具调用机制 |
| Matplotlib / Seaborn | 结果可视化 |
| Pandas / NumPy | 数据分析 |

 项目结构
 │  .gitignore
│  README.md
│  requirements.txt
│  setup.py
│
├─experiments
│      run.py
│
├─figures
│      method_comparison_figure3.png
│      pass_k_trends_figure4.png
│
├─reports
│      deepseek_v3_full_experiment_report.md
│
├─results
│  │  model_comparison_full.csv
│  │
│  └─json
│          deepseek_all_experiments_20260418_221827.json
│          deepseek_results_ao_20260418_221827.json
│          deepseek_results_fc_20260418_195031.json
│          deepseek_results_react_20260418_210646.json
│
└─tau_bench
    │  check_imports.py
    │  run.py
    │  types.py
    │  __init__.py
    │
    ├─agents
    │  │  base.py
    │  │  chat_react_agent.py
    │  │  deepseek_v3_agent.py
    │  │  few_shot_agent.py
    │  │  tool_calling_agent.py
    │  │  __init__.py
    │  │
    │  └─__pycache__
    │          base.cpython-312.pyc
    │          deepseek_agent.cpython-312.pyc
    │          __init__.cpython-312.pyc
    │
    ├─envs
    │  │  base.py
    │  │  tool.py
    │  │  user.py
    │  │  __init__.py
    │  │
    │  ├─airline
    │  │  │  env.py
    │  │  │  rules.py
    │  │  │  tasks.py
    │  │  │  tasks_test.py
    │  │  │  wiki.md
    │  │  │  wiki.py
    │  │  │  __init__.py
    │  │  │
    │  │  ├─data
    │  │  │  │  flights.json
    │  │  │  │  reservations.json
    │  │  │  │  users.json
    │  │  │  │  __init__.py
    │  │  │  │
    │  │  │  └─__pycache__
    │  │  │          __init__.cpython-312.pyc
    │  │  │
    │  │  ├─tools
    │  │  │  │  book_reservation.py
    │  │  │  │  calculate.py
    │  │  │  │  cancel_reservation.py
    │  │  │  │  get_reservation_details.py
    │  │  │  │  get_user_details.py
    │  │  │  │  list_all_airports.py
    │  │  │  │  search_direct_flight.py
    │  │  │  │  search_onestop_flight.py
    │  │  │  │  send_certificate.py
    │  │  │  │  think.py
    │  │  │  │  transfer_to_human_agents.py
    │  │  │  │  update_reservation_baggages.py
    │  │  │  │  update_reservation_flights.py
    │  │  │  │  update_reservation_passengers.py
    │  │  │  │  __init__.py
    │  │  │  │
    │  │  │  └─__pycache__
    │  │  │          book_reservation.cpython-312.pyc
    │  │  │          calculate.cpython-312.pyc
    │  │  │          cancel_reservation.cpython-312.pyc
    │  │  │          get_reservation_details.cpython-312.pyc
    │  │  │          get_user_details.cpython-312.pyc
    │  │  │          list_all_airports.cpython-312.pyc
    │  │  │          search_direct_flight.cpython-312.pyc
    │  │  │          search_onestop_flight.cpython-312.pyc
    │  │  │          send_certificate.cpython-312.pyc
    │  │  │          think.cpython-312.pyc
    │  │  │          transfer_to_human_agents.cpython-312.pyc
    │  │  │          update_reservation_baggages.cpython-312.pyc
    │  │  │          update_reservation_flights.cpython-312.pyc
    │  │  │          update_reservation_passengers.cpython-312.pyc
    │  │  │          __init__.cpython-312.pyc
    │  │  │
    │  │  └─__pycache__
    │  │          env.cpython-312.pyc
    │  │          rules.cpython-312.pyc
    │  │          wiki.cpython-312.pyc
    │  │          __init__.cpython-312.pyc
    │  │
    │  ├─retail
    │  │  │  env.py
    │  │  │  rules.py
    │  │  │  tasks.py
    │  │  │  tasks_dev.py
    │  │  │  tasks_test.py
    │  │  │  tasks_train.py
    │  │  │  wiki.md
    │  │  │  wiki.py
    │  │  │  __init__.py
    │  │  │
    │  │  ├─data
    │  │  │      orders.json
    │  │  │      products.json
    │  │  │      readme.md
    │  │  │      users.json
    │  │  │      __init__.py
    │  │  │
    │  │  └─tools
    │  │          calculate.py
    │  │          cancel_pending_order.py
    │  │          exchange_delivered_order_items.py
    │  │          find_user_id_by_email.py
    │  │          find_user_id_by_name_zip.py
    │  │          get_order_details.py
    │  │          get_product_details.py
    │  │          get_user_details.py
    │  │          list_all_product_types.py
    │  │          modify_pending_order_address.py
    │  │          modify_pending_order_items.py
    │  │          modify_pending_order_payment.py
    │  │          modify_user_address.py
    │  │          return_delivered_order_items.py
    │  │          think.py
    │  │          transfer_to_human_agents.py
    │  │          __init__.py
    │  │
    │  └─__pycache__
    │          base.cpython-312.pyc
    │          base.cpython-38.pyc
    │          tool.cpython-312.pyc
    │          tool.cpython-38.pyc
    │          user.cpython-312.pyc
    │          __init__.cpython-312.pyc
    │          __init__.cpython-38.pyc
    │
    ├─model_utils
    │  │  args.py
    │  │  __init__.py
    │  │
    │  ├─api
    │  │      api.py
    │  │      cache.py
    │  │      datapoint.py
    │  │      exception.py
    │  │      logging.py
    │  │      router.py
    │  │      sample.py
    │  │      tokens.py
    │  │      types.py
    │  │      _model_methods.py
    │  │      __init__.py
    │  │
    │  ├─func_tools
    │  │      filter.py
    │  │      map.py
    │  │      __init__.py
    │  │
    │  └─model
    │          anyscale.py
    │          chat.py
    │          claude.py
    │          completion.py
    │          exception.py
    │          general_model.py
    │          mistral.py
    │          model.py
    │          openai.py
    │          outlines_completion.py
    │          utils.py
    │          vllm_chat.py
    │          vllm_completion.py
    │          vllm_utils.py
    │          __init__.py
    │
    └─__pycache__
            types.cpython-312.pyc
            __init__.cpython-312.pyc
            __init__.cpython-38.pyc
