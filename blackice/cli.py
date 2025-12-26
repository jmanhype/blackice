"""
BLACKICE CLI
============

Command-line interface for the software factory.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="blackice",
    help="Neuro-symbolic software factory",
    add_completion=False,
)

console = Console()


def banner():
    """Print the BLACKICE banner."""
    console.print("""
[bold blue]
 ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██╗ ██████╗███████╗
 ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝██║██╔════╝██╔════╝
 ██████╔╝██║     ███████║██║     █████╔╝ ██║██║     █████╗
 ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ██║██║     ██╔══╝
 ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗██║╚██████╗███████╗
 ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
[/bold blue]
[dim]Neuro-symbolic software factory v0.1.0[/dim]
""")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Debug mode"),
):
    """BLACKICE - Neuro-symbolic software factory."""
    pass


@app.command()
def generate(
    spec: Path = typer.Argument(..., help="Path to spec file (YAML)"),
    output: Path = typer.Option("./output", "--output", "-o", help="Output directory"),
    mode: str = typer.Option("greenfield", "--mode", "-m", help="Generation mode: greenfield, brownfield, hybrid"),
    flywheel: bool = typer.Option(True, "--flywheel/--no-flywheel", help="Use flywheel (generate->test->fix loop)"),
    max_iterations: int = typer.Option(5, "--max-iterations", help="Max flywheel iterations"),
):
    """Generate code from a specification."""
    banner()

    console.print(f"[cyan]Generating from spec:[/cyan] {spec}")
    console.print(f"[cyan]Mode:[/cyan] {mode}")
    console.print(f"[cyan]Output:[/cyan] {output}")

    if not spec.exists():
        console.print(f"[red]Error:[/red] Spec file not found: {spec}")
        raise typer.Exit(1)

    # Load spec
    import yaml
    with open(spec) as f:
        spec_data = yaml.safe_load(f)

    console.print(f"\n[green]Loaded spec:[/green] {spec_data.get('name', 'unknown')}")

    # TODO: Integrate with inference and flywheel
    console.print("\n[yellow]Generation not yet implemented - run with vLLM server[/yellow]")


@app.command()
def extract(
    path: Path = typer.Argument(..., help="Path to codebase to extract from"),
    output: Path = typer.Option("./spec.yaml", "--output", "-o", help="Output spec file"),
    language: str = typer.Option("python", "--language", "-l", help="Primary language"),
):
    """Extract specification from existing codebase."""
    banner()

    console.print(f"[cyan]Extracting from:[/cyan] {path}")
    console.print(f"[cyan]Language:[/cyan] {language}")

    if not path.exists():
        console.print(f"[red]Error:[/red] Path not found: {path}")
        raise typer.Exit(1)

    # Run extraction
    from packages.extraction.src.extractor import extract_spec

    result = extract_spec(path, language)

    # Display results
    table = Table(title="Extraction Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Classes", str(len(result.classes)))
    table.add_row("Functions", str(len(result.functions)))
    table.add_row("Imports", str(len(result.imports)))
    table.add_row("Confidence", f"{result.confidence:.0%}")

    console.print(table)

    # Show patterns
    if result.patterns:
        console.print("\n[cyan]Detected Patterns:[/cyan]")
        for name, value in result.patterns.items():
            console.print(f"  - {name}: {value}")

    if result.naming_conventions:
        console.print("\n[cyan]Naming Conventions:[/cyan]")
        for element, convention in result.naming_conventions.items():
            console.print(f"  - {element}: {convention}")

    # Save spec
    import yaml
    spec_dict = {
        "name": path.name,
        "version": "0.1.0",
        "description": f"Extracted from {path}",
        "mode": "brownfield",
        "patterns": result.patterns,
        "naming_conventions": result.naming_conventions,
        "classes": [{"name": c.name, "methods": c.methods} for c in result.classes],
        "functions": [{"name": f.name, "is_async": f.is_async} for f in result.functions],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        yaml.dump(spec_dict, f, default_flow_style=False)

    console.print(f"\n[green]Spec saved to:[/green] {output}")


@app.command()
def validate(
    path: Path = typer.Argument(..., help="Path to code to validate"),
    gates: str = typer.Option("syntax,types,tests", "--gates", "-g", help="Comma-separated gates to run"),
):
    """Validate code through quality gates."""
    banner()

    console.print(f"[cyan]Validating:[/cyan] {path}")
    console.print(f"[cyan]Gates:[/cyan] {gates}")

    # TODO: Run gates
    console.print("\n[yellow]Validation not yet fully implemented[/yellow]")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8080, "--port", "-p", help="Port to bind to"),
    mcp: bool = typer.Option(True, "--mcp/--no-mcp", help="Enable MCP server"),
):
    """Start the BLACKICE server."""
    banner()

    console.print(f"[cyan]Starting server on:[/cyan] {host}:{port}")
    console.print(f"[cyan]MCP enabled:[/cyan] {mcp}")

    # TODO: Start server
    console.print("\n[yellow]Server not yet implemented[/yellow]")


@app.command()
def init(
    path: Path = typer.Option(".", "--path", "-p", help="Path to initialize"),
    template: str = typer.Option("minimal", "--template", "-t", help="Template: minimal, full, brownfield"),
):
    """Initialize a new BLACKICE project."""
    banner()

    console.print(f"[cyan]Initializing project in:[/cyan] {path}")
    console.print(f"[cyan]Template:[/cyan] {template}")

    # Create config
    config_path = path / "blackice.yaml"
    if config_path.exists():
        console.print(f"[yellow]Warning:[/yellow] {config_path} already exists")
    else:
        import yaml
        config = {
            "version": "0.1.0",
            "mode": "hybrid",
            "inference": {
                "url": "http://localhost:8000",
                "model": "deepseek-ai/deepseek-coder-6.7b-instruct",
            },
            "validation": {
                "gates": ["syntax", "types", "tests"],
            },
        }
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        console.print(f"[green]Created:[/green] {config_path}")

    # Create tasks file
    tasks_path = path / ".blackice" / "tasks.json"
    tasks_path.parent.mkdir(parents=True, exist_ok=True)
    if not tasks_path.exists():
        import json
        with open(tasks_path, "w") as f:
            json.dump({"version": "1.0", "tasks": []}, f)
        console.print(f"[green]Created:[/green] {tasks_path}")

    console.print("\n[green]Project initialized![/green]")


@app.command()
def status():
    """Show project status."""
    banner()

    # Check for config
    config_path = Path("blackice.yaml")
    if not config_path.exists():
        console.print("[yellow]Not a BLACKICE project. Run 'blackice init' first.[/yellow]")
        return

    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    console.print(f"[cyan]Project Mode:[/cyan] {config.get('mode', 'unknown')}")

    # Check for tasks
    tasks_path = Path(".blackice/tasks.json")
    if tasks_path.exists():
        import json
        with open(tasks_path) as f:
            tasks_data = json.load(f)
        tasks = tasks_data.get("tasks", [])

        pending = sum(1 for t in tasks if t.get("status") == "pending")
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
        completed = sum(1 for t in tasks if t.get("status") == "completed")

        console.print(f"\n[cyan]Tasks:[/cyan]")
        console.print(f"  Pending: {pending}")
        console.print(f"  In Progress: {in_progress}")
        console.print(f"  Completed: {completed}")


if __name__ == "__main__":
    app()
