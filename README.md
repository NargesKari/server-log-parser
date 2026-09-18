# server-log-parser

A CLI tool that parses Apache/Nginx-style access logs (including `.gz` archives) line by line and reports traffic metrics, error rates, and simple brute-force/anomaly detection, without loading the whole file into memory.

## What it does

- Parses standard combined-log-format lines (IP, timestamp, method, endpoint, status, size), tolerating malformed lines instead of crashing on them.
- Flags IPs that hit `/login` with repeated `401` responses (brute-force pattern) and alerts when hourly `5xx` rates exceed 5%.
- Reads `.log.gz` files directly, no manual decompression needed.
- Renders the report as a terminal dashboard via `rich`, and can export the same metrics to JSON.
- Ships an interactive shell (`-i`) so you can load a file once and re-run queries (`top <N>`, `export`, `report`) without re-parsing it.
- Has its own test runner (`test_parser.py`) that feeds randomized and edge-case log lines (malformed strings, IPv6, missing fields) through the parser and checks the metrics come out right.

## Tech stack

Python standard library for parsing (zero dependencies for the actual log processing); `rich` for the terminal UI.

## Getting started

```bash
pip install rich

python analyzer.py logs/access.log                       # basic report
python analyzer.py logs/access.log -t 20 -e report.json   # top 20 endpoints, export to JSON
python analyzer.py logs/old_access.log.gz                 # compressed log, no extraction needed
python analyzer.py -i                                     # interactive shell mode

python test_parser.py   # run the test suite
```
