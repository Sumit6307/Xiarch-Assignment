import urllib.request
import re
from typing import Dict, Any
from agent.tools.base import BaseTool, ToolResult

class WebPageFetcherTool(BaseTool):
    """Tool for fetching and scraping readable text from a web URL."""

    def __init__(self):
        super().__init__(
            name="web_fetcher",
            description="Fetches raw text content from a given web URL or API endpoint.",
            parameters_schema={
                "url": "Target http or https URL to fetch text from."
            }
        )

    def execute(self, url: str = "", **kwargs) -> ToolResult:
        if self.simulated_failure:
            return ToolResult(
                success=False,
                output=None,
                error="SimulatedToolError: HTTP 403 Forbidden - Access denied by target host."
            )

        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return ToolResult(
                success=False,
                output=None,
                error=f"InvalidURLError: URL must start with http:// or https://. Got: '{url}'"
            )

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AgenticBot/1.0"}
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                content_type = response.headers.get('Content-Type', '')
                raw_bytes = response.read()
                
                # Check for text or HTML
                html_text = raw_bytes.decode('utf-8', errors='ignore')
                
                # Clean HTML tags
                text_only = re.sub(r'<script.*?>.*?</script>', '', html_text, flags=re.DOTALL)
                text_only = re.sub(r'<style.*?>.*?</style>', '', text_only, flags=re.DOTALL)
                text_only = re.sub(r'<[^>]+>', ' ', text_only)
                lines = [line.strip() for line in text_only.splitlines() if line.strip()]
                clean_content = "\n".join(lines[:60]) # Limit to top 60 relevant lines

                if len(clean_content) > 3000:
                    clean_content = clean_content[:3000] + "\n...[truncated]"

                return ToolResult(
                    success=True,
                    output=clean_content,
                    metadata={"url": url, "content_type": content_type, "length": len(clean_content)}
                )
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"WebFetchError: Failed to fetch '{url}': {str(e)}"
            )
