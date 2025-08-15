import sys
from pathlib import Path

def main():
    root = Path(".").resolve()
    matches = list(root.rglob("asset_loader.py"))
    print("[SCAN] Found asset_loader.py files:")
    for p in matches:
        print(" -", p)
    print("Total:", len(matches))
    if not matches:
        return
    # Heuristic: show first line of each to distinguish versions
    for p in matches:
        try:
            with p.open("r", encoding="utf-8") as f:
                head = f.readline().strip()
            print(f"[HEAD] {p}: {head}")
        except Exception:
            pass
    print("\nIf multiple versions exist, keep only the one under frostborn-realms/frostborn-realms/assets/loader or adjust PYTHONPATH so it is first.")

if __name__ == "__main__":
    main()
