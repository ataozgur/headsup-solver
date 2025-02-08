import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define the ranks in canonical descending order.
ranks = list("AKQJT98765432")

# Determine the current directory (where this script is located).
this_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the CSV summary file.
csv_file = os.path.join(this_dir, "equity_simulation_results", "equity_summary.csv")

# Read the CSV file into a DataFrame.
df = pd.read_csv(csv_file)

# Create a dictionary mapping each hand string (e.g. "AKo", "AKs", "AA", etc.) to its average equity.
equity_dict = dict(zip(df['Hand'], df['Average Equity']))

# Create an empty 13x13 NumPy array to hold the equity values.
matrix = np.empty((13, 13), dtype=float)
matrix[:] = np.nan  # Initialize with NaN

# Fill in the matrix according to the following rule:
# - For diagonal cells: use the pocket pair (e.g. "AA").
# - For cells where row index < column index (upper triangle): use the suited version.
# - For cells where row index > column index (lower triangle): use the offsuited version,
#   ensuring that the higher card is always first.
for i, r1 in enumerate(ranks):
    for j, r2 in enumerate(ranks):
        if i == j:
            hand_str = r1 * 2  # e.g., "AA"
        elif i < j:
            # For upper triangle, row index < column index.
            # Because ranks is in descending order, r1 is higher than r2.
            hand_str = r1 + r2 + "s"
        else:
            # For lower triangle, row index > column index.
            # In this case r1 is lower than r2, so put the higher card (r2) first.
            hand_str = r2 + r1 + "o"
        # Look up the average equity; if not found, leave as NaN.
        equity = equity_dict.get(hand_str, np.nan)
        matrix[i, j] = equity

# Create a DataFrame from the matrix for easier plotting.
matrix_df = pd.DataFrame(matrix, index=ranks, columns=ranks)

# Create the heatmap.
plt.figure(figsize=(10, 8))
ax = sns.heatmap(matrix_df, annot=True, fmt=".4f", cmap="viridis", linewidths=0.5,
                 cbar_kws={"label": "Average Equity"})

# Move the x-axis (the "Second Card" label) to the top.
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
plt.xlabel("Second Card")
plt.ylabel("First Card")

# Remove the default title and add a caption below the matrix.
plt.title("")
plt.figtext(0.5, 0.01, "Preflop Hand Equity Matrix", ha="center", fontsize=14)

# Save the heatmap to a PNG file.
output_file = os.path.join(this_dir, "equity_matrix.png")
plt.savefig(output_file, dpi=300)
plt.show()

print("Equity matrix saved to:", output_file)
