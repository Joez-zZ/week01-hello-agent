import json
import time
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

api_key = __import__("os").getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件")


client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


class EmailResult(BaseModel):
    intent: str
    urgency: Literal["低", "中", "高"]
    action: str


SYSTEM_PROMPT = """
你是一个专业的邮件分类助手。

你的任务是分析用户提供的邮件，并输出 JSON。

字段说明：

1. intent
描述邮件的主要意图。
如果存在多个意图，只选择最主要、最需要处理的那个。
不要把“尽快”“麻烦”“谢谢”等礼貌或紧迫表达直接作为 intent。

2. urgency
只能输出：
低 / 中 / 高

判断规则：
- 高：
  今天、明天、24小时内等明确短期限；
  或存在严重问题，可能影响项目、交付、上线、验收、测试等。
- 中：
  有明确任务，但截止时间距离现在超过24小时；
  或只说“尽快”“麻烦处理”“比较重要”等，没有明确短期限或严重后果。
- 低：
  普通咨询、确认、感谢、资料请求等，没有明显时间压力。

特别注意：
“本周”“下周”但没有明确指向今天或明天时，通常判定为“中”。

3. action
给出一个具体、可执行的下一步行动。

只输出合法 JSON，不要输出 Markdown，不要输出解释文字。

格式：

{
  "intent": "...",
  "urgency": "低/中/高",
  "action": "..."
}
"""


def classify_email_once(email_text: str) -> EmailResult:
    """
    只负责执行一次模型调用。
    如果模型调用、JSON 解析或结构校验失败，就直接抛出异常。
    """

    response = client.responses.create(
        model="deepseek-v4-flash",
        instructions=SYSTEM_PROMPT,
        input=email_text,
    )

    content = response.output_text

    data = json.loads(content)

    result = EmailResult.model_validate(data)

    return result


def classify_email(
    email_text: str,
    max_retries: int = 3
) -> EmailResult:
    """
    带重试和兜底机制的邮件分类函数。
    """

    for attempt in range(1, max_retries + 1):
        try:
            result = classify_email_once(email_text)

            print(f"第 {attempt} 次调用成功")

            return result

        except Exception as e:
            print(f"第 {attempt} 次调用失败：{e}")

            if attempt < max_retries:
                wait_seconds = attempt

                print(
                    f"{wait_seconds} 秒后进行第 "
                    f"{attempt + 1} 次重试..."
                )

                time.sleep(wait_seconds)

    print("连续重试失败，进入兜底机制。")

    return EmailResult(
        intent="无法判断",
        urgency="中",
        action="请人工查看该邮件"
    )


if __name__ == "__main__":
    email = input("请输入邮件内容：").strip()

    if not email:
        print("邮件内容不能为空")
    else:
        try:
            result = classify_email(email)

            print("\n分类结果：")
            print(result.model_dump_json(indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"程序发生未预期错误：{e}")