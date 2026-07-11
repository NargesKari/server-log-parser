# 📊 Server Log Analyzer CLI

A highly efficient, modular, and interactive command-line tool designed to parse server access logs, extract critical metrics, and detect security anomalies. Built with a focus on performance, the core parsing logic is zero-dependency, while the presentation layer leverages the `rich` library to deliver a stunning dashboard experience directly in your terminal.

## 🏗️ Architecture & File Structure

The project is strictly modularized into four distinct components to adhere to best software engineering practices:

| File | Description |
| :--- | :--- |
| **`analyzer.py`** | The core engine and main entry point. It handles CLI argument parsing (including `.gz` file support), reads the log lines, and updates the metrics dictionary in memory. |
| **`reporter.py`** | The presentation layer. Utilizes the `rich` library to render grids, tables, and histograms. It also handles the data serialization logic for exporting metrics to JSON. |
| **`shell.py`** | The interactive environment module. Inherits from Python's built-in `cmd.Cmd` to provide a custom REPL (Read-Eval-Print Loop) interface, allowing users to execute consecutive queries without reloading massive log files. |
| **`test_parser.py`** | The QA and testing suite. A custom-built test runner that feeds randomized standard logs and strict edge cases into the parser, validates metric counters, and ensures JSON export integrity (with automatic file cleanup). |

## 🚀 Advanced & Bonus Features Implemented

This tool goes beyond basic log counting by introducing several "extra mile" engineering features:

* **Interactive Shell (State Management):** By passing the `-i` flag, users enter a dedicated REPL environment. This allows for blazing-fast consecutive queries on large datasets without needing to re-parse the log file from disk.


* **Automated Anomaly Detection:** Automatically flags IP addresses that exhibit brute-force behavior (e.g., triggering too many `401 Unauthorized` errors on the `/login` endpoint).


* **Server Error Spike Alerts:** Calculates hourly failure rates and alerts the user if `5xx` server errors exceed a 5.0% threshold in any given hour.


* **Compressed File Support:** Seamlessly reads `.log.gz` archives natively without requiring manual extraction.


* **Beautiful UI/UX:** Transforms standard standard terminal output into a readable, color-coded dashboard using `rich`.



## ⚙️ Installation

The core processing relies solely on Python's standard library. However, the UI requires the `rich` package.

```bash
pip install rich
```

Note: The decision to include a third-party library was strictly limited to the presentation layer (`reporter.py`) to drastically improve user experience and readability. The actual log parsing and mathematical calculations remain entirely zero-dependency.

## 💻 Usage Instructions

### 1. Standard CLI Mode (Fire-and-Forget)

Run the tool directly against a log file. It will process the file, print the report, export the data, and exit.

```bash
# Basic usage
python analyzer.py logs/access.log

# View top 20 endpoints and export results to JSON
python analyzer.py logs/access.log -t 20 -e final_report.json

# Analyze a compressed log file directly
python analyzer.py logs/old_access.log.gz
```

### 2. Interactive Shell Mode

Enter a continuous session to manipulate the report parameters dynamically.

```bash
python analyzer.py -i
```

Once inside the `(analyzer)` prompt, you can use the following commands:

* `load <filepath>`: Load and analyze a new log file.


* `top <N>`: Immediately change the number of displayed top endpoints.


* `export <filepath>`: Save the current state to a JSON file.


* `report`: Re-print the dashboard.


* `help`: View detailed command documentation.



## 🧪 Testing

The project includes a robust, custom test runner (`test_parser.py`) that generates random standard logs, tests severe edge cases (like completely malformed strings and IPv6 parsing), checks anomaly counters, and verifies File I/O integrity.

To run the test suite:

```bash
python test_parser.py
```

**Sample Test Output:**

```text
=======================================================
 🧪 STARTING RANDOMIZED LOG PARSER TESTS
=======================================================

[TEST 1] Parse Random Valid Log (DELETE /api/v1/users)
 -> Expected : {'ip': '133.202.245.198', 'timestamp': '01/Jun/2026:23:14:22 +0000', 'method': 'DELETE', 'endpoint': '/api/v1/users', 'protocol': 'HTTP/1.1', 'status': '400', 'size': '28275'}
 -> Actual   : {'ip': '133.202.245.198', 'timestamp': '01/Jun/2026:23:14:22 +0000', 'method': 'DELETE', 'endpoint': '/api/v1/users', 'protocol': 'HTTP/1.1', 'status': '400', 'size': '28275'}
 -> [LOG] Status : MATCHED ✅

[TEST 2] Parse Random Valid Log (GET /login)
 -> Expected : {'ip': '86.68.57.118', 'timestamp': '01/Jun/2026:15:14:22 +0000', 'method': 'GET', 'endpoint': '/login', 'protocol': 'HTTP/1.1', 'status': '301', 'size': '99957'}
 -> Actual   : {'ip': '86.68.57.118', 'timestamp': '01/Jun/2026:15:14:22 +0000', 'method': 'GET', 'endpoint': '/login', 'protocol': 'HTTP/1.1', 'status': '301', 'size': '99957'}
 -> [LOG] Status : MATCHED ✅

[TEST 3] Parse Random Valid Log (DELETE /cart/checkout)
 -> Expected : {'ip': '142.100.205.153', 'timestamp': '01/Jun/2026:03:14:22 +0000', 'method': 'DELETE', 'endpoint': '/cart/checkout', 'protocol': 'HTTP/1.1', 'status': '301', 'size': '97894'}
 -> Actual   : {'ip': '142.100.205.153', 'timestamp': '01/Jun/2026:03:14:22 +0000', 'method': 'DELETE', 'endpoint': '/cart/checkout', 'protocol': 'HTTP/1.1', 'status': '301', 'size': '97894'}
 -> [LOG] Status : MATCHED ✅

[TEST 4] Edge Case 1 (Completely malformed garbage string)
 -> Expected : None
 -> Actual   : None
 -> [LOG] Status : MATCHED ✅

[TEST 5] Edge Case 2 (Incomplete line missing status/size)
 -> Expected : None
 -> Actual   : None
 -> [LOG] Status : MATCHED ✅

[TEST 6] Edge Case 3 (Valid IPv6 Address format)
 -> Expected : 2001:0db8:85a3:0000:0000:8a2e:0370:7334
 -> Actual   : 2001:0db8:85a3:0000:0000:8a2e:0370:7334
 -> [LOG] Status : MATCHED ✅

[TEST 7] Edge Case 4 (Complex Query Params in Endpoint)
 -> Expected : /api/search?query=python&sort=desc&limit=100&token=vVqhgvsDlZvWdvE
 -> Actual   : /api/search?query=python&sort=desc&limit=100&token=vVqhgvsDlZvWdvE
 -> [LOG] Status : MATCHED ✅

[TEST 8] Edge Case 5 (Missing quotes in request line)
 -> Expected : None
 -> Actual   : None
 -> [LOG] Status : MATCHED ✅

[TEST 9] Metrics Update (Brute-Force Suspicious IPs Counter)
 -> Expected : 7
 -> Actual   : 7
 -> [LOG] Status : MATCHED ✅

[TEST 10] Metrics Update (5xx Error Hourly Counter)
 -> Expected : 4
 -> Actual   : 4
 -> [LOG] Status : MATCHED ✅
💾 Report successfully exported to test_temp_output.json

[TEST 11] JSON Export (File Creation)
 -> Expected : True
 -> Actual   : True
 -> [LOG] Status : MATCHED ✅

[TEST 12] JSON Export (Data Integrity - Total Requests)
 -> Expected : 11
 -> Actual   : 11
 -> [LOG] Status : MATCHED ✅

[TEST 13] JSON Export (Data Integrity - Suspicious IPs)
 -> Expected : 7
 -> Actual   : 7
 -> [LOG] Status : MATCHED ✅

==========================================================
 🏁 FINAL SUMMARY: 13 out of 13 tests passed successfully.
==========================================================

```