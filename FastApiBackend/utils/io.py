import os
import csv
from datetime import datetime
from models.api_model import DataTransferRateResponse  # Adjust import if needed

def save_data_transfer_rate_to_file(
    response: DataTransferRateResponse,
    file_path: str = "data_transfer_log.csv"
):
    if not response.timestamp:
        response.timestamp = datetime.utcnow().isoformat()
    
    record = response.dict()

    # ✅ Ensure directory exists
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(file_path)

    # Open file in append mode
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=record.keys())
        
        # Write header only if file is new/empty
        if not file_exists or os.path.getsize(file_path) == 0:
            writer.writeheader()
        
        # Write the record
        writer.writerow(record)
