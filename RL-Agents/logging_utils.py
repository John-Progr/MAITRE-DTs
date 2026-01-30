import csv
import os
from datetime import datetime

def save_to_csv(rows, filename="experiment.csv"):
    # Put Iteration first
    headers = ["Iteration", "Channel", "Reward", "Timestamp"]
    
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        if not file_exists:
            writer.writeheader()

        for row in rows:
            # Convert UNIX timestamp to readable date if needed
            ts = row.get("Timestamp")
            if isinstance(ts, (int, float)):  # UNIX seconds
                row["Timestamp"] = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            # Otherwise if it's a string, we leave it as-is

            writer.writerow(row)
