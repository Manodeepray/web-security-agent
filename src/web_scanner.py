from pipelines.execution_pipeline import task_execution
from pipelines.extraction_pipeline import task_extraction
import argparse


from rich import print
from rich.panel import Panel
from rich.console import Group
from rich.text import Text

import json


parser = argparse.ArgumentParser(description="Optional URL argument with default")



parser.add_argument(
        '--url',
        type=str,
        default='http://127.0.0.1:5000',
        help='Base URL of the server (default: http://127.0.0.1:5000)'
    )

    # Parse the arguments
args = parser.parse_args()

# Use the URL
URL = args.url

print(f"Using URL: {URL}")
    


print(Panel("[bold green]INITIALIZING STAGE 1/3: EXTRACTOR AGENT[/bold green]", title="Startup"))

combined_response , tasks_response , detailed_workflows , WORKFLOW_DIR , workflow_paths = task_extraction.main(URL = URL)
print(Panel("[bold red]CLOSING AGENT LOOP[/bold red]", title="Shutdown"))

print(" \n\n\n\n\n")

print(Panel("[bold green]INITIALIZING STAGE 2/3 : EXECUTOR AGENT[/bold green]", title="Startup"))

states  , failed = task_execution.batch_execution(workflow_paths=workflow_paths , url= URL)

print(Panel("[bold red]CLOSING EXECUTOR AGENT LOOP[/bold red]", title="Shutdown"))

# Pretty-print the failed dict with indentation
if failed:
    failed_str = json.dumps(failed, indent=4)
    print(Panel(Text(failed_str, style="red"), title="Failed Details", border_style="red"))
else:
    print(Panel(Text("No failures reported.", style="green"), title="Failed Details", border_style="green"))




