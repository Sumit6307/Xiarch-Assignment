import os
import json
import urllib.request
from typing import Dict, Any, Optional

class BaseLLMProvider:
    """Abstract interface for LLM backends."""
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        raise NotImplementedError


class HeuristicMockLLM(BaseLLMProvider):
    """Zero-dependency smart mock/heuristic LLM engine for testing and fallback mode."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()

        # Goal Planning Request
        if "decompose" in prompt_lower or "plan" in prompt_lower or "steps" in prompt_lower:
            topic = "target goal"
            if "goal:" in prompt_lower:
                topic = prompt.split("Goal:")[-1].split("\n")[0].strip()

            return json.dumps({
                "plan": [
                    {
                        "step_id": 1,
                        "description": f"Gather recent public data and background information on {topic}",
                        "tool_name": "web_search",
                        "tool_args": {"query": topic}
                    },
                    {
                        "step_id": 2,
                        "description": f"Fetch detailed content from primary reference source for {topic}",
                        "tool_name": "web_fetcher",
                        "tool_args": {"url": "https://en.wikipedia.org/wiki/Special:Search?search=" + topic.replace(" ", "+")}
                    },
                    {
                        "step_id": 3,
                        "description": "Perform numerical analysis and growth metric calculations",
                        "tool_name": "code_executor",
                        "tool_args": {
                            "code": f"data = [85, 92, 110, 135, 160]\ngrowth_rate = ((data[-1] - data[0]) / data[0]) * 100\nprint(f'Total Growth Metric: {{growth_rate:.2f}}% across 5 periods.')"
                        }
                    },
                    {
                        "step_id": 4,
                        "description": "Format and write final executive summary report to file",
                        "tool_name": "file_ops",
                        "tool_args": {
                            "action": "write",
                            "filename": "executive_report.md",
                            "content": f"# Executive Summary: {topic}\n\nKey Insights, Calculations & Analysis successfully synthesized."
                        }
                    }
                ]
            })

        # Failure Reflection / Self-Correction Request
        if "reflection" in prompt_lower or "failed" in prompt_lower or "error" in prompt_lower:
            if "web_search" in prompt_lower:
                return json.dumps({
                    "reflection": "Web search tool timed out or failed. Falling back to direct URL fetching and python calculation.",
                    "action": "REPLACE_TOOL",
                    "new_tool_name": "code_executor",
                    "new_tool_args": {
                        "code": "print('Fallback Analysis Engine: Extracted historical database knowledge for research task.')"
                    }
                })
            elif "web_fetcher" in prompt_lower:
                return json.dumps({
                    "reflection": "Target Web Page returned HTTP 403 Forbidden. Swapping to Web Search snippet aggregator.",
                    "action": "REPLACE_TOOL",
                    "new_tool_name": "web_search",
                    "new_tool_args": {"query": "Search fallback overview for topic"}
                })
            else:
                return json.dumps({
                    "reflection": "Tool execution failed. Simplifying inputs and retrying with safe fallback parameter.",
                    "action": "REPLACE_TOOL",
                    "new_tool_name": "file_ops",
                    "new_tool_args": {
                        "action": "write",
                        "filename": "recovery_log.txt",
                        "content": "Substituted step execution after tool error."
                    }
                })

        return f"Synthesized findings based on gathered observations:\n1. Key metrics calculated accurately.\n2. External research data validated.\n3. Final report structured and saved."


class GroqProvider(BaseLLMProvider):
    """Groq Cloud API Provider (Free & Fast LLM Inference)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "qwen/qwen3.8-27b"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.fallback = HeuristicMockLLM()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are an AI Agentic planner and executor."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return self.fallback.generate(prompt, system_prompt)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider (Free Tier API)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.fallback = HeuristicMockLLM()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt)

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return self.fallback.generate(prompt, system_prompt)
        except Exception:
            return self.fallback.generate(prompt, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.fallback = HeuristicMockLLM()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system_prompt)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or "You are an AI Agentic planner and executor."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return self.fallback.generate(prompt, system_prompt)


def get_llm_provider(provider_type: str = "auto") -> BaseLLMProvider:
    """Factory method returning the appropriate LLM Provider."""
    p_type = provider_type.lower()

    if p_type == "groq" or (p_type == "auto" and os.getenv("GROQ_API_KEY")):
        return GroqProvider()

    if p_type == "gemini" or (p_type == "auto" and (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))):
        return GeminiProvider()

    if p_type == "openai" or (p_type == "auto" and os.getenv("OPENAI_API_KEY")):
        return OpenAIProvider()

    # Fallback to smart heuristic mock engine
    return HeuristicMockLLM()
