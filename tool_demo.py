import json
import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件")


client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


def calculator(a: float, b: float, operation: str) -> float:
    """
    执行基础数学运算。
    """

    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("除数不能为 0")
        return a / b

    raise ValueError(f"不支持的操作：{operation}")


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行基础数学运算，包括加法、减法、乘法和除法。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字",
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字",
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                        ],
                        "description": "要执行的数学运算",
                    },
                },
                "required": [
                    "a",
                    "b",
                    "operation",
                ],
            },
        },
    }
]


messages = [
    {
        "role": "system",
        "content": (
            "你是一个可以使用计算工具的助手。"
            "当用户需要数学计算时，请使用 calculator 工具。"
        ),
    },
    {
        "role": "user",
        "content": "今天北京有什么好玩的？",
    },
]


response = client.chat.completions.create(
    model="deepseek-flash",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

message = response.choices[0].message


if message.tool_calls:
    tool_call = message.tool_calls[0]

    tool_name = tool_call.function.name
    tool_arguments = json.loads(
        tool_call.function.arguments
    )

    print("模型选择工具：", tool_name)
    print("工具参数：", tool_arguments)

    if tool_name == "calculator":
        result = calculator(
            a=tool_arguments["a"],
            b=tool_arguments["b"],
            operation=tool_arguments["operation"],
        )

        print("工具执行结果：", result)

        messages.append(message)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            }
        )

        final_response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        print("\n最终回答：")
        print(final_response.choices[0].message.content)

else:
    print("模型没有调用工具。")
    print(message.content)