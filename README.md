# Week 01 - Hello Agent

一个基于 DeepSeek API 的最小 AI Agent 示例。

用户输入一段自然语言任务，Agent 会自动分析任务，并返回结构化结果：

- category：任务类别
- priority：优先级
- next_action：下一步行动

## 项目目标

本项目是 AI Agent 学习路线第一周的实践项目。

目标不是做一个复杂的 Agent，而是跑通最基本的链路：

用户输入
→ LLM
→ JSON
→ Schema Validation
→ Python 程序

## 技术栈

- Python
- OpenAI Python SDK
- DeepSeek API
- Pydantic
- python-dotenv
- Git / GitHub

## 项目结构

```text
week01-hello-agent/
│
├── .venv/
├── .env
├── .gitignore
├── main.py
├── README.md
└── requirements.txt