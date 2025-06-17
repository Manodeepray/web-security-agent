from rich import print
from rich.panel import Panel
from rich.console import Console

console = Console()

def showExploitToolsMenu():
    tools = {
        "1": "XSS scripting ",
        "2": "SQL injection (will be added in future)",
        "exit":"EXIT the app"
    }

    menu_text = "\n".join([f"[bold cyan]{k}[/bold cyan]: {v}" for k, v in tools.items()])
    console.print(Panel(menu_text, title="Available Tools", border_style="green"))

    while True:
        choice = input("Enter option number: ").strip()
        if choice in tools:
            console.print(f"[bold green]You chose:[/bold green] {tools[choice]}")
            return choice
        else:
            console.print("[bold red]Invalid choice. Try again.[/bold red]")

# Example usage after your webscanner or pipeline runs
if __name__ == "__main__":
    print(Panel("[bold green]Web Scanner Completed[/bold green]", title="Status"))
    user_choice = showExploitToolsMenu()

    # Dummy handlers
    if user_choice == "1":
        print(">> Running XSS exploit scanner ...")
    elif user_choice == "2":
        print(">> Running SQL injection exploit scanner...")
    elif user_choice == "exit":
        print(">> exiting agent agent...")



