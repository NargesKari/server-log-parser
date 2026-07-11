import json

from sklearn import metrics

def export_to_json(metrics, export_path, top_n=10):
    export_data = {
        "total_requests": metrics['total_requests'],
        "unique_ips_count": len(metrics['unique_ips']),
        "malformed_lines": metrics['malformed_lines'],
        "top_endpoints": metrics['endpoints'].most_common(top_n),
        "hourly_traffic": dict(metrics.get('hourly_traffic', {}))
    }
    
    try:
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=4)
        print(f"💾 Report successfully exported to {export_path}")
    except IOError as e:
        print(f"❌ Error exporting to JSON: {e}")


def print_report(metrics, execution_time=None, top_n=10):
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
    
    error_rate = (metrics['errors'] / total) * 100 if total > 0 else 0

    print(f" 🔹 Total Requests:       {total:,}")
    print(f" 🔹 Unique Client IPs:    {unique_ips_count:,}")
    print(f" 🔹 Malformed Lines:      {malformed:,} (Skipped)")
    print(f" 🔹 Error Rate (4xx/5xx): {error_rate:.2f}%\n")
    
    print("-" * 55)
    print(" 🔥 TOP 10 REQUESTED ENDPOINTS")
    print("-" * 55)
    
    top_endpoints = metrics['endpoints'].most_common(top_n)
    
    print(f"    {'Rank':<5} | {'Endpoint':<30} | {'Requests'}")
    print("    " + "-"*47)
    
    for i, (endpoint, count) in enumerate(top_endpoints, 1):
        display_endpoint = endpoint if len(endpoint) <= 28 else endpoint[:25] + "..."
        print(f"    {i:<5} | {display_endpoint:<30} | {count:,}")
        
    print("\n" + "-" * 55)
    print(" 🕒 HOURLY TRAFFIC DISTRIBUTION (Histogram)")
    print("-" * 55)
    
    hourly_data = metrics.get('hourly_traffic', {})
    if hourly_data:
        max_traffic = max(hourly_data.values())
        max_bar_length = 30 
        
        for hour in sorted(hourly_data.keys()):
            count = hourly_data[hour]
            bar_length = int((count / max_traffic) * max_bar_length) if max_traffic > 0 else 0
            
            bar = "▇" * bar_length
            print(f"    {hour}:00 | {bar} {count:,}")
            
    suspicious_ips = metrics.get('suspicious_ips', {})
    brute_force_suspects = {ip: count for ip, count in suspicious_ips.items() if count >= 5}
    
    if brute_force_suspects:
        print("\n" + "-" * 55)
        print(" 🚨 SUSPICIOUS ACTIVITY DETECTED (Brute-Force)")
        print("-" * 55)
        
        for ip, count in sorted(brute_force_suspects.items(), key=lambda item: item[1], reverse=True):
            print(f"    ⚠️  {ip:<15} | {count} failed login attempts (401)")

            
    if execution_time is not None:
        print("-" * 55)
        print(f"⏱️  Execution Time: {execution_time:.3f} seconds")
    print("="*55 + "\n")