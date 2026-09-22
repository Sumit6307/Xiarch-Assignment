import os
import json
from typing import Dict, Any
from agent.tools.base import BaseTool, ToolResult

class FileReaderWriterTool(BaseTool):
    """Tool for reading and writing files in the workspace output directory."""

    def __init__(self, base_dir: str = "output"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        super().__init__(
            name="file_ops",
            description="Reads from or writes text/JSON reports to disk files.",
            parameters_schema={
                "action": "'read' or 'write'",
                "filename": "The relative file path (e.g. 'report.md', 'summary.json')",
                "content": "(Optional) Content to write if action is 'write'"
            }
        )

    def execute(self, action: str = "read", filename: str = "report.md", content: str = "", **kwargs) -> ToolResult:
        if self.simulated_failure:
            return ToolResult(
                success=False,
                output=None,
                error="SimulatedToolError: PermissionDenied (FileSystem access blocked)."
            )

        target_path = os.path.join(self.base_dir, os.path.basename(filename))

        if action == "write":
            try:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return ToolResult(
                    success=True,
                    output=f"Successfully wrote {len(content)} characters to {target_path}",
                    metadata={"path": target_path, "bytes": len(content.encode('utf-8'))}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"FileWriteError: Unable to write to {target_path}: {str(e)}"
                )

        elif action == "read":
            if not os.path.exists(target_path):
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"FileNotFoundError: File '{target_path}' does not exist."
                )
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = f.read()
                return ToolResult(
                    success=True,
                    output=data,
                    metadata={"path": target_path, "length": len(data)}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"FileReadError: Unable to read file {target_path}: {str(e)}"
                )

        else:
            return ToolResult(
                success=False,
                output=None,
                error=f"InvalidActionError: Action must be 'read' or 'write', got '{action}'."
            )
