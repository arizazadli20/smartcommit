import json
import subprocess
from pathlib import Path

import typer
from google import genai
from rich.console import Console
from rich.prompt import Prompt

console = Console()
CONFIG_FILE = Path.home() / ".smartcommit_config.json"


def load_api_key() -> str:
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if data.get("gemini_api_key"):
                return data["gemini_api_key"]
        except Exception:
            pass

    console.print("[cyan]No Gemini API key found.[/cyan]")
    api_key = Prompt.ask("Enter your Gemini API key", password=True).strip()

    CONFIG_FILE.write_text(json.dumps({"gemini_api_key": api_key}, indent=2), encoding="utf-8")
    console.print(f"[green]Saved API key to {CONFIG_FILE}[/green]\n")
    return api_key


def get_diff() -> str:
    res = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)

    if res.returncode != 0:
        console.print("[red]Error: Not a git repository or git failed.[/red]")
        raise typer.Exit(code=1)

    diff = res.stdout.strip()
    if not diff:
        console.print("[yellow]No staged changes found. Run 'git add' first.[/yellow]")
        raise typer.Exit(code=0)

    return diff


def generate_message(diff: str, api_key: str) -> str:
    client = genai.Client(api_key=api_key)
    prompt = (
        "You are an expert developer. Read the provided git diff and generate a "
        "single, concise commit message using the Conventional Commits format "
        "(e.g., feat: added login, fix: resolved typo). Do not output any markdown "
        "formatting, explanations, or quotes. Just the raw commit message string.\n\n"
        f"Git Diff:\n{diff}"
    )

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    return response.text.strip().strip("`\"'")


def git_commit(message: str) -> None:
    res = subprocess.run(["git", "commit", "-m", message])

    if res.returncode == 0:
        console.print("[bold green]Changes committed![/bold green]")
    else:
        console.print("[bold red]Commit failed.[/bold red]")
        raise typer.Exit(code=res.returncode)


def run():
    api_key = load_api_key()
    diff = get_diff()

    while True:
        with console.status("[bold cyan]Generating commit message...[/bold cyan]", spinner="dots"):
            try:
                msg = generate_message(diff, api_key)
            except Exception as e:
                console.print(f"[bold red]API Error:[/bold red] {e}")
                raise typer.Exit(code=1)

        console.print(f"\nSuggested Commit:\n[bold green]{msg}[/bold green]\n")

        action = Prompt.ask(
            "[A]ccept, [E]dit, [R]egenerate, or [C]ancel?",
            choices=["a", "e", "r", "c"],
            case_sensitive=False,
            default="a",
        ).lower()

        if action == "a":
            git_commit(msg)
            break
        elif action == "e":
            custom_msg = Prompt.ask("Edit message", default=msg).strip()
            if custom_msg:
                git_commit(custom_msg)
            else:
                console.print("[yellow]Empty message, commit canceled.[/yellow]")
            break
        elif action == "r":
            console.print("[cyan]Regenerating...[/cyan]\n")
        elif action == "c":
            console.print("[yellow]Commit canceled.[/yellow]")
            break


if __name__ == "__main__":
    typer.run(run)
