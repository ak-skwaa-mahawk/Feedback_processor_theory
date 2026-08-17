import os
from typing import List, Optional

LOG_FILE = "meta_logs.txt"

def load_logs(filename: str) -> List[str]:
    if not os.path.exists(filename):
        print(f"[!] Warning: File '{filename}' not found. Returning empty log buffer.")
        return []
    with open(filename, "r", encoding="utf-8", errors="replace") as file:
        return file.readlines()

def recall_by_keyword(log_lines: List[str], keyword: str) -> List[str]:
    query = keyword.lower()
    return [line.strip() for line in log_lines if query in line.lower()]

def recall_by_line_number(log_lines: List[str], start: int = 0, end: Optional[int] = None) -> List[str]:
    start = max(0, start)
    if end is None or end > len(log_lines):
        end = len(log_lines)
    return log_lines[start:end]

def print_menu() -> None:
    print("\n--- Meta Logs Recall System ---")
    print("1. Recall by keyword")
    print("2. Recall by line number range")
    print("3. Reload logs from disk")
    print("4. Exit")

def main() -> None:
    logs = load_logs(LOG_FILE)
    print(f"[+] Loaded {len(logs)} lines from '{LOG_FILE}'.")
    
    while True:
        print_menu()
        choice = input("Enter option (1-4): ").strip()
        
        if choice == "1":
            keyword = input("Enter search keyword: ").strip()
            if not keyword:
                print("[-] Empty search keyword.")
                continue
            results = recall_by_keyword(logs, keyword)
            if results:
                print(f"[+] Found {len(results)} matching entries:")
                for r in results:
                    print(f"  - {r}")
            else:
                print(f"[-] No entries found containing '{keyword}'.")
                
        elif choice == "2":
            try:
                start_in = input(f"Start index [0-{max(0, len(logs)-1)}]: ").strip()
                start = int(start_in) if start_in else 0
                end_in = input(f"End index (exclusive, optional): ").strip()
                end = int(end_in) if end_in else None
                
                selected = recall_by_line_number(logs, start, end)
                print(f"[+] Displaying lines {start} to {end if end is not None else len(logs)}:")
                for idx, line in enumerate(selected, start=start):
                    print(f"  [{idx:04d}] {line.strip()}")
            except ValueError:
                print("[-] Invalid line index. Expected integer.")
                
        elif choice == "3":
            logs = load_logs(LOG_FILE)
            print(f"[+] Reloaded {len(logs)} lines from '{LOG_FILE}'.")
            
        elif choice == "4":
            print("[*] Exiting recall system.")
            break
            
        else:
            print("[-] Invalid selection. Enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
