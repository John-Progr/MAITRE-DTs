import csv
import json
from pathlib import Path
from datetime import datetime

class ExperimentLogger:
    def __init__(self, experiment_name):
        self.dir = Path("experiments") / experiment_name
        self.dir.mkdir(parents=True, exist_ok=True)

        self.csv_path = self.dir / "steps.csv"

        with open(self.csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "iteration",
                "arm_index",
                "arm_label",
                "reward",
                "q_values",
                "timestamp"
            ])

    def log_step(self, iteration, arm_index, arm_label, reward, q_values):
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                iteration,
                arm_index,
                arm_label,
                reward,
                json.dumps(q_values.tolist()),  # <-- FIX
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
