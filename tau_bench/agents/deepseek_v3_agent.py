
import json
import re
from typing import Dict, List, Any, Optional
import requests


class DeepSeekV3Agent:


    def __init__(
            self,
            api_key: str,
            base_url: str = "https://xingjiabiapi.com/v1",
            model: str = "deepseek-chat",
            use_function_calling: bool = True,
            verbose: bool = False
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.use_function_calling = use_function_calling
        self.verbose = verbose

        self.messages = []
        self.tools = []
        self.tool_executor = None

    def set_tools(self, tools: List[Dict]):
        self.tools = self._convert_to_openai_tools(tools)

    def set_tool_executor(self, executor):
        self.tool_executor = executor

    def set_system_prompt(self, system_prompt: str):
        self.messages = [{"role": "system", "content": system_prompt}]

    def _convert_to_openai_tools(self, functions: List[Dict]) -> List[Dict]:
        tools = []
        for func in functions:
            if "type" in func and func["type"] == "function":
                tools.append(func)
            elif "function" in func:
                tools.append(func)
            else:
                tool = {
                    "type": "function",
                    "function": {
                        "name": func.get("name", ""),
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {
                            "type": "object",
                            "properties": {},
                            "required": []
                        })
                    }
                }
                tools.append(tool)
        return tools

    def _call_api(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 2048,
            "stream": False
        }

        if self.use_function_calling and tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        if self.verbose:
            print(f"\n[API] 调用 {self.model}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code != 200:
                return {
                    "error": True,
                    "message": f"API错误: {response.status_code}",
                    "choices": [{
                        "message": {"role": "assistant", "content": f"API调用失败: {response.status_code}"}
                    }]
                }

            return response.json()

        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "choices": [{
                    "message": {"role": "assistant", "content": f"API异常: {str(e)}"}
                }]
            }

    def _parse_response(self, response: Dict) -> Dict:
        if response.get("error"):
            return {"type": "text", "content": response.get("message", "未知错误")}

        if "choices" not in response or len(response["choices"]) == 0:
            return {"type": "text", "content": "API返回空响应"}

        message = response["choices"][0].get("message", {})

        if "tool_calls" in message and message["tool_calls"]:
            tool_call = message["tool_calls"][0]
            try:
                arguments = json.loads(tool_call["function"]["arguments"])
            except:
                arguments = {}

            return {
                "type": "function_call",
                "name": tool_call["function"]["name"],
                "arguments": arguments,
                "tool_call_id": tool_call.get("id", "")
            }

        return {"type": "text", "content": message.get("content", "")}

    def _execute_function(self, name: str, arguments: Dict, tool_call_id: str = "") -> str:
        if self.tool_executor is None:
            return json.dumps({"error": "工具执行器未设置"})

        try:
            result = self.tool_executor.execute(name, arguments)
            return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": f"执行 {name} 失败: {str(e)}"})

    def step(self, user_input: str = None) -> Dict:
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        response = self._call_api(self.messages, self.tools if self.use_function_calling else None)
        parsed = self._parse_response(response)

        if parsed["type"] == "function_call":
            assistant_message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": parsed.get("tool_call_id", f"call_{len(self.messages)}"),
                    "type": "function",
                    "function": {
                        "name": parsed["name"],
                        "arguments": json.dumps(parsed["arguments"], ensure_ascii=False)
                    }
                }]
            }
            self.messages.append(assistant_message)

            result = self._execute_function(parsed["name"], parsed["arguments"])
            tool_message = {
                "role": "tool",
                "tool_call_id": parsed.get("tool_call_id", f"call_{len(self.messages)}"),
                "content": result
            }
            self.messages.append(tool_message)
        else:
            self.messages.append({"role": "assistant", "content": parsed["content"]})

        return parsed

    def reset(self):
        system_messages = [m for m in self.messages if m["role"] == "system"]
        self.messages = system_messages

    def get_history(self) -> List[Dict]:
        return self.messages


class SimpleToolExecutor:
    """简单的工具执行器"""

    def __init__(self, flights_data: Dict = None):
        self.flights_data = flights_data or {}

    def execute(self, name: str, arguments: Dict) -> str:
        if name == "search_direct_flight":
            return self._search_direct_flight(arguments)
        elif name == "get_user_details":
            return self._get_user_details(arguments)
        elif name == "book_reservation":
            return self._book_reservation(arguments)
        elif name == "cancel_reservation":
            return self._cancel_reservation(arguments)
        else:
            return json.dumps({"status": "success", "message": f"工具 {name} 已执行"})

    def _search_direct_flight(self, args: Dict) -> str:
        mock_flights = [
            {
                "flight_number": "HAT001",
                "origin": args.get("origin", ""),
                "destination": args.get("destination", ""),
                "date": args.get("date", ""),
                "departure_time": "08:00",
                "arrival_time": "10:30",
                "price": 299,
                "available_seats": 15
            }
        ]
        return json.dumps(mock_flights, ensure_ascii=False)

    def _get_user_details(self, args: Dict) -> str:
        return json.dumps({
            "user_id": args.get("user_id", ""),
            "name": "Test User",
            "membership": "gold"
        })

    def _book_reservation(self, args: Dict) -> str:
        return json.dumps({
            "status": "success",
            "reservation_id": "RES_" + str(hash(str(args)))[:8]
        })

    def _cancel_reservation(self, args: Dict) -> str:
        return json.dumps({
            "status": "success",
            "message": f"预订已取消"
        })


class ReActDeepSeekAgent(DeepSeekV3Agent):
    """ReAct模式的Agent"""

    def __init__(self, api_key: str, base_url: str = "https://xingjiabiapi.com/v1",
                 model: str = "deepseek-chat", verbose: bool = False):
        super().__init__(api_key, base_url, model, use_function_calling=False, verbose=verbose)

    def set_system_prompt(self, system_prompt: str):
        tools_desc = []
        for tool in self.tools:
            func = tool.get("function", tool)
            tools_desc.append(f"- {func['name']}: {func.get('description', '无描述')}")

        react_prompt = f"""
## 可用工具
{chr(10).join(tools_desc)}

## 输出格式
Thought: 分析思考
Action: 工具名称
Action Input: {{"参数": "值"}}

或
Final Answer: 最终回复
"""
        self.messages = [{"role": "system", "content": system_prompt + "\n\n" + react_prompt}]

    def step(self, user_input: str = None) -> Dict:
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        response = self._call_api(self.messages, tools=None)

        if response.get("error"):
            return {"type": "text", "content": response.get("message", "错误")}

        content = response["choices"][0]["message"].get("content", "")
        self.messages.append({"role": "assistant", "content": content})

        # 解析Action
        action_match = re.search(r'Action:\s*(\w+)', content)
        input_match = re.search(r'Action Input:\s*(\{.*\})', content, re.DOTALL)

        if action_match and input_match:
            try:
                args = json.loads(input_match.group(1))
                result = self._execute_function(action_match.group(1), args)
                self.messages.append({
                    "role": "user",
                    "content": f"结果: {result}"
                })
                return {"type": "function_call", "name": action_match.group(1), "arguments": args}
            except:
                pass

        return {"type": "text", "content": content}