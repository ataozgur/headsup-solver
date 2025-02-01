import random
import os
import matplotlib.pyplot as plt

# -------------------------------
# Helper Functions
# -------------------------------

def build_deck(exclude_cards):
    """
    Build a standard 52-card deck (each card is a tuple (rank, suit))
    and remove any cards that are in the exclude_cards list.
    """
    suits = ['h', 'd', 'c', 's']
    ranks = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    deck = [(r, s) for r in ranks for s in suits]
    deck = [card for card in deck if card not in exclude_cards]
    return deck

def has_straight(cards):
    """
    Given a list of cards (each a tuple (rank, suit)), return True if the cards
    contain any 5-card straight.
    
    Ace counts as high (14) and low (1).
    """
    rank_values = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
                   "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
    values = set()
    for card in cards:
        r = card[0]
        val = rank_values[r]
        values.add(val)
        if r == "A":  # Ace as low as well
            values.add(1)
    sorted_values = sorted(values)
    consec = 1
    for i in range(1, len(sorted_values)):
        if sorted_values[i] == sorted_values[i - 1] + 1:
            consec += 1
            if consec >= 5:
                return True
        else:
            consec = 1
    return False

def simulate_straight_probability(hand, simulations=10000):
    """
    Simulate the probability of making a straight in Texas Hold'em given a starting hand.
    
    Parameters:
      hand (str): A hand string, e.g., "T9o", "AKo", "QJo", etc.
                  For non-pairs the format is 3 characters: first two are ranks,
                  third is 'o' for offsuit or 's' for suited.
      simulations (int): Number of simulations per run.
      
    Returns:
      The probability (float) that the 7-card combination (2 hole cards + 5 board)
      contains a straight.
    """
    # Determine hole cards:
    # For simplicity, if offsuit, assign first card hearts, second card diamonds.
    # If suited (last char == 's'), assign both cards the same suit.
    hole_cards = []
    if len(hand) == 3:
        rank1, rank2, style = hand[0], hand[1], hand[2]
        if style == 's':
            hole_cards = [(rank1, "h"), (rank2, "h")]
        else:
            hole_cards = [(rank1, "h"), (rank2, "d")]
    elif len(hand) == 2:
        hole_cards = [(hand[0], "h"), (hand[1], "d")]
    else:
        return 0.0

    success = 0
    deck = build_deck(hole_cards)
    for _ in range(simulations):
        board = random.sample(deck, 5)
        seven_cards = hole_cards + board
        if has_straight(seven_cards):
            success += 1
    return success / simulations

def get_gap(hand):
    """
    Compute the gap between the two hole card ranks.
    Assumes hand is 3 characters (e.g., 'T9o' or 'AKo').
    Returns: integer gap = (numeric value of higher card) - (numeric value of lower card)
    """
    rank_values = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
                   "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
    if len(hand) < 2:
        return None
    card1 = hand[0]
    card2 = hand[1]
    v1 = rank_values[card1]
    v2 = rank_values[card2]
    # Ensure v1 is the higher value.
    if v2 > v1:
        v1, v2 = v2, v1
    return v1 - v2

# -------------------------------
# Main Simulation and Graphing
# -------------------------------

if __name__ == "__main__":
    # Define test hands. You can adjust or add more as needed.
    test_hands = ["AKo", "AQo", "AJo", "KQo", "T9o", "T8o", "T7o", "T6o", "65o", "54o", "43o", "32o"]
    
    num_runs = 25
    simulations_per_run = 10000
    results_data = {}  # To store average probability and gap for each hand
    
    # Create a results folder inside the simulation folder.
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, "simulation_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Loop through each test hand.
    for hand in test_hands:
        run_results = []
        for run in range(num_runs):
            prob = simulate_straight_probability(hand, simulations=simulations_per_run)
            run_results.append(prob)
        avg_probability = sum(run_results) / len(run_results)
        gap = get_gap(hand)
        results_data[hand] = {"avg_probability": avg_probability, "gap": gap, "run_results": run_results}
        
        # Save individual hand results to a text file.
        output_file = os.path.join(results_dir, f"straight_results_{hand}.txt")
        with open(output_file, "w") as f:
            f.write(f"Straight probability results for {hand} ({num_runs} runs of {simulations_per_run} simulations each):\n\n")
            for i, prob in enumerate(run_results, 1):
                f.write(f"Run {i}: {prob:.4f}\n")
            f.write("\n")
            f.write(f"Average Probability: {avg_probability:.4f}\n")
            f.write(f"Gap: {gap}\n")
        
        print(f"Results for {hand}: Average Straight Probability: {avg_probability:.4f}, Gap: {gap}")
    
    # -------------------------------
    # Visualization: Graph the results.
    # -------------------------------
    # Create a scatter plot with:
    #   x-axis: Gap between the hole cards
    #   y-axis: Average straight probability
    # Annotate each point with the hand string.
    gaps = []
    probabilities = []
    labels = []
    for hand, data in results_data.items():
        if data["gap"] is not None:
            gaps.append(data["gap"])
            probabilities.append(data["avg_probability"])
            labels.append(hand)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(gaps, probabilities, color="blue")
    for i, label in enumerate(labels):
        plt.annotate(label, (gaps[i], probabilities[i]), textcoords="offset points", xytext=(5,5))
    plt.xlabel("Gap Between Hole Cards (Numeric Difference)")
    plt.ylabel("Average Straight Probability")
    plt.title("Straight Probability vs. Gap of Hole Cards")
    plt.grid(True)
    
    # Save the graph.
    graph_file = os.path.join(results_dir, "straight_probability_graph.png")
    plt.savefig(graph_file)
    plt.show()
    
    print(f"\nGraph saved to: {graph_file}")
