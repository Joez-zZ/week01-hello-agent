import csv
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


def read_file(filename: str) -> str:
    """
    读取本地文本文件。
    """

    if not os.path.exists(filename):
        return f"文件不存在：{filename}"

    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
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
                "required": ["a", "b", "operation"],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "读取本地文本文件的内容。"
                "当用户要求查看、读取、总结某个本地文本文件时使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": (
                            "需要读取的文件名，例如 notes.txt"
                        ),
                    },
                },
                "required": ["filename"],
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "csv_summary",
        "description": (
            "读取 CSV 文件并返回基本信息，"
            "包括数据行数、列名和前几条数据。"
            "当用户要求查看 CSV 的结构、"
            "数据量、列信息或简单预览时使用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": (
                        "需要读取的 CSV 文件名，"
                        "例如 sales.csv"
                    ),
                },
            },
            "required": ["filename"],
        },
    },
},
]
def csv_summary(filename: str) -> str:
    """
    读取 CSV 文件并返回基本信息。
    """

    if not os.path.exists(filename):
        return f"文件不存在：{filename}"

    try:
        with open(
            filename,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as f:

            reader = csv.DictReader(f)

            rows = list(reader)

            columns = reader.fieldnames or []

        result = {
            "filename": filename,
            "row_count": len(rows),
            "columns": columns,
            "preview": rows[:3],
        }

        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        return f"读取 CSV 失败：{e}"
def execute_tool(tool_name: str, arguments: dict):
    if tool_name == "calculator":
        return calculator(
            a=arguments["a"],
            b=arguments["b"],
            operation=arguments["operation"],
        )

    if tool_name == "read_file":
        return read_file(
            filename=arguments["filename"]
        )
    if tool_name == "csv_summary":
        return csv_summary(
            filename=arguments["filename"]
        )
    raise ValueError(f"未知工具：{tool_name}")
def run_agent(user_input: str):

    messages = [
        {
    "role": "system",
    "content": (
        "你是一个可以使用工具完成任务的助手。"
        "如果任务需要数学计算，请使用 calculator。"
        "如果任务需要读取普通文本文件，请使用 read_file。"
        "如果任务需要查看 CSV 文件的数据结构、"
        "行数、列名或数据预览，请使用 csv_summary。"
        "如果不需要工具，可以直接回答。"
    ),
     },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    if not message.tool_calls:
        print("\n模型没有调用工具。")
        print(message.content)
        return

    tool_call = message.tool_calls[0]

    tool_name = tool_call.function.name

    arguments = json.loads(
        tool_call.function.arguments
    )

    print("\n模型选择工具：", tool_name)
    print("工具参数：", arguments)

    result = execute_tool(
        tool_name,
        arguments,
    )

    print("工具执行结果：")
    print(result)

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
    print(
        final_response
        .choices[0]
        .message
        .content
    )
if __name__ == "__main__":

    user_input = input(
        "请输入任务："
    ).strip()

    if not user_input:
        print("任务不能为空")

    else:
        run_agent(user_input)