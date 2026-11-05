import json
import subprocess
from pathlib import Path

from google import genai
from rich.console import Console
from rich.prompt import Prompt
import typer

# Initialize Rich console for styled terminal output
console = Console()

# Configuration path for storing the Gemini API key locally
CONFIG_PATH = Path.home() / ".smartcommit_config.json"


def get_api_key() -> str:
    # 1. Check if the config file already exists and load the stored key
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                api_key = data.get("gemini_api_key")
                if api_key:
                    return api_key
        except Exception:
            # If reading the config file fails, fall through to prompt the user
            pass

    # 2. If no key is found, prompt the user to input their Gemini API key
    console.print("[cyan]No Gemini API key found.[/cyan]")
    api_key = Prompt.ask("Please enter your Gemini API key", password=True).strip()

    # 3. Save the API key to ~/.smartcommit_config.json for future sessions
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"gemini_api_key": api_key}, f, indent=2)

    console.print(f"[green]API key saved to {CONFIG_PATH}[/green]\n")
    return api_key


def get_staged_diff() -> str:
    # 1. Run 'git diff --staged' using subprocess to capture staged changes
    result = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True,
        text=True
    )

    # 2. Check if git executed successfully (e.g., verifying this is a git repo)
    if result.returncode != 0:
        console.print("[red]Error: Not a git repository (or git command failed).[/red]")
        raise typer.Exit(code=1)

    diff_text = result.stdout.strip()

    # 3. If there are no staged files, show a yellow warning and exit gracefully
    if not diff_text:
        console.print("[yellow]No staged files found. Run 'git add' first.[/yellow]")
        raise typer.Exit(code=0)

    return diff_text


def generate_commit_message(diff: str, api_key: str) -> str:
    # 1. Initialize the new Google GenAI SDK client
    client = genai.Client(api_key=api_key)

    # 2. Define the strict prompt for Conventional Commit format
    prompt = (
        "You are an expert developer. Read the provided git diff and generate a "
        "single, concise commit message using the Conventional Commits format "
        "(e.g., feat: added login, fix: resolved typo). Do not output any markdown "
        "formatting, explanations, or quotes. Just the raw commit message string.\n\n"
        f"Git Diff:\n{diff}"
    )

    # 3. Generate content using the new SDK and gemini-3.8-flash
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    # 4. Clean up any accidental markdown or quotes from the response
    message = response.text.strip().strip("`").strip('"').strip("'")
    return message


def commit_changes(message: str) -> None:
    # 1. Execute 'git commit -m "<message>"' via subprocess
    result = subprocess.run(["git", "commit", "-m", message])

    # 2. Display success or failure message based on git's exit code
    if result.returncode == 0:
        console.print("[bold green]Successfully committed changes![/bold green]")
    else:
        console.print("[bold red]Commit failed.[/bold red]")
        raise typer.Exit(code=result.returncode)


def main():
    # 1. Retrieve the Gemini API key from local config or user prompt
    api_key = get_api_key()

    # 2. Extract the staged git diff (exits early if no staged changes exist)
    diff = get_staged_diff()

    # 3. Interactive terminal loop for review and confirmation
    while True:
        # Show a rich loading spinner while waiting for Gemini API response
        with console.status("[bold cyan]Generating commit message...[/bold cyan]", spinner="dots"):
            try:
                commit_message = generate_commit_message(diff, api_key)
            except Exception as e:
                console.print(f"[bold red]API Error:[/bold red] {e}")
                raise typer.Exit(code=1)

        # Print the suggested commit message in bold green
        console.print("\nSuggested Commit Message:")
        console.print(f"[bold green]{commit_message}[/bold green]\n")

        # Prompt user to choose an action
        choice = Prompt.ask(
            "[A]ccept, [E]dit, [R]egenerate, or [C]ancel?",
            choices=["a", "e", "r", "c", "A", "E", "R", "C"],
            default="a"
        ).lower()

        # Handle user choice
        if choice == "a":
            # Accept and commit immediately
            commit_changes(commit_message)
            break
        elif choice == "e":
            # Edit the suggested message before committing
            edited_message = Prompt.ask("Edit message", default=commit_message).strip()
            if edited_message:
                commit_changes(edited_message)
            else:
                console.print("[yellow]Commit message cannot be empty. Canceled.[/yellow]")
            break
        elif choice == "r":
            # Request a new generation from the API
            console.print("[cyan]Regenerating commit message...[/cyan]\n")
            continue
        elif choice == "c":
            # Exit without committing
            console.print("[yellow]Commit canceled.[/yellow]")
            break


# Entry point using typer to run the CLI
if __name__ == "__main__":
    typer.run(main)
