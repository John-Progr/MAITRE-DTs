import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt

# --- Load your experiment CSV ---
df = pd.read_csv("experiments/optimal_channel_20260122_101440/steps.csv")
df["q_values"] = df["q_values"].apply(json.loads)

# -------- 1) CUMULATIVE AVERAGE --------
rewards = df["reward"].values
steps = np.arange(1, len(rewards) + 1)
avg = np.cumsum(rewards) / steps

plt.figure(figsize=(10,5))
plt.plot(steps, avg, color="#E69F00", linewidth=2)

# Add first and last iteration numbers above the curve
plt.text(steps[0], avg[0]+0.05*(max(avg)-min(avg)), f"{avg[0]:.2f}", ha='center', fontsize=10)
plt.text(steps[-1], avg[-1]+0.05*(max(avg)-min(avg)), f"{avg[-1]:.2f}", ha='center', fontsize=10)

plt.xlabel("Iteration")
plt.ylabel("Cumulative Average Reward")
plt.title("Cumulative Average Reward Over Time")
plt.grid(True, alpha=0.4)
plt.show()

# -------- 2) AVG REWARD PER DEVICE --------
grouped = df.groupby("arm_label")["reward"].mean()

plt.figure(figsize=(8,5))
bars = plt.bar(grouped.index, grouped.values, color="#56B4E9")
plt.xlabel("Device")
plt.ylabel("Average Reward")
plt.title("Average Reward per Device")
plt.xticks(grouped.index)  # Only show the devices present
plt.grid(axis='y', alpha=0.4)

# Add the numbers on top of each bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.02*max(grouped.values),
             f'{height:.2f}', ha='center', va='bottom', fontsize=10)

plt.show()

# -------- 3) Q-VALUE PER DEVICE (ALL TOGETHER) --------
devices = df["arm_label"].unique()

plt.figure(figsize=(10,6))
for device in devices:
    device_df = df[df["arm_label"] == device]
    steps = device_df["iteration"].values
    q_vals = [row["q_values"][row["arm_index"]] for _, row in device_df.iterrows()]
    plt.plot(steps, q_vals, label=f"Device {device}", linewidth=2)

plt.xlabel("Iteration")
plt.ylabel("Q-Value")
plt.title("Q-Value Learning Curves (All Devices)")
plt.legend()
plt.grid(True, alpha=0.4)
plt.show()

# -------- 4) Q-VALUE PER DEVICE (SEPARATE PLOTS, NUMBERS ONLY) --------
for device in devices:
    device_df = df[df["arm_label"] == device]
    steps = device_df["iteration"].values
    q_vals = [row["q_values"][row["arm_index"]] for _, row in device_df.iterrows()]

    plt.figure(figsize=(8,5))
    plt.plot(steps, q_vals, color="#009E73", linewidth=2)
    
    # Add numbers at first and last points only (no bullets)
    plt.text(steps[0], q_vals[0]+0.02*(max(q_vals)-min(q_vals)), f"{q_vals[0]:.2f}", ha='center', fontsize=10)
    plt.text(steps[-1], q_vals[-1]+0.02*(max(q_vals)-min(q_vals)), f"{q_vals[-1]:.2f}", ha='center', fontsize=10)

    plt.xlabel("Iteration")
    plt.ylabel("Q-Value")
    plt.title(f"Q-Value Learning Curve: Device {device}")
    plt.grid(True, alpha=0.4)
    plt.show()
