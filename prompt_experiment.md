# Week 02 - Prompt Experiment

## 实验目的

比较不同 Prompt 写法对模型输出稳定性的影响。

重点观察：

- 任务是否理解正确
- category 是否稳定
- priority 是否稳定
- 输出是否符合要求
- 模型是否出现额外内容

---

## Experiment 1 - 模糊 Prompt

### Prompt

帮我分析这个任务。

### Input

帮我研究一下最近的 AI Agent 发展趋势

### 预期

希望模型判断任务类型和优先级。

### 问题

没有明确告诉模型：

- 分析什么
- 输出什么
- category 有哪些选项
- priority 有哪些选项

### 结论

无效 Prompt。

---

## Experiment 2 - 指定 JSON

### Prompt

帮我分析这个任务。

请返回 JSON。

### Input

帮我研究一下最近的 AI Agent 发展趋势

### 改进

明确要求返回 JSON。

### 问题

没有规定 JSON 的具体字段和字段取值。

### 结论

比 Experiment 1 好，但仍然不够稳定。

---

## Experiment 3 - 指定字段

### Prompt

请分析下面的任务，并返回 JSON。

需要包含：

- category
- priority
- next_action

### Input

帮我研究一下最近的 AI Agent 发展趋势

### 改进

明确了输出字段。

### 问题

category 和 priority 的取值仍然没有限制。

### 结论

基本有效，但约束不足。

---

## Experiment 4 - 加入取值约束

### Prompt

请分析下面的任务，并返回 JSON。

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

next_action 用一句话说明下一步动作。

只返回 JSON。

### Input

帮我研究一下最近的 AI Agent 发展趋势

### 观察

模型能够按照指定类别和优先级输出。

### 结论

有效 Prompt。

---

## Experiment 5 - 加入决策规则

### Prompt

你是一个任务分类助手。

请分析用户输入的任务。

### category 分类规则

- 工作：公司工作、客户、会议、汇报、沟通等
- 学习：学习知识、课程、编程练习等
- 生活：购物、家务、个人日常事务等
- 研究：资料搜集、行业研究、趋势分析等
- 项目开发：编写代码、调试程序、开发项目等
- 其他：以上类别都不适用

### priority 判断规则

- 高：有明确且临近的截止时间，或者明显紧急
- 中：近期需要完成，但没有明显紧迫性
- 低：没有明确截止时间，也不紧急

### next_action

用一句话描述用户现在最应该执行的下一步动作。

### 输出要求

只输出 JSON。

category 必须使用指定选项。

priority 必须使用指定选项。

不要输出 Markdown。

不要输出额外解释。

### Input

帮我研究一下最近的 AI Agent 发展趋势

### 观察

模型输出：

{
  "category": "研究",
  "priority": "中",
  "next_action": "搜集近期 AI Agent 发展趋势的相关资料并整理成摘要。"
}

### 结论

目前最稳定。

核心原因：

1. 明确角色
2. 明确任务
3. 明确分类规则
4. 明确优先级规则
5. 明确输出要求

---

## 本日总结

Prompt 稳定性主要来自：

Role
+
Task
+
Rules
+
Constraints
+
Output Format

而不是单纯把 Prompt 写得更长。

# Week 02 Day 2 - Schema Design

## 邮件分类器

### Schema

```text
intent
urgency
action
# Week 02 Day 2 - Test Results

## Test 1
Input:
您好，我们希望了解一下目前项目的阶段性进展，请在本周五前提供一份简要报告，谢谢。

Result:
intent = 询问项目阶段性进展并索取简要报告
urgency = 中

Assessment:
合理。

## Test 2
Input:
您好，我想了解一下贵司是否支持小规模试用，以及试用周期大概是多久？

Result:
intent = 咨询试用支持及周期
urgency = 低

Assessment:
合理。

## Test 3
Input:
客户现场出现严重问题，请今天17:00前给出处理方案，否则将影响明天的项目上线。

Result:
intent = 索取客户现场严重问题的处理方案
urgency = 高

Assessment:
合理。

## Test 4
Input:
您好，昨天发送的项目资料我们已经收到，感谢您的配合。

Result:
intent = 确认已收到项目资料并致谢
urgency = 低

Assessment:
合理。

## Test 5
Input:
您好，目前自动驾驶项目已经进入联调阶段。请您把最新版测试报告和报价单发给我们，同时确认一下下周三上午是否方便召开项目评审会。

Result:
intent = 索取测试报告和报价单并确认评审会时间
urgency = 中

Assessment:
合理。

## 当前发现的问题

1. 多意图邮件如何定义主意图。
2. urgency 中“近期截止”和“紧急截止”的边界需要进一步明确。
3. 明天需要通过 10 条测试进一步验证 Prompt。