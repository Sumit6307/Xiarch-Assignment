import json
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()

class TraceLogger:
    """Rich visual logger formatting planning traces, tool calls, and failure recovery events."""

    @staticmethod
    def on_event(event_type: str, data: Dict[str, Any]):
        if event_type == "PLANNING_START":
            console.print(Panel(
                f"[bold cyan]🎯 Goal Received:[/bold cyan] {data['goal']}\n[yellow]Decomposing goal into executable step plan...[/yellow]",
                title="[bold yellow]Agentic Planning Phase[/bold yellow]",
                border_style="yellow"
            ))

        elif event_type == "PLANNING_COMPLETE":
            table = Table(title="📋 Decomposed Plan Steps", border_style="cyan", show_header=True)
            table.add_column("Step", style="bold white", width=6)
            table.add_column("Description", style="white")
            table.add_column("Target Tool", style="bold magenta")
            table.add_column("Parameters", style="green")

            for step in data["plan"]:
                table.add_row(
                    str(step.get("step_id", "")),
                    step.get("description", ""),
                    step.get("tool_name", ""),
                    json.dumps(step.get("tool_args", {}))
                )
            console.print(table)
            console.print()

        elif event_type == "STEP_START":
            console.print(f"[bold blue]▶ Step {data['step_id']}:[/bold blue] {data['description']}")

        elif event_type == "TOOL_EXECUTION_ATTEMPT":
            console.print(f"  [dim]⚙ Executing tool:[/dim] [bold magenta]{data['tool']}[/bold magenta] (Attempt {data['attempt']})")
            console.print(f"  [dim]Inputs:[/dim] {json.dumps(data['args'])}")

        elif event_type == "TOOL_SUCCESS":
            status_color = "green" if data['status'] == "SUCCESS" else "yellow"
            console.print(f"  [{status_color}]✔ Tool Execution Output ({data['status']}):[/{status_color}]")
            output_snippet = str(data['output'])
            if len(output_snippet) > 400:
                output_snippet = output_snippet[:400] + "... [truncated]"
            console.print(Panel(output_snippet, border_style=status_color))
            console.print()

        elif event_type == "TOOL_FAILURE":
            console.print(f"  [bold red]✖ Tool Failure Detected:[/bold red] {data['error']}")

        elif event_type == "SELF_CORRECTION_START":
            console.print(Panel(
                f"[bold yellow]🔄 Inducing Self-Correction Mechanism![/bold yellow]\n"
                f"[red]Failed Tool:[/red] {data['failed_tool']}\n"
                f"[red]Error:[/red] {data['error']}\n"
                f"[cyan]Analyzing failure and generating dynamic recovery strategy...[/cyan]",
                title="[bold red]Self-Correction Event[/bold red]",
                border_style="red"
            ))

        elif event_type == "SELF_CORRECTION_COMPLETE":
            console.print(Panel(
                f"[bold green]💡 Recovery Plan Formulated:[/bold green]\n"
                f"[italic]{data['reflection']}[/italic]\n\n"
                f"[bold cyan]Swapping to Tool:[/bold cyan] {data['new_tool']}\n"
                f"[bold cyan]New Parameters:[/bold cyan] {json.dumps(data['new_args'])}",
                title="[bold green]Self-Correction Executed[/bold green]",
                border_style="green"
            ))

        elif event_type == "EXECUTION_COMPLETE":
            console.print(Panel(
                f"[bold green]✨ Goal Execution Complete![/bold green]\n"
                f"Total Duration: {data['duration_seconds']}s | Self-Corrections: {len(data['self_corrections'])}",
                border_style="bold green"
            ))
