import argparse
import os
import sys

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
    
if __name__ == "__main__":
    main()