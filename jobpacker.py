#!/usr/bin/env python3
"""
JobPacker - Beautiful CLI job harvester for Cleansheet
"""

import json
import math
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from jobspy import scrape_jobs

# Initialize rich console
console = Console()

# Config file path (same directory as script)
CONFIG_PATH = Path(__file__).parent / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "default_search": "",
    "default_location": "USA",
    "results_per_site": 15,
    "remote_only": False,
    "job_type": None,
    "job_boards": ["indeed", "linkedin", "glassdoor", "zip_recruiter", "google"]
}

# Available job boards
ALL_JOB_BOARDS = ["indeed", "linkedin", "glassdoor", "zip_recruiter", "google"]

# Job type options
JOB_TYPES = [None, "fulltime", "parttime", "internship", "contract"]


def load_config() -> dict:
    """Load configuration from file or return defaults."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                config = json.load(f)
                # Merge with defaults in case new options added
                return {**DEFAULT_CONFIG, **config}
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Save configuration to file."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def display_banner() -> None:
    """Display the application banner."""
    banner = """
     ╦╔═╗╔╗ ╔═╗╔═╗╔═╗╦╔═╔═╗╦═╗
     ║║ ║╠╩╗╠═╝╠═╣║  ╠╩╗║╣ ╠╦╝
    ╚╝╚═╝╚═╝╩  ╩ ╩╚═╝╩ ╩╚═╝╩╚═
    """
    console.print(Panel(banner, title="[bold blue]Job Harvester for Cleansheet[/]",
                        subtitle="[dim]Powered by JobSpy[/]", box=box.DOUBLE))


def display_main_menu() -> str:
    """Display main menu and get user choice."""
    console.print("\n[bold cyan]Main Menu[/]")
    console.print("  [1] Search for Jobs")
    console.print("  [2] Settings")
    console.print("  [3] Export Results")
    console.print("  [4] Exit")
    console.print()

    return Prompt.ask("[bold]Select option[/]", choices=["1", "2", "3", "4"], default="1")


def display_settings_menu(config: dict) -> dict:
    """Display and modify settings."""
    while True:
        console.print("\n[bold cyan]Settings[/]")
        console.print(f"  [1] Default Search: [yellow]{config['default_search'] or '(none)'}[/]")
        console.print(f"  [2] Default Location: [yellow]{config['default_location']}[/]")
        console.print(f"  [3] Results per Site: [yellow]{config['results_per_site']}[/]")
        console.print(f"  [4] Remote Only: [yellow]{config['remote_only']}[/]")
        console.print(f"  [5] Job Type: [yellow]{config['job_type'] or 'Any'}[/]")
        console.print(f"  [6] Job Boards: [yellow]{', '.join(config['job_boards'])}[/]")
        console.print("  [0] Back to Main Menu")
        console.print()

        choice = Prompt.ask("[bold]Select option[/]", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")

        if choice == "0":
            save_config(config)
            break
        elif choice == "1":
            config["default_search"] = Prompt.ask("Default search terms", default=config["default_search"])
        elif choice == "2":
            config["default_location"] = Prompt.ask("Default location", default=config["default_location"])
        elif choice == "3":
            config["results_per_site"] = IntPrompt.ask("Results per site", default=config["results_per_site"])
        elif choice == "4":
            config["remote_only"] = Confirm.ask("Remote jobs only?", default=config["remote_only"])
        elif choice == "5":
            console.print("\nJob Types: [dim](none)[/], fulltime, parttime, internship, contract")
            job_type = Prompt.ask("Job type", default=config["job_type"] or "")
            config["job_type"] = job_type if job_type in JOB_TYPES[1:] else None
        elif choice == "6":
            config["job_boards"] = select_job_boards(config["job_boards"])

    return config


def select_job_boards(current: list) -> list:
    """Interactive job board selection."""
    console.print("\n[bold]Select Job Boards[/] (comma-separated numbers)")
    for i, board in enumerate(ALL_JOB_BOARDS, 1):
        status = "[green]✓[/]" if board in current else "[dim]○[/]"
        console.print(f"  {status} [{i}] {board}")

    console.print("\nEnter numbers (e.g., 1,2,3) or 'all' for all boards")
    selection = Prompt.ask("Selection", default="all")

    if selection.lower() == "all":
        return ALL_JOB_BOARDS.copy()

    try:
        indices = [int(x.strip()) for x in selection.split(",")]
        selected = [ALL_JOB_BOARDS[i-1] for i in indices if 1 <= i <= len(ALL_JOB_BOARDS)]
        return selected if selected else current
    except (ValueError, IndexError):
        console.print("[red]Invalid selection, keeping current boards[/]")
        return current


def search_jobs(config: dict) -> tuple[list, str]:
    """Search for jobs using current config or custom parameters.

    Returns:
        Tuple of (jobs list, search term used)
    """
    console.print("\n[bold cyan]Job Search[/]")

    # Get search parameters
    search_term = Prompt.ask("Job title / keywords", default=config["default_search"])
    if not search_term:
        console.print("[red]Search term is required[/]")
        return [], ""

    location = Prompt.ask("Location", default=config["default_location"])

    # Show current settings
    console.print(f"\n[dim]Searching {len(config['job_boards'])} boards, {config['results_per_site']} results each[/]")
    if config["remote_only"]:
        console.print("[dim]Remote jobs only[/]")
    if config["job_type"]:
        console.print(f"[dim]Job type: {config['job_type']}[/]")

    # Perform search with progress indicator
    jobs = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Searching job boards...", total=None)

        try:
            results = scrape_jobs(
                site_name=config["job_boards"],
                search_term=search_term,
                location=location,
                results_wanted=config["results_per_site"],
                is_remote=config["remote_only"],
                job_type=config["job_type"],
                country_indeed="USA"
            )

            progress.update(task, description="Processing results...")

            # Convert DataFrame to list of dicts
            if results is not None and len(results) > 0:
                jobs = results.to_dict("records")

        except Exception as e:
            console.print(f"[red]Search error: {e}[/]")
            return [], search_term

    # Display results
    if not jobs:
        console.print("\n[yellow]No jobs found. Try different search terms or location.[/]")
        return [], search_term

    console.print(f"\n[green]Found {len(jobs)} jobs![/]")
    display_jobs_table(jobs)

    return jobs, search_term


def display_jobs_table(jobs: list) -> None:
    """Display jobs in a formatted table."""
    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Title", style="bold", max_width=30)
    table.add_column("Company", max_width=25)
    table.add_column("Location", max_width=20)
    table.add_column("Source", style="cyan", width=12)

    for i, job in enumerate(jobs[:50], 1):  # Show max 50 in table
        title = str(job.get("title", ""))[:30]
        company = str(job.get("company", ""))[:25]
        location = str(job.get("location", ""))[:20]
        source = str(job.get("site", ""))

        table.add_row(str(i), title, company, location, source)

    console.print(table)

    if len(jobs) > 50:
        console.print(f"[dim]...and {len(jobs) - 50} more (all will be exported)[/]")


def export_jobs(jobs: list, search_term: str = "") -> None:
    """Export jobs to Cleansheet-compatible JSON."""
    if not jobs:
        console.print("\n[yellow]No jobs to export. Run a search first.[/]")
        return

    console.print(f"\n[bold cyan]Export {len(jobs)} Jobs[/]")

    # Build filename with search term and timezone
    # Sanitize search term for filename (replace spaces/special chars)
    safe_search = re.sub(r'[^\w\-]', '_', search_term.lower()).strip('_') if search_term else "jobs"
    safe_search = re.sub(r'_+', '_', safe_search)  # Collapse multiple underscores

    # Get local timezone offset (e.g., -0500, +0100)
    now = datetime.now().astimezone()
    tz_offset = now.strftime('%z')  # Returns like -0500 or +0100

    default_name = f"{safe_search}_{now.strftime('%Y%m%d_%H%M%S')}{tz_offset}.json"
    filename = Prompt.ask("Filename", default=default_name)

    if not filename.endswith(".json"):
        filename += ".json"

    # Convert to Cleansheet format
    cleansheet_jobs = []
    for job in jobs:
        # Handle date formatting
        date_posted = job.get("date_posted")
        if date_posted:
            if hasattr(date_posted, "strftime"):
                date_posted = date_posted.strftime("%Y-%m-%d")
            else:
                date_posted = str(date_posted)[:10]
        else:
            date_posted = datetime.now().strftime("%Y-%m-%d")

        # Handle salary (check for NaN values)
        salary = ""
        min_sal = job.get("min_amount")
        max_sal = job.get("max_amount")

        def is_valid_number(val):
            """Check if value is a valid number (not None, not NaN)."""
            if val is None:
                return False
            try:
                return not math.isnan(float(val))
            except (ValueError, TypeError):
                return False

        try:
            if is_valid_number(min_sal) and is_valid_number(max_sal):
                salary = f"${int(min_sal):,} - ${int(max_sal):,}"
            elif is_valid_number(min_sal):
                salary = f"${int(min_sal):,}+"
            elif is_valid_number(max_sal):
                salary = f"Up to ${int(max_sal):,}"
        except (ValueError, TypeError):
            salary = ""

        cleansheet_job = {
            "id": str(uuid.uuid4()),
            "company": str(job.get("company", "")),
            "title": str(job.get("title", "")),
            "location": str(job.get("location", "")),
            "url": str(job.get("job_url", "")),
            "description": str(job.get("description", "")),
            "salary": salary,
            "datePosted": date_posted,
            "source": str(job.get("site", "")),
            "status": "Saved",
            "tags": []
        }
        cleansheet_jobs.append(cleansheet_job)

    # Write file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(cleansheet_jobs, f, indent=2, ensure_ascii=False)

        console.print(f"\n[green]Exported {len(cleansheet_jobs)} jobs to {filename}[/]")
        console.print("[dim]Import this file into Cleansheet Job Opportunities[/]")

    except IOError as e:
        console.print(f"[red]Export failed: {e}[/]")


def main():
    """Main application loop."""
    display_banner()

    config = load_config()
    jobs = []
    last_search_term = ""

    while True:
        choice = display_main_menu()

        if choice == "1":
            jobs, last_search_term = search_jobs(config)
        elif choice == "2":
            config = display_settings_menu(config)
        elif choice == "3":
            export_jobs(jobs, last_search_term)
        elif choice == "4":
            console.print("\n[bold blue]Goodbye![/]\n")
            break


if __name__ == "__main__":
    main()
