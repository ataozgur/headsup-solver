import os
import glob
import csv

# Set the directory where your simulation results are stored.
# For example, if this script is in the same folder as the "equity_simulation_results" folder:
this_dir = os.path.dirname(os.path.abspath(__file__))
results_dir = os.path.join(this_dir, "equity_simulation_results")

# Find all files matching the pattern "equity_results_*.txt" in the results directory.
file_pattern = os.path.join(results_dir, "equity_results_*.txt")
file_list = glob.glob(file_pattern)

# List to hold tuples of (hand, average_equity)
results = []

# Process each file.
for file_path in file_list:
    filename = os.path.basename(file_path)
    # Extract the hand string.
    # Files are named like "equity_results_AKo.txt" or "equity_results_22.txt".
    # We extract the portion between "equity_results_" and ".txt".
    prefix = "equity_results_"
    suffix = ".txt"
    hand = filename[len(prefix):-len(suffix)]
    
    # Open and read the file.
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    avg_equity = None
    # Look for the line that starts with "Average Equity:"
    for line in lines:
        if line.strip().startswith("Average Equity:"):
            # Expecting a line like: "Average Equity: 0.502026"
            try:
                parts = line.strip().split(":")
                if len(parts) >= 2:
                    avg_equity = parts[1].strip()
                    break
            except Exception as e:
                print(f"Error processing line in {filename}: {e}")
    
    if avg_equity is not None:
        results.append((hand, avg_equity))
    else:
        print(f"Warning: Could not find average equity in file {filename}")

# Optionally sort the results by hand for clarity.
results.sort(key=lambda x: x[0])

# Write the results to a CSV file in the same directory.
csv_file = os.path.join(results_dir, "equity_summary.csv")
with open(csv_file, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header row.
    csvwriter.writerow(["Hand", "Average Equity"])
    # Write each result.
    for hand, equity in results:
        csvwriter.writerow([hand, equity])

print("CSV summary written to:", csv_file)
