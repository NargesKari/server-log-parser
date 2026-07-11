import argparse
import os
import sys
import re
from collections import Counter

def print_report(metrics):
    total = metrics['total_requests']
    
    print("\n" + "="*55)
    print(" 📊 SERVER LOG ANALYSIS REPORT")
    print("="*55)
    
    if total == 0:
        print(" ⚠️ No valid requests found in the log.")
        print("="*55 + "\n")
        return

    unique_ips_count = len(metrics['unique_ips'])
    malformed = metrics['malformed_lines']
    
    error_rate = (metrics['errors'] / total) * 100

    print(f" 🔹 Total Requests:       {total:,}")
    print(f" 🔹 Unique Client IPs:    {unique_ips_count:,}")
    print(f" 🔹 Malformed Lines:      {malformed:,} (Skipped)")
    print(f" 🔹 Error Rate (4xx/5xx): {error_rate:.2f}%\n")
    
    print("-" * 55)
    print(" 🔥 TOP 10 REQUESTED ENDPOINTS")
    print("-" * 55)
    
    top_endpoints = metrics['endpoints'].most_common(10)
    
    print(f"    {'Rank':<5} | {'Endpoint':<30} | {'Requests'}")
    print("    " + "-"*47)
    
    for i, (endpoint, count) in enumerate(top_endpoints, 1):
        display_endpoint = endpoint if len(endpoint) <= 28 else endpoint[:25] + "..."
        print(f"    {i:<5} | {display_endpoint:<30} | {count:,}")

    print("-" * 55)
    print(" 🕒 HOURLY TRAFFIC DISTRIBUTION (Histogram)")
    print("-" * 55)
    
    hourly_data = metrics['hourly_traffic']
    if hourly_data:
        max_traffic = max(hourly_data.values())
        max_bar_length = 30
        for hour in sorted(hourly_data.keys()):
            count = hourly_data[hour]
            bar_length = int((count / max_traffic) * max_bar_length) if max_traffic > 0 else 0
            bar = "█" * bar_length
            print(f"    {hour}:00 | {bar} {count:,}")
            
    print("="*55 + "\n")


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
    
    with open(file_path, 'r') as file:
        for line in file:
            parsed_data = parse_line(line)
            
            if parsed_data:
                update_metrics(parsed_data, metrics)
            else:
                metrics['malformed_lines'] += 1
                
    return metrics

def main():
    parser = argparse.ArgumentParser(
        description="A CLI tool to analyze server access logs and generate traffic metrics."
    )
    
    parser.add_argument(
        "log_file",
        nargs="?",
        default=os.path.join("logs", "access.log"),
        help="Path to the access log file (default: logs/access.log)"
    )
    
    args = parser.parse_args()
    file_path = args.log_file
    
    if not os.path.exists(file_path):
        print(f"Error: The log file was not found at '{file_path}'.")
        print("Please provide a valid path or ensure 'logs/access.log' exists.")
        sys.exit(1)
        
    print(f"Successfully found the log file: {file_path}")
    print("Starting analysis...\n")

    final_metrics = analyze_log(file_path)
    
    print_report(final_metrics)
    
if __name__ == "__main__":
    main()