from main import classify_email
from test_cases import TEST_CASES

failed_cases = []
def main():
    intent_correct = 0
    urgency_correct = 0

    print("=" * 60)
    print("Week 02 - Email Classifier Evaluation")
    print("=" * 60)

    for case in TEST_CASES:
        print(f"\n[Test {case['id']}]")
        print("邮件：", case["email"])

        try:
            result = classify_email(case["email"])

        except Exception as e:
            print("运行失败：", e)
            continue

        print("实际 intent：", result.intent)
        print("期望 intent：", case["expected_intent"])

        print("实际 urgency：", result.urgency)
        print("期望 urgency：", case["expected_urgency"])

        # -------------------------
        # Intent
        # -------------------------

        intent_ok = input("Intent 是否正确？(y/n)：").strip().lower() == "y"
        if intent_ok:
            intent_correct += 1

        # -------------------------
        # Urgency
        # -------------------------

        urgency_ok = result.urgency == case["expected_urgency"]
        if urgency_ok:
            urgency_correct += 1

        print("Intent：", "✅" if intent_ok else "❌")
        print("Urgency：", "✅" if urgency_ok else "❌")

        print("Action：", result.action)
        if not intent_ok or not urgency_ok:
            failed_cases.append({
                "id": case["id"],
                "intent_ok": intent_ok,
                "urgency_ok": urgency_ok,
            })
    total = len(TEST_CASES)

    print("\n" + "=" * 60)
    print("Evaluation Result")
    print("=" * 60)
    print("\nFailed Cases:")

    if not failed_cases:
        print("None")
    else:
        for case in failed_cases:
            print(case)
    print(
        f"Intent Accuracy: "
        f"{intent_correct}/{total} "
        f"({intent_correct / total:.1%})"
    )

    print(
        f"Urgency Accuracy: "
        f"{urgency_correct}/{total} "
        f"({urgency_correct / total:.1%})"
    )


if __name__ == "__main__":
    main()