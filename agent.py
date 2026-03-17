# === IMPORTS & CONFIG ===
import anthropic
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# === CONFIGURATION ===
class Config:
    # Claude Settings
    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 1024
    MAX_ITERATIONS = 10
    SYSTEM_PROMPT = (
        "You are a helpful assistant. You have access to tools. "
        "You use a tool when needed. Always respond in German. "
        "When you need a tool, use it — don't guess."
    )

# === TOOL DEFINITIONS ===
tools = [
    {
        "name": "calculator",
        "description": "Calculates mathematical expressions. Use this tool for ALL calculations. - addition, subtractions, multiplications, divisions, percentage calculations, exponentiation. Do NOT use for estimations or approximations, but only for EXACT calculations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression, e.G. '(42 * 17) + 891' or '2**10'",
                }
            },
            "required": ["expression"]
        }
    },

    {
        "name": "current_date",
        "description":
            "Returns the current date, time, and day of the week. "
            "Use this tool when the user asks about today's date, the current time, the day of the week, or any other time-related information.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },

    {
       "name": "text_analysis",
        "description": (
            "Analyzes a text and returns detailed statistics: "
            "word count, character count, sentence count, "
            "average word length, and the 5 most frequent words. "
            "Use this tool when the user wants to analyze, count, "
            "or statistically evaluate a text."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to be analyzed",
                },
            },
            "required": ["text"]
        }
    },

    {
        "name": "web_search",
        "description": (
            "Searches the web using DuckDuckGo and returns titles, URLs, and text snippets. "
            "Use this tool when the user asks about current events or facts you are unsure about, "
            "or anything that requires up-to-date information from the internet. "
            "Do NOT use for questions you can confidently answer from your own knowledge."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g. 'current chancellor of Germany' or 'Python 3.12 new features'"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-5). Default is 3.",
                    "default": 3
                }
            },
            "required": ["query"]
        }
    }
]

# === STOPWORD FILTER ===
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords

german_stopwords = set(stopwords.words('german'))

# === TOOL EXECUTION ===
def run_tool(name, tool_input):
    """
    Executes a tool locally and returns the result as JSON string.
    :param name: Tool name matching a tool definition
    :param tool_input: Dict with tool-specific input parameters
    :return: JSON string with tool result or error
    """

    if name == "calculator":
        try:
            # eval() ist in Production ein Sicherheitsrisiko — nur für Demo!
            # In Production: ast.literal_eval() oder eine Math-Library
            result = eval(tool_input["expression"])
            return json.dumps({
                "expression": tool_input["expression"],
                "result": result
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "error": f"Calculation failed: {str(e)}",
            })

    elif name == "current_date":
        try:
            current_date = datetime.now()
            return json.dumps({
                "date": current_date.strftime("%d.%m.%Y"),
                "time": current_date.strftime("%H:%M:%S"),
                "weekday": current_date.strftime("%A"),
                "iso": current_date.isoformat(),
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "error": f"Receiving current date failed: {str(e)}",
            })

    elif name == "text_analysis":
        try:
            text = tool_input["text"]
            words = text.split()
            sentences = text.count('.') + text.count('!') + text.count('?')
            symbols = len(text)
            avg_word_length = sum(len(w) for w in words) / len(words) if words else 0

            # Count most common words
            count = {}
            for word in words:
                clean = word.lower().strip('.,!?;:()[]"\'')
                if len(clean) > 2 and clean not in german_stopwords: # Exclude words with less than 2 letters AND Stop Words (e.g. "die", "ist", "und", "ein")
                    count[clean] = count.get(clean, 0) + 1
            top_5 = sorted(count.items(), key=lambda x: x[1], reverse=True)[:5]

            return json.dumps({
                "word count": len(words),
                "symbol count": symbols,
                "average word length": round(avg_word_length, 1),
                "top 5 words": [{"wort": w, "anzahl": c} for w, c in top_5],
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "error": f"Test analysis failed: {str(e)}",
            })

    elif name == "web_search":
        try:
            from ddgs import DDGS # only load if needed

            query = tool_input["query"]
            max_results = tool_input.get("max_results", 3) # <- default value wenn Claude nicht mitschickt

            # DDGS().text() returns a list of dicts, each with:
            #   - "title": page title
            #   - "href": URL
            #   - "body": text snippet (usually 1-2 sentences) <- so no summary logic needed
            raw_results = DDGS().text(query, max_results=max_results) # Only pass what Claude actually needs — title, url, snippet

            clean_results = []
            for r in raw_results:
                clean_results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })

            return json.dumps({
                "query": query,
                "result_count": len(clean_results),
                "results": clean_results,
            }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "error": f"Web search failed: {str(e)}",
            })

    else:
        return json.dumps({"error": f"Unknown tool: {name}"})

# === CONVERSATION STATE ===
# Persists across agent runs for conversation memory (Silver)
conversation_history = []

# === AGENT LOOP ===
def agent_run(user_query, max_iterations, model, system_prompt, max_tokens):
    """
    Sends a query to the agent and executes the tool-use loop.
    Uses conversation_history for cross-query memory (Silver).
    :param user_query: The user's question as string
    :param max_iterations: Safety limit for loop iterations
    :param model: Claude model identifier
    :param system_prompt: System prompt for Claude
    :param max_tokens: Max tokens per API response
    """

    print(f"\n{'='*60}")
    print(f"USER: {user_query}")
    print(f"{'='*60}")

    conversation_history.append({"role": "user", "content": user_query})

    run_count = 0
    total_tokens = 0

    while True:
        run_count += 1
        print(f"\n--- Loop number: {run_count} ---")

        # Call claude API
        response = client.messages.create(
            model = model,
            max_tokens = max_tokens,
            system = system_prompt,
            tools = tools,
            messages = conversation_history
        )

        # Token tracking
        tokens_current_run = response.usage.input_tokens + response.usage.output_tokens
        total_tokens += tokens_current_run
        print(f"Stop Reason: {response.stop_reason} | Tokens: {total_tokens}")

        # Logic for proceeding
        # Case 1: Claude is finished - return final answer and run statistics
        if response.stop_reason == "end_turn":
            # Add final message to history
            conversation_history.append({"role": "assistant", "content": response.content})
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAgent: {block.text}")
            print(f"\n[Total: {run_count} Runs, {total_tokens} Tokens]")
            return

        # Case 2: Claude wants to use a Tool
        elif response.stop_reason == "tool_use":

            # Append assistant answer to history
            conversation_history.append({"role": "assistant", "content": response.content})

            # Execute tool
            tool_results = []
            for block in response.content:
                if block.type == "tool_use": # Savety block to not crash if block is only string
                    print(f"  → Tool: {block.name}")
                    print(f"    Input: {json.dumps(block.input, ensure_ascii=False)}")

                    # Run tool locally:
                    result = run_tool(block.name, block.input)
                    print(f"    Tool result: {result[:200]}{'...' if len(result) > 200 else ''}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

            # Return tool results to claude
            conversation_history.append({"role": "user", "content": tool_results})

        # Savety stop to precent endless loops
        if run_count >= max_iterations :
            print("Warning: Maximal number of iterations reached. Stopping Agent call")
            return



# === INTERACTIVE MODE ===
if __name__ == "__main__":
    print("=" * 60)
    print(f"AGENT Started — {len(tools)} Tools defined: {[t['name'] for t in tools]}")
    print("Enter 'quit' to terminate run")
    print("=" * 60)

    while True:
        query = input("\nYour query: ")
        if query.lower() in ["quit", "exit", "q"]:
            print("Agent terminated.")
            break
        if query.strip() == "":
            continue
        agent_run(query, model=Config.MODEL, system_prompt=Config.SYSTEM_PROMPT, max_tokens=Config.MAX_TOKENS, max_iterations=Config.MAX_ITERATIONS)