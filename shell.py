import cmd
import time
from rich import box
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from reporter import print_report, export_to_json

console = Console()

class LogAnalyzerShell(cmd.Cmd):
    prompt = "\033[1;36m(analyzer)\033[0m " 
    intro = "" 
    def __init__(self, analyze_func, current_metrics=None, current_filepath=None, top_n=10):
        super().__init__()
        self.analyze_func = analyze_func 
        self.metrics = current_metrics
        self.filepath = current_filepath
        self.top_n = top_n

    def preloop(self):
        welcome_text = (
            "[bold white]Welcome to Log Analyzer Interactive Shell![/bold white]\n"
            "[dim]Type [bold cyan]'help'[/bold cyan] or [bold cyan]'?'[/bold cyan] to list commands.[/dim]"
        )
        console.print()
        console.print(Panel(welcome_text, title="🚀 [bold cyan]Log Analyzer[/bold cyan]", border_style="cyan", expand=False))
        console.print()

    def do_load(self, arg):
        """Load and analyze a new log file. Usage: load <path/to/file.log>"""
        if not arg:
            console.print("[bold red]❌ Please provide a file path. Example: load logs/access.log[/bold red]")
            return
        
        console.print(f"[bold cyan][*] Loading and analyzing {arg} ...[/bold cyan]")
        start_time = time.perf_counter()
        
        new_metrics = self.analyze_func(arg)
        
        if new_metrics:
            self.metrics = new_metrics
            self.filepath = arg
            exec_time = time.perf_counter() - start_time
            console.print(f"[bold green]✅ Successfully loaded in {exec_time:.3f} seconds.[/bold green]")

    def do_top(self, arg):
        """Set the number of top endpoints and show report. Usage: top <N>"""
        if not self.metrics:
            console.print("[bold red]❌ No log file loaded. Use 'load' first.[/bold red]")
            return
        try:
            self.top_n = int(arg)
            console.print(f"[bold cyan][*] Displaying top {self.top_n} endpoints:[/bold cyan]")
            print_report(self.metrics, execution_time=None, top_n=self.top_n)
        except ValueError:
            console.print("[bold red]❌ Please provide a valid integer. Example: top 20[/bold red]")

    def do_export(self, arg):
        """Export the currently loaded log metrics to JSON. Usage: export <path/to/output.json>"""
        if not self.metrics:
            console.print("[bold red]❌ No log file loaded. Use 'load' first.[/bold red]")
            return
        if not arg:
            console.print("[bold red]❌ Please provide an export path. Example: export output.json[/bold red]")
            return
        
        console.print(f"[bold cyan][*] Exporting data to {arg} ...[/bold cyan]")
        export_to_json(self.metrics, arg, self.top_n)
        console.print(f"[bold green]✅ Export completed successfully.[/bold green]")

    def do_report(self, arg):
        """Print the full report for the currently loaded log. Usage: report"""
        if not self.metrics:
            console.print("[bold red]❌ No log file loaded. Use 'load' first.[/bold red]")
            return
        print_report(self.metrics, execution_time=None, top_n=self.top_n)

    def do_exit(self, arg):
        """Exit the interactive shell."""
        console.print("\n[bold magenta]Goodbye! 👋[/bold magenta]\n")
        return True
        
    def do_quit(self, arg):
        """Exit the interactive shell (alias for exit)."""
        return self.do_exit(arg)
    
    def do_help(self, arg):
        """Show help information for available commands."""
        if not arg:
            table = Table(title="🛠️ [bold cyan]Available Commands[/bold cyan]", box=box.SIMPLE, expand=False)
            table.add_column("Command", style="bold green", justify="left")
            table.add_column("Description", style="dim white")
            table.add_column("Usage Example", style="cyan")

            table.add_row("load", "Load and analyze a new log file", "load logs/access.log")
            table.add_row("report", "Print the full report for the loaded log", "report")
            table.add_row("top", "Set the number of top endpoints to display", "top 20")
            table.add_row("export", "Export the current log metrics to JSON", "export output.json")
            table.add_row("help", "Show this help message or details for a command", "help load")
            table.add_row("exit / quit", "Exit the interactive shell", "exit")

            console.print("\n")
            console.print(table)
            console.print("[dim]💡 Type [bold]help <command>[/bold] for more details on a specific command.[/dim]\n")
        else:
            help_dict = {
                "load": ("load <filepath>", "Reads the specified log file, parses its contents, and generates analysis metrics."),
                "report": ("report", "Displays the beautifully formatted analysis report for the currently loaded log file."),
                "top": ("top <N>", "Changes the number of top requested endpoints displayed in the report to N and re-prints the report."),
                "export": ("export <filepath>", "Saves the current analysis metrics into a structured JSON file for external use."),
                "help": ("help [command]", "Displays the main help menu or specific details about a provided command."),
                "exit": ("exit", "Safely closes the interactive shell."),
                "quit": ("quit", "Safely closes the interactive shell (alias for exit).")
            }

            command = arg.strip().lower()
            if command in help_dict:
                usage, desc = help_dict[command]
                panel = Panel(
                    f"[bold]Usage:[/bold] [cyan]{usage}[/cyan]\n\n{desc}", 
                    title=f"📖 Help: [bold green]{command}[/bold green]", 
                    border_style="green", 
                    expand=False
                )
                console.print("\n")
                console.print(panel)
                console.print("\n")
            else:
                console.print(f"\n[bold red]❌ No help available for '{command}'. Command not found.[/bold red]\n")