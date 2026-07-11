import random
import string
from collections import Counter
from analyzer import parse_line, update_metrics

class LoggerTestRunner:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0

    def assert_equal(self, test_name, expected, actual):
        self.total_tests += 1
        print(f"\n[TEST {self.total_tests}] {test_name}")
        print(f" -> Expected : {expected}")
        print(f" -> Actual   : {actual}")
        
        if expected == actual:
            print(" -> [LOG] Status : MATCHED \u2705")
            self.passed_tests += 1
        else:
            print(" -> [LOG] Status : FAILED \u274C")

    def print_summary(self):
        print("\n" + "="*55)
        print(f" 🏁 FINAL SUMMARY: {self.passed_tests} out of {self.total_tests} tests passed successfully.")
        print("="*55 + "\n")


def generate_random_ip():
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"

def get_blank_metrics():
    return {
        'total_requests': 0,
        'malformed_lines': 0,
        'errors': 0,
        'unique_ips': set(),
        'endpoints': Counter(),
        'statuses': Counter(),
        'hourly_traffic': Counter(),
        'suspicious_ips': Counter(),
        'hourly_5xx_errors': Counter()
    }

def main():
    runner = LoggerTestRunner()
    
    print("="*55)
    print(" 🧪 STARTING RANDOMIZED LOG PARSER TESTS")
    print("="*55)

    # ---------------------------------------------------------
    # PHASE 1: Random Standard Valid Lines
    # ---------------------------------------------------------
    for _ in range(3):
        ip = generate_random_ip()
        method = random.choice(["GET", "POST", "PUT", "DELETE", "PATCH"])
        endpoint = random.choice(["/api/v1/users", "/login", "/products/1877", "/cart/checkout"])
        status = random.choice(["200", "201", "301", "400", "404", "500"])
        size = str(random.randint(100, 99999))
        hour = f"{random.randint(0, 23):02d}"
        timestamp = f"01/Jun/2026:{hour}:14:22 +0000"
        
        log_line = f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "Mozilla/5.0"'
        
        expected_parsed = {
            'ip': ip,
            'timestamp': timestamp,
            'method': method,
            'endpoint': endpoint,
            'protocol': 'HTTP/1.1',
            'status': status,
            'size': size
        }
        
        actual_parsed = parse_line(log_line)
        runner.assert_equal(f"Parse Random Valid Log ({method} {endpoint})", expected_parsed, actual_parsed)

    # ---------------------------------------------------------
    # PHASE 2: 5 Edge Cases
    # ---------------------------------------------------------
    
    # Edge Case 1: Completely malformed random garbage string
    garbage_string = "".join(random.choices(string.ascii_letters + string.digits, k=60))
    runner.assert_equal("Edge Case 1 (Completely malformed garbage string)", None, parse_line(garbage_string))
    
    # Edge Case 2: Incomplete line (missing HTTP status and response size)
    incomplete_line = f'{generate_random_ip()} - - [01/Jun/2026:12:00:00 +0000] "GET / HTTP/1.1"'
    runner.assert_equal("Edge Case 2 (Incomplete line missing status/size)", None, parse_line(incomplete_line))
    
    # Edge Case 3: IPv6 Address parsing
    ipv6_address = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
    ipv6_line = f'{ipv6_address} - - [01/Jun/2026:15:30:00 +0000] "GET /home HTTP/1.1" 200 1024 "-" "-"'
    actual_ipv6_parsed = parse_line(ipv6_line)
    runner.assert_equal("Edge Case 3 (Valid IPv6 Address format)", ipv6_address, actual_ipv6_parsed['ip'] if actual_ipv6_parsed else None)
    
    # Edge Case 4: Extremely complex endpoint with query strings and special characters
    complex_endpoint = "/api/search?query=python&sort=desc&limit=100&token=" + "".join(random.choices(string.ascii_letters, k=15))
    complex_line = f'{generate_random_ip()} - - [01/Jun/2026:16:45:00 +0000] "GET {complex_endpoint} HTTP/1.1" 200 4096 "-" "-"'
    actual_complex_parsed = parse_line(complex_line)
    runner.assert_equal("Edge Case 4 (Complex Query Params in Endpoint)", complex_endpoint, actual_complex_parsed['endpoint'] if actual_complex_parsed else None)
    
    # Edge Case 5: Missing quotes around the request line (Method, Endpoint, Protocol)
    no_quotes_line = f'{generate_random_ip()} - - [01/Jun/2026:17:00:00 +0000] GET /index HTTP/1.1 200 500 "-" "-"'
    runner.assert_equal("Edge Case 5 (Missing quotes in request line)", None, parse_line(no_quotes_line))

    # ---------------------------------------------------------
    # PHASE 3: Metrics Calculation Logic
    # ---------------------------------------------------------
    metrics = get_blank_metrics()
    
    # Test Brute-Force Threshold Calculation
    brute_ip = generate_random_ip()
    target_hour = f"{random.randint(0, 23):02d}"
    
    for _ in range(7):
        data = {
            'ip': brute_ip,
            'timestamp': f"01/Jun/2026:{target_hour}:12:00 +0000",
            'method': 'POST',
            'endpoint': '/login',
            'protocol': 'HTTP/1.1',
            'status': '401',
            'size': '256'
        }
        update_metrics(data, metrics)
        
    runner.assert_equal(
        "Metrics Update (Brute-Force Suspicious IPs Counter)", 
        7, 
        metrics['suspicious_ips'][brute_ip]
    )
    
    # Test 5xx Server Error Hourly Spike Calculation
    spike_hour = "22"
    for _ in range(4):
        data = {
            'ip': generate_random_ip(),
            'timestamp': f"01/Jun/2026:{spike_hour}:50:00 +0000",
            'method': 'GET',
            'endpoint': '/unstable-api',
            'protocol': 'HTTP/1.1',
            'status': '503',
            'size': '1024'
        }
        update_metrics(data, metrics)
        
    runner.assert_equal(
        "Metrics Update (5xx Error Hourly Counter)", 
        4, 
        metrics['hourly_5xx_errors'][spike_hour]
    )

    # Finally, print the tally
    runner.print_summary()

if __name__ == "__main__":
    main()