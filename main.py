import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError


# =========================
# 1. 定义输出结构
# =========================

class TaskResult(BaseModel):
    category: Literal[
        "工作",
        "学习",
        "生活",
        "研究",
        "项目开发",
        "其他"
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
# 3. 创建 DeepSeek 客户端
# =========================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


# =========================
# 4. 用户任务
# =========================

task = input("请输入你的任务：").strip()

if not task:
    print("错误：任务不能为空。")
    raise SystemExit(1)


# =========================
# 5. 调用模型
# =========================

try:
    response = client.responses.create(
        model="deepseek-v4-flash",
        instructions="""
        你是一个任务分类助手。

        请分析用户给出的任务，并只返回一个 JSON 对象。

        JSON 必须严格包含以下三个字段：

        category：
        只能选择：
        - 工作
        - 学习
        - 生活
        - 研究
        - 项目开发
        - 其他

        priority：
        只能选择：
        - 低
        - 中
        - 高

        next_action：
        用一句话说明用户下一步最应该做什么。

        要求：
        1. 只返回 JSON。
        2. 不要输出 Markdown。
        3. 不要输出额外解释。
        """,
        input=task,
    )

except Exception as e:
    print("\nAPI 调用失败。")
    print("错误信息：", e)
    raise SystemExit(1)

# =========================
# 6. 先看看模型原始输出
# =========================

raw_text = response.output_text

print("模型原始输出：")
print(raw_text)


# =========================
# 7. JSON 解析
# =========================

try:
    data = json.loads(raw_text)

except json.JSONDecodeError:
    print("\n错误：模型返回的内容不是合法 JSON。")
    print("原始返回：")
    print(raw_text)

    raise SystemExit(1)


# =========================
# 8. Pydantic 验证
# =========================

try:
    result = TaskResult.model_validate(data)

except ValidationError as e:
    print("\n错误：模型返回的数据不符合要求。")
    print(e)

    print("\n模型原始 JSON：")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    raise SystemExit(1)

# =========================
# 9. 最终结果
# =========================

print("\n最终结构化结果：")
print(result)

print("\n最终 JSON：")
print(
    result.model_dump_json(
        indent=2,
        ensure_ascii=False
    )
)