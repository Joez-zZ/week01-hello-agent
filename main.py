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

用简洁的中文短语描述邮件要求完成的主要事项。

不要把“尽快”“麻烦”“谢谢”等礼貌或催促语气作为 intent 的核心内容。

例如：

“这件事情比较重要，麻烦尽快处理。”

intent 应概括为：
“请求处理事项”

而不是：
“催促尽快处理重要事项”

【urgency：紧急程度】

只能选择：
- 高
- 中
- 低

判断规则：

高：
- 邮件明确要求今天完成
- 邮件明确要求明天完成
- 邮件存在 24 小时以内的明确截止时间
- 邮件明确说明延误会影响上线、验收、交付等关键结果
- 已经发生严重问题，并且正在影响当前工作、测试或联调

中：
- 邮件要求在 2 天以后完成
- 邮件只有“尽快”“麻烦处理”“比较重要”等表达，
  但没有明确截止时间，也没有明确严重后果
- 有明确任务要求，但当前没有立即风险

低：
- 没有明确时间要求
- 没有明显紧迫性
- 普通咨询
- 感谢
- 确认信息
- 一般资料索取

特别规则：

1. “尽快”本身不能判定为高。
2. “本周”“下周”等时间表达，
   如果不是今天或明天，默认判定为中。
3. 如果明确给出具体日期，
   只有距离当前时间不超过 24 小时才判定为高。
4. 如果存在“否则会影响上线/验收/交付”等明确后果，
   即使没有具体时间，也可以判定为高。

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