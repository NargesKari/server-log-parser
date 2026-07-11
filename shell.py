import cmd
import time
from reporter import print_report, export_to_json

class LogAnalyzerShell(cmd.Cmd):
    intro = "\n" + "="*55 + "\n 🚀 Welcome to Log Analyzer Interactive Shell!\n Type 'help' or '?' to list commands.\n" + "="*55 + "\n"
    prompt = "(analyzer) "

    def __init__(self, analyze_func, current_metrics=None, current_filepath=None, top_n=10):
        super().__init__()
        self.analyze_func = analyze_func 
        self.metrics = current_metrics
        self.filepath = current_filepath
        self.top_n = top_n

    def do_load(self, arg):
        """Load and analyze a new log file. Usage: load <path/to/file.log>"""
        if not arg:
            print("❌ Please provide a file path. Example: load logs/access.log")
            return
        
        print(f"[*] Loading and analyzing {arg} ...")
        start_time = time.perf_counter()
        
        new_metrics = self.analyze_func(arg)
        
        if new_metrics:
            self.metrics = new_metrics
            self.filepath = arg
            exec_time = time.perf_counter() - start_time
            print(f"✅ Successfully loaded in {exec_time:.3f} seconds.")

    def do_top(self, arg):
        """Set the number of top endpoints and show report. Usage: top <N>"""
        if not self.metrics:
            print("❌ No log file loaded. Use 'load' first.")
            return
        try:
            self.top_n = int(arg)
            print(f"[*] Displaying top {self.top_n} endpoints:")
            print_report(self.metrics, execution_time=None, top_n=self.top_n)
        except ValueError:
            print("❌ Please provide a valid integer. Example: top 20")

    def do_export(self, arg):
        """Export the currently loaded log metrics to JSON. Usage: export <path/to/output.json>"""
        if not self.metrics:
            print("❌ No log file loaded. Use 'load' first.")
            return
        if not arg:
            print("❌ Please provide an export path. Example: export output.json")
            return
        export_to_json(self.metrics, arg, self.top_n)

    def do_report(self, arg):
        """Print the full report for the currently loaded log. Usage: report"""
        if not self.metrics:
            print("❌ No log file loaded. Use 'load' first.")
            return
        print_report(self.metrics, execution_time=None, top_n=self.top_n)

    def do_exit(self, arg):
        """Exit the interactive shell."""
        print("Goodbye! 👋\n")
        return True
        
    def do_quit(self, arg):
        """Exit the interactive shell (alias for exit)."""
        return self.do_exit(arg)