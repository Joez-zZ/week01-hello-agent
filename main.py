import json
import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ValidationError


# =========================
# 1. 定义 Agent 的输出结构
# =========================

class EmailResult(BaseModel):
    intent: str
    urgency: Literal["低", "中", "高"]
    action: str

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

def classify_email(email: str) -> EmailResult:
    """
    输入自然语言任务，
    返回结构化的 TaskResult。
    """

    response = client.responses.create(
        model="deepseek-v4-flash",
        instructions="""
你是一个专业的企业邮件分析助手。

你的任务是阅读一封邮件，并提取以下三个字段：

1. intent
2. urgency
3. action

【intent：邮件意图】

用简洁的中文短语概括这封邮件最主要的目的。

例如：
- 询问项目进展
- 索取资料
- 索取报价
- 咨询产品能力
- 投诉问题
- 邀请会议
- 确认信息
- 提供信息

如果示例都不适用，请根据邮件内容自行概括。

如果一封邮件包含多个意图，
选择其中最主要、最需要处理的一个作为 intent。

【urgency：紧急程度】

只能选择：
- 高
- 中
- 低

判断规则：

高：
- 明确要求在今天或明天完成
- 有临近截止时间
- 明确表达紧急、严重、影响上线、影响交付等情况

中：
- 近期需要处理
- 有一定时间要求
- 但没有明显紧迫性

低：
- 没有明确截止时间
- 没有明显紧迫性
- 主要用于信息确认、感谢或普通咨询

【action：下一步行动】

描述收到邮件后最应该采取的下一步动作。

要求：
- 必须具体
- 必须可执行
- 尽量包含必要的对象和时间要求
- 如果邮件明确提出截止时间，应在 action 中体现

【输出要求】

只返回 JSON。

必须包含：

{
  "intent": "...",
  "urgency": "...",
  "action": "..."
}

urgency 必须严格使用：
高 / 中 / 低

不要输出 Markdown。
不要输出 ```json。
不要输出解释。
不要添加其他字段。
""",
        input=email,
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
        result = EmailResult.model_validate(data)
    except ValidationError as e:
        raise ValueError(
            f"模型返回的数据不符合要求：\n{e}"
        )

    return result


# =========================
# 5. 程序入口
# =========================

def main():
    email = input("请输入邮件内容：").strip()

    if not email:
        print("错误：邮件内容不能为空。")
        return

    try:
        result = classify_email(email)

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