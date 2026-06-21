import os
import sys
import json
import time
import importlib.util
from typing import Dict, List, Any
from datetime import datetime


# 动态获取路径 - 自动找到 tasks.py
def find_airline_path():
    """自动查找 airline 环境路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    possible_paths = [
        os.path.join(current_dir, "tau_bench", "envs", "airline"),
        os.path.join(current_dir, "..", "tau_bench", "envs", "airline"),
        r"E:\count\tau-bench-main\tau_bench\envs\airline",
    ]

    for path in possible_paths:
        tasks_file = os.path.join(path, "tasks.py")
        if os.path.exists(tasks_file):
            print(f"✅ 找到任务文件: {tasks_file}")
            return path

    print("❌ 找不到 tasks.py 文件，请检查路径")
    sys.exit(1)


AIRLINE_PATH = find_airline_path()
sys.path.insert(0, AIRLINE_PATH)

from deepseek_v3_agent import DeepSeekV3Agent, ReActDeepSeekAgent

# ============================================
# DeepSeek 官方开放平台 API 配置
# ============================================
API_KEY = "sk-7dd3d2e251ab4d7e93a9022ab96383c2"
BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"


def load_tasks_from_file():
    tasks_file = os.path.join(AIRLINE_PATH, "tasks.py")

    if not os.path.exists(tasks_file):
        print(f"❌ 任务文件不存在: {tasks_file}")
        return []

    print(f"📂 从 {tasks_file} 加载任务...")

    try:
        spec = importlib.util.spec_from_file_location("airline_tasks", tasks_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        tasks = []

        for attr_name in ['TASKS', 'tasks', 'all_tasks']:
            if hasattr(module, attr_name):
                task_list = getattr(module, attr_name)
                if isinstance(task_list, list):
                    tasks = task_list
                    print(f"✅ 找到 {len(tasks)} 个任务 (变量名: {attr_name})")
                    break

        if not tasks:
            for attr_name in dir(module):
                if attr_name.startswith('TASK_') or attr_name.endswith('_task'):
                    task = getattr(module, attr_name)
                    if isinstance(task, dict) and 'instruction' in task:
                        tasks.append(task)
            if tasks:
                print(f"✅ 找到 {len(tasks)} 个任务 (从单个变量)")

        for i, task in enumerate(tasks):
            if 'id' not in task:
                task['id'] = f"task_{i + 1:03d}"

        return tasks

    except Exception as e:
        print(f"❌ 加载失败: {e}")
        return []


class SimpleToolExecutor:
    def execute(self, name: str, arguments: Dict) -> str:
        print(f"  🔧 执行: {name}")

        mock_responses = {
            "search_direct_flight": lambda a: json.dumps([
                {"flight_number": "HAT001", "origin": a.get("origin"), "destination": a.get("destination"),
                 "date": a.get("date"), "departure": "08:00", "arrival": "10:30", "price": 299}
            ]),
            "search_onestop_flight": lambda a: json.dumps([
                {"flight_number": "HAT136", "origin": a.get("origin"), "destination": "ATL", "price": 152},
                {"flight_number": "HAT039", "origin": "ATL", "destination": a.get("destination"), "price": 103}
            ]),
            "get_user_details": lambda a: json.dumps({"user_id": a.get("user_id"), "membership": "gold"}),
            "get_reservation_details": lambda a: json.dumps(
                {"reservation_id": a.get("reservation_id"), "status": "confirmed"}),
            "book_reservation": lambda a: json.dumps({"status": "success", "reservation_id": "RES_123"}),
            "cancel_reservation": lambda a: json.dumps({"status": "success"}),
            "update_reservation_flights": lambda a: json.dumps({"status": "success"}),
            "send_certificate": lambda a: json.dumps({"status": "success", "amount": a.get("amount", 0)}),
            "transfer_to_human_agents": lambda a: json.dumps({"status": "transferred"})
        }

        if name in mock_responses:
            return mock_responses[name](arguments)
        return json.dumps({"status": "success"})


class TauBenchRunner:

    def __init__(self, num_tasks: int = 5):
        self.tasks = load_tasks_from_file()

        if not self.tasks:
            print("❌ 没有加载到任务，程序退出")
            sys.exit(1)

        self.tasks = self.tasks[:num_tasks]
        self.tools = self._get_tools()

        print(f"\n📋 将运行 {len(self.tasks)} 个任务:")
        for i, task in enumerate(self.tasks):
            inst = task.get('instruction', '')[:60]
            print(f"   {i + 1}. {inst}...")

    def _get_tools(self) -> List[Dict]:
        return [
            {"type": "function", "function": {"name": "search_direct_flight", "description": "搜索直飞航班",
                                              "parameters": {"type": "object", "properties": {
                                                  "origin": {"type": "string"}, "destination": {"type": "string"},
                                                  "date": {"type": "string"}
                                              }, "required": ["origin", "destination", "date"]}}},
            {"type": "function", "function": {"name": "search_onestop_flight", "description": "搜索经停航班",
                                              "parameters": {"type": "object", "properties": {
                                                  "origin": {"type": "string"}, "destination": {"type": "string"},
                                                  "date": {"type": "string"}
                                              }, "required": ["origin", "destination", "date"]}}},
            {"type": "function", "function": {"name": "get_user_details", "description": "获取用户信息",
                                              "parameters": {"type": "object",
                                                             "properties": {"user_id": {"type": "string"}},
                                                             "required": ["user_id"]}}},
            {"type": "function", "function": {"name": "get_reservation_details", "description": "获取预订信息",
                                              "parameters": {"type": "object",
                                                             "properties": {"reservation_id": {"type": "string"}},
                                                             "required": ["reservation_id"]}}},
            {"type": "function", "function": {"name": "book_reservation", "description": "预订航班",
                                              "parameters": {"type": "object", "properties": {
                                                  "user_id": {"type": "string"}, "origin": {"type": "string"},
                                                  "destination": {"type": "string"},
                                                  "flight_type": {"type": "string"}, "cabin": {"type": "string"},
                                                  "flights": {"type": "array"}, "passengers": {"type": "array"}
                                              }, "required": ["user_id", "origin", "destination", "flight_type",
                                                              "cabin", "flights", "passengers"]}}},
            {"type": "function", "function": {"name": "cancel_reservation", "description": "取消预订",
                                              "parameters": {"type": "object",
                                                             "properties": {"reservation_id": {"type": "string"}},
                                                             "required": ["reservation_id"]}}},
            {"type": "function", "function": {"name": "update_reservation_flights", "description": "修改航班",
                                              "parameters": {"type": "object",
                                                             "properties": {"reservation_id": {"type": "string"},
                                                                            "new_flights": {"type": "array"}},
                                                             "required": ["reservation_id", "new_flights"]}}},
            {"type": "function", "function": {"name": "send_certificate", "description": "发送补偿券",
                                              "parameters": {"type": "object",
                                                             "properties": {"user_id": {"type": "string"},
                                                                            "amount": {"type": "number"}},
                                                             "required": ["user_id", "amount"]}}},
            {"type": "function", "function": {"name": "transfer_to_human_agents", "description": "转人工客服",
                                              "parameters": {"type": "object",
                                                             "properties": {"summary": {"type": "string"}},
                                                             "required": ["summary"]}}}
        ]

    def create_agent(self, agent_type: str = "function_calling", use_function_calling: bool = True):
        """创建不同模式的 Agent"""
        if agent_type == "react":
            agent = ReActDeepSeekAgent(
                api_key=API_KEY,
                base_url=BASE_URL,
                model=MODEL_NAME,
                verbose=True
            )
        elif agent_type == "act_only":
            agent = DeepSeekV3Agent(
                api_key=API_KEY,
                base_url=BASE_URL,
                model=MODEL_NAME,
                use_function_calling=False,
                verbose=True
            )
        else:
            agent = DeepSeekV3Agent(
                api_key=API_KEY,
                base_url=BASE_URL,
                model=MODEL_NAME,
                use_function_calling=True,
                verbose=True
            )
        agent.set_system_prompt(self._build_system_prompt())
        agent.set_tools(self.tools)
        return agent

    def _build_system_prompt(self) -> str:
        return f"""
你是航空公司客服。帮助用户处理航班预订、修改、取消等请求。

当前时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} EST

规则:
1. 修改操作前必须获得用户确认
2. 一次只能调用一个工具
3. 无法处理时转人工

请开始服务。
"""

    def run_single_task(self, agent, task: Dict, max_turns: int = 20) -> Dict:
        instruction = task.get("instruction", "")
        task_id = task.get("id", "unknown")

        print(f"\n{'=' * 60}")
        print(f"📋 任务: {task_id}")
        print(f"📝 用户: {instruction[:100]}...")
        print(f"{'=' * 60}")

        agent.reset()
        user_input = instruction
        turn = 0
        function_calls = []

        while turn < max_turns:
            turn += 1
            print(f"\n--- Turn {turn}/{max_turns} ---")

            try:
                response = agent.step(user_input)

                if response["type"] == "text":
                    content = response.get('content', '')
                    print(f"🤖 Agent: {content[:200]}")
                    if "##STOP##" in content or "再见" in content or "任务完成" in content:
                        print(f"✅ 任务提前结束于第 {turn} 轮")
                        break
                    user_input = None
                elif response["type"] == "function_call":
                    print(f"🔧 调用: {response['name']}")
                    function_calls.append(response['name'])
                    user_input = None
            except Exception as e:
                print(f"❌ 执行出错: {e}")
                break

        if turn >= max_turns:
            print(f"⚠️ 达到最大轮数限制 ({max_turns} 轮)")

        success = len(function_calls) > 0

        return {
            "task_id": task_id,
            "instruction": instruction[:100],
            "success": success,
            "turns": turn,
            "function_calls": function_calls,
            "total_calls": len(function_calls)
        }

    def run_experiment(self, agent_type: str = "function_calling",
                       num_trials: int = 8, max_turns: int = 20) -> Dict:
        print(f"\n{'=' * 60}")
        print(f"🚀 开始实验 - Agent模式: {agent_type}")
        print(f"📊 任务数: {len(self.tasks)}, 试验次数: {num_trials}, 最大轮数: {max_turns}")
        print(f"{'=' * 60}")

        all_results = []
        tool_executor = SimpleToolExecutor()

        for task_idx, task in enumerate(self.tasks, 1):
            print(f"\n{'#' * 60}")
            print(f"## 任务 {task_idx}/{len(self.tasks)}: {task['id']}")
            print(f"{'#' * 60}")

            task_results = []
            for trial in range(num_trials):
                print(f"\n--- 任务 {task['id']} / 第{trial + 1}/{num_trials}次试验 ---")
                agent = self.create_agent(agent_type=agent_type)
                agent.set_tool_executor(tool_executor)
                result = self.run_single_task(agent, task, max_turns)
                task_results.append(result)
                time.sleep(1)

            all_results.append({
                "task_id": task["id"],
                "instruction": task["instruction"][:100],
                "trials": task_results,
                "success_count": sum(1 for r in task_results if r["success"]),
                "avg_turns": sum(r["turns"] for r in task_results) / num_trials,
                "avg_calls": sum(r["total_calls"] for r in task_results) / num_trials
            })

            success_rate = all_results[-1]["success_count"] / num_trials * 100
            print(f"\n📊 任务 {task['id']} 完成: 成功率 {success_rate:.1f}%")

        total = len(all_results)
        pass_rates = {}

        # 计算 Pass@1, Pass@2, Pass@4, Pass@8
        for k in [1, 2, 4, 8]:
            if k <= num_trials:
                success_count = 0
                for r in all_results:
                    trials = r.get("trials", [])
                    if len(trials) >= k:
                        all_success = True
                        for i in range(k):
                            if not trials[i].get("success", False):
                                all_success = False
                                break
                        if all_success:
                            success_count += 1
                pass_rates[f"pass_{k}"] = (success_count / total) * 100 if total > 0 else 0

        avg_turns_all = sum(r["avg_turns"] for r in all_results) / total if total > 0 else 0
        avg_calls_all = sum(r["avg_calls"] for r in all_results) / total if total > 0 else 0

        print(f"\n{'=' * 60}")
        print(f"📊 最终实验结果 - {agent_type}")
        print(f"{'=' * 60}")
        for k, rate in pass_rates.items():
            print(f"  {k.replace('_', '@')}: {rate:.1f}%")
        print(f"  平均对话轮次: {avg_turns_all:.2f}")
        print(f"  平均工具调用: {avg_calls_all:.2f}")
        print(f"{'=' * 60}")

        return {
            "agent_type": agent_type,
            "api_provider": "DeepSeek Official",
            "model": MODEL_NAME,
            **pass_rates,
            "total_tasks": total,
            "trials_per_task": num_trials,
            "max_turns": max_turns,
            "avg_turns": avg_turns_all,
            "avg_calls": avg_calls_all,
            "details": all_results
        }


def run_all_experiments():
    """运行所有三种模式的实验"""
    print("=" * 60)
    print("🚀 DeepSeek 官方开放平台 API 实验 - 完整对比实验")
    print("=" * 60)
    print(f"📍 API 地址: {BASE_URL}")
    print(f"🤖 模型: {MODEL_NAME}")
    print(f"⚙️ 实验配置:")
    print(f"   - 运行任务数: 5")
    print(f"   - 每任务试验次数: 8")
    print(f"   - 最大对话轮数: 20")
    print("=" * 60)

    # 测试 API 连接
    print("\n🔍 测试 API 连接...")
    try:
        import requests
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": MODEL_NAME, "messages": [{"role": "user", "content": "test"}]},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ API 连接成功！")
        else:
            print(f"⚠️ API 响应异常: {response.status_code}")
    except Exception as e:
        print(f"⚠️ API 连接测试失败: {e}")

    all_experiment_results = {}

    # 1. Function Calling 模式
    print("\n" + "=" * 60)
    print("🔧 实验 1/3: Function Calling 模式")
    print("=" * 60)
    runner = TauBenchRunner(num_tasks=5)
    fc_results = runner.run_experiment(agent_type="function_calling", num_trials=8, max_turns=20)
    all_experiment_results["function_calling"] = fc_results

    output_file = f"deepseek_results_fc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(fc_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Function Calling 结果已保存: {output_file}")

    # 2. ReAct 模式
    print("\n" + "=" * 60)
    print("🔄 实验 2/3: ReAct 模式")
    print("=" * 60)
    runner = TauBenchRunner(num_tasks=5)
    react_results = runner.run_experiment(agent_type="react", num_trials=8, max_turns=20)
    all_experiment_results["react"] = react_results

    output_file = f"deepseek_results_react_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(react_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 ReAct 结果已保存: {output_file}")

    # 3. Act-only 模式
    print("\n" + "=" * 60)
    print("📝 实验 3/3: Act-only 模式")
    print("=" * 60)
    runner = TauBenchRunner(num_tasks=5)
    ao_results = runner.run_experiment(agent_type="act_only", num_trials=8, max_turns=20)
    all_experiment_results["act_only"] = ao_results

    output_file = f"deepseek_results_ao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ao_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Act-only 结果已保存: {output_file}")

    # 保存完整对比结果
    all_results_file = f"deepseek_all_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(all_results_file, "w", encoding="utf-8") as f:
        json.dump(all_experiment_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 完整对比结果已保存: {all_results_file}")

    print("\n✅ 所有实验完成！")
    return all_experiment_results


def main():
    """主函数"""
    run_all_experiments()


if __name__ == "__main__":
    main()