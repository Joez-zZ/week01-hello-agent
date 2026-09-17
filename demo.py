from main import classify_email


demo_emails = [
    "请把最新测试报告发给我，本周五之前给我就可以。",
    
    "客户反馈目前测试中出现严重问题，请今天17:00之前给出解决方案，否则会影响明天的验收。",
    
    "感谢您昨天提供的资料，我这边已经收到，后续如果有问题再联系您。",
]


def run_demo():
    print("=" * 60)
    print("Email Agent Demo")
    print("=" * 60)

    for i, email in enumerate(demo_emails, start=1):
        print(f"\n【Demo {i}】")
        print(f"邮件：{email}")

        result = classify_email(email)

        print("分类结果：")
        print(f"  Intent   : {result.intent}")
        print(f"  Urgency  : {result.urgency}")
        print(f"  Action   : {result.action}")


if __name__ == "__main__":
    run_demo()