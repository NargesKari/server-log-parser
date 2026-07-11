import argparse
import os
import sys
import re
import gzip
import time
from collections import Counter
from reporter import print_report, export_to_json
from shell import LogAnalyzerShell

LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] '
    r'"(?P<method>\S+) (?P<endpoint>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+)'
)

def parse_line(line):
    match = LOG_PATTERN.search(line)
    if match:
        return match.groupdict()
    return None

def update_metrics(parsed_data, metrics):
    metrics['total_requests'] += 1
    metrics['unique_ips'].add(parsed_data['ip'])
    metrics['endpoints'][parsed_data['endpoint']] += 1
    
    status = int(parsed_data['status'])
    metrics['statuses'][status] += 1
    if status >= 400:
        metrics['errors'] += 1

    hour = parsed_data['timestamp'].split(':')[1] 
    metrics['hourly_traffic'][hour] += 1

def analyze_log(file_path):
    metrics = {
        'total_requests': 0,
        'malformed_lines': 0,
        'errors': 0,
        'unique_ips': set(),
        'endpoints': Counter(),
        'statuses': Counter(),
        'hourly_traffic': Counter()
    }
    
    open_func = gzip.open if file_path.endswith('.gz') else open
    
    try:
        with open_func(file_path, 'rt', encoding='utf-8') as file:
            for line in file:
                parsed_data = parse_line(line)
                
                if parsed_data:
                    update_metrics(parsed_data, metrics)
                else:
                    metrics['malformed_lines'] += 1
    except FileNotFoundError:
        print(f"❌ Error: The log file was not found at '{file_path}'.")
        return None
                    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="A highly efficient CLI tool to analyze server access logs.")
    parser.add_argument("log_file", nargs="?", default="logs/access.log", help="Path to the log file (.log or .log.gz)")
    parser.add_argument("-e", "--export", type=str, help="Export the final report to a JSON file (e.g., output.json)")
    parser.add_argument("-t", "--top", type=int, default=10, help="Number of top endpoints to display (default: 10)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run the tool in an interactive shell mode")
    
    args = parser.parse_args()
    file_path = args.log_file
    
    if args.interactive:
        initial_metrics = None
        if os.path.exists(file_path):
            print(f"[*] Pre-loading initial log file: {file_path}")
            initial_metrics = analyze_log(file_path)
        else:
            print(f"⚠️ Initial file '{file_path}' not found. Starting empty.")
            
        shell = LogAnalyzerShell(
            analyze_func=analyze_log, 
            current_metrics=initial_metrics, 
            current_filepath=file_path, 
            top_n=args.top
        )
        shell.cmdloop()
        
    else:
        if not os.path.exists(file_path):
            print(f"Error: The log file was not found at '{file_path}'.")
            sys.exit(1)
            
        print(f"[*] Successfully found the log file: {file_path}")
        print("[*] Starting analysis...\n")

        start_time = time.perf_counter()
        final_metrics = analyze_log(file_path)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        print_report(final_metrics, execution_time, top_n=args.top)
        
        if args.export:
            export_to_json(final_metrics, args.export, args.top)

if __name__ == "__main__":
    main()