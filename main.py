import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError


# =========================
# 1. 定义 Agent 的输出结构
# =========================

class TaskResult(BaseModel):
    category: Literal[
        "工作",
        "学习",
        "生活",
        "研究",
        "项目开发",
        "其他",
    ]
    priority: Literal["低", "中", "高"]
    next_action: str


# =========================
# 2. 加载环境变量
# =========================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError(
        "没有找到 DEEPSEEK_API_KEY，请检查 .env 文件。"
    )


# =========================
# 3. 创建客户端
# =========================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


# =========================
# 4. Agent 主函数
# =========================

def classify_task(task: str) -> TaskResult:
    """
    输入自然语言任务，
    返回结构化的 TaskResult。
    """

    response = client.responses.create(
        model="deepseek-v4-flash",
        instructions="""
你是一个任务分类助手。

请分析用户给出的任务，并只返回一个 JSON 对象。

category 只能是：
- 工作
- 学习
- 生活
- 研究
- 项目开发
- 其他

priority 只能是：
- 低
- 中
- 高

next_action：
用一句话说明用户下一步最应该做什么。

要求：
1. 只返回 JSON。
2. 不要输出 Markdown。
3. 不要输出 ```json。
4. 不要输出额外解释。
""",
        input=task,
    )

    raw_text = response.output_text

    # JSON 解析
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError(
            f"模型返回的内容不是合法 JSON：\n{raw_text}"
        )

    # Schema 验证
    try:
        result = TaskResult.model_validate(data)
    except ValidationError as e:
        raise ValueError(
            f"模型返回的数据不符合要求：\n{e}"
        )

    return result


# =========================
# 5. 程序入口
# =========================

def main():
    task = input("请输入你的任务：").strip()

    if not task:
        print("错误：任务不能为空。")
        return

    try:
        result = classify_task(task)

    except Exception as e:
        print("\n程序运行失败：")
        print(e)
        return

    print("\n最终结构化结果：")
    print(result)

    print("\n最终 JSON：")
    print(result.model_dump_json(
        indent=2,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    main()