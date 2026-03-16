# 🤖 Claude Agent Toolbox

> **Learning Project**: Building an autonomous AI agent with tool use from scratch — Claude SDK, agentic loop, conversation memory, structured output, and production error handling.

---

## 🎯 What This Is

An autonomous agent that decides **on its own** which tools to use:

**User question → Claude analyzes intent → Selects & calls tools → Processes results → Returns answer**

Built as the Week 3 project for the KI & Python Advanced module at Morphos GmbH.

---

## 🏆 Challenge Status

| Level | What | Status |
|---|---|---|
| 🥉 Bronze | Agent loop + 3 tools + 5 test queries | ✅ Done |
| 🥈 Silver | 4th custom tool + conversation history | ⬜ Todo |
| 🥇 Gold | Structured output (tool_choice) + error handling | ⬜ Todo |

---

## 🛠️ Available Tools

| Tool | Description | Example Query |
|---|---|---|
| `calculator` | Evaluates math expressions (all operators, exponentiation) | "Was ist 847 mal 293?" |
| `current_date` | Returns current date, time, and weekday | "Was ist das heutige Datum?" |
| `text_analysis` | Word count, sentence count, avg word length, top 5 words | "Analysiere diesen Text: ..." |

### Planned Tools (Silver)

| Tool | Description |
|---|---|
| `translator` or `unit_converter` | 4th tool — TBD |

---

## ⚙️ How The Agent Loop Works

```
1. User asks a question
2. Claude receives query + tool definitions
3. Claude responds:
   → stop_reason == "end_turn"  → Final answer, loop ends
   → stop_reason == "tool_use"  → Claude wants to call a tool
4. Tool is executed locally
5. Result is sent back to Claude
6. Back to step 3
```

The agent handles **multi-tool queries** — e.g. asking for today's date AND a calculation in one question triggers both tools in a single loop iteration.

---

## 🗂️ Project Structure

```
claude-agent-toolbox/
├── agent.py              ← Main agent — tools, loop, interactive mode
├── bronze_test_results.md ← Documented test results for 5 test queries
├── .env                  ← API key (not committed)
├── .env.example          ← Template for environment variables
└── requirements.txt      ← Dependencies
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Anthropic API Key

### Installation

```bash
git clone https://github.com/yourusername/claude-agent-toolbox.git
cd claude-agent-toolbox

python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
```

`.env.example`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Run the Agent

```bash
python agent.py
```

---

## 🧪 Test Results (Bronze)

5 mandatory test queries — documented in `bronze_test_results.md`:

| # | Query | Expected Tool | Result |
|---|---|---|---|
| 1 | "Was ist das heutige Datum?" | `current_date` | ✅ |
| 2 | "Was ist 847 mal 293?" | `calculator` | ✅ |
| 3 | Text analysis query | `text_analysis` | ✅ |
| 4 | Date + calculation (multi-tool) | `current_date` + `calculator` | ✅ |
| 5 | "Erkläre mir was Machine Learning ist." | NONE (pure LLM) | ✅ |

---

## ✨ Extra Features

| Feature | Description |
|---|---|
| **Config class** | Centralized settings — model, max tokens, max iterations, system prompt |
| **NLTK stopword filtering** | Text analysis filters German stopwords (articles, pronouns, etc.) for more meaningful word frequency results |
| **English codebase** | All variables, comments, and docstrings in English — agent responds in German |
| **Token tracking** | Every agent run logs input + output tokens per loop iteration |

---

## 📋 Planned Features

| Feature | Challenge Level | Description |
|---|---|---|
| 4th custom tool | 🥈 Silver | Translator or unit converter |
| Conversation history | 🥈 Silver | Agent remembers previous questions across turns |
| Structured output | 🥇 Gold | Force JSON schema via `tool_choice` |
| Error handling wrapper | 🥇 Gold | Agent never crashes on bad tool input |
| Reflection document | 🥇 Gold | `reflexion.md` with technical answers + CV bullet point |

---

## 🔬 Tech Stack

| Technology | Purpose |
|---|---|
| **Anthropic Claude SDK** | LLM API + tool use |
| **Claude Sonnet 4** | Model for agent reasoning |
| **Python** | Agent loop, tool execution |
| **NLTK** | German stopword filtering |

---

## ✏️ Author

**Dennis Feyerabend**
KI & Python Advanced — Morphos GmbH — March 2026

---

## 📝 License

Created as part of an AI & Python training program at Morphos GmbH. Learning project for educational purposes.
