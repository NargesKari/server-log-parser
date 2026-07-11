import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

def export_to_json(metrics, export_path, top_n=10):
    export_data = {
        "total_requests": metrics['total_requests'],
        "unique_ips_count": len(metrics['unique_ips']),
        "malformed_lines": metrics['malformed_lines'],
        "top_endpoints": metrics['endpoints'].most_common(top_n),
        "hourly_traffic": dict(metrics.get('hourly_traffic', {})),
        "suspicious_ips": dict(metrics.get('suspicious_ips', {})),
        "hourly_5xx_errors": dict(metrics.get('hourly_5xx_errors', {}))
    }
    
    try:
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=4)
        print(f"💾 Report successfully exported to {export_path}")
    except IOError as e:
        print(f"❌ Error exporting to JSON: {e}")



def print_report(metrics, execution_time=None, top_n=10):
    console = Console()
    total = metrics.get('total_requests', 0)
    
    # 1. Header
    console.print(Panel("[bold cyan]📊 SERVER LOG ANALYSIS REPORT[/bold cyan]", border_style="cyan", expand=False))
    
    if total == 0:
        console.print("[bold yellow]⚠️ No valid requests found in the log.[/bold yellow]\n")
        return

    # 2. Summary Section (No lines, just aligned text)
    unique_ips_count = len(metrics.get('unique_ips', []))
    malformed = metrics.get('malformed_lines', 0)
    error_rate = (metrics.get('errors', 0) / total) * 100 if total > 0 else 0

    summary = Table.grid(padding=(0, 2))
    summary.add_row("🔹 [bold]Total Requests:[/bold]", f"[green]{total:,}[/green]")
    summary.add_row("🔹 [bold]Unique Client IPs:[/bold]", f"[blue]{unique_ips_count:,}[/blue]")
    summary.add_row("🔹 [bold]Malformed Lines:[/bold]", f"[yellow]{malformed:,}[/yellow] (Skipped)")
    
    error_color = "red" if error_rate > 5 else "green"
    summary.add_row("🔹 [bold]Error Rate (4xx/5xx):[/bold]", f"[{error_color}]{error_rate:.2f}%[/{error_color}]")
    
    console.print(summary)
    console.print()

    # 3. Top Endpoints Table
    table = Table(title="🔥 TOP 10 REQUESTED ENDPOINTS", title_style="bold magenta", box=box.SIMPLE)
    table.add_column("Rank", justify="center", style="dim")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Requests", justify="right", style="green")

    top_endpoints = metrics['endpoints'].most_common(top_n)
    for i, (endpoint, count) in enumerate(top_endpoints, 1):
        display_endpoint = endpoint if len(endpoint) <= 28 else endpoint[:25] + "..."
        table.add_row(str(i), display_endpoint, f"{count:,}")
    
    console.print(table)
    console.print()

    # 4. Hourly Traffic Histogram
    console.print("[bold yellow]🕒 HOURLY TRAFFIC DISTRIBUTION[/bold yellow]")
    hourly_data = metrics.get('hourly_traffic', {})
    if hourly_data:
        max_traffic = max(hourly_data.values())
        max_bar_length = 30 
        
        hist_table = Table.grid(padding=(0, 1))
        for hour in sorted(hourly_data.keys()):
            count = hourly_data[hour]
            bar_length = int((count / max_traffic) * max_bar_length) if max_traffic > 0 else 0
            bar = "▇" * bar_length
            hist_table.add_row(f"{int(hour):02d}:00", f"[cyan]{bar}[/cyan]", f" {count:,}")
        
        console.print(hist_table)

# 5. Suspicious Activity
    suspicious_ips = metrics.get('suspicious_ips', {})
    brute_force_suspects = {ip: count for ip, count in suspicious_ips.items() if count >= 5}
    
    if brute_force_suspects:
        console.print("\n[bold red]🚨 SUSPICIOUS ACTIVITY DETECTED (Brute-Force)[/bold red]")
        suspect_table = Table.grid(padding=(0, 2)) 
        for ip, count in sorted(brute_force_suspects.items(), key=lambda item: item[1], reverse=True):
            suspect_table.add_row("  ⚠️", f"[bold red]{ip:<15}[/bold red]", f"{count:,} failed login attempts (401)")
            
        console.print(suspect_table)

    # 6. Error Spikes
    hourly_5xx = metrics.get('hourly_5xx_errors', {})
    spikes = []
    for hour, total_in_hour in hourly_data.items():
        errors_in_hour = hourly_5xx.get(hour, 0)
        if total_in_hour > 0:
            rate = (errors_in_hour / total_in_hour) * 100
            if rate >= 5.0 and errors_in_hour >= 50:
                spikes.append((hour, errors_in_hour, rate))
                
    if spikes:
        console.print("\n[bold red]📈 AUTOMATED ERROR SPIKE DETECTION (5xx)[/bold red]")
        for hour, errors, rate in sorted(spikes):
            console.print(f"  🔥 [white on red] {int(hour):02d}:00 to {int(hour):02d}:59 [/white on red] {errors:,} errors | {rate:.1f}% failure rate")
    
    # 7. Execution Time Footer
    if execution_time is not None:
        console.print(f"\n[dim]⏱️ Execution Time: {execution_time:.3f} seconds[/dim]")