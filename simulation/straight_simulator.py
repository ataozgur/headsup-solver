import random
import os

def build_deck(exclude_cards):
    """
    Build a standard 52-card deck (each card is a tuple (rank, suit))
    and remove any cards that are in the exclude_cards list.
    """
    suits = ['h', 'd', 'c', 's']
    ranks = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
    deck = [(r, s) for r in ranks for s in suits]
    # Remove cards that are in exclude_cards
    deck = [card for card in deck if card not in exclude_cards]
    return deck

def has_straight(cards):
    """
    Given a list of cards (tuples of (rank, suit)), return True if the cards
    contain a 5-card straight.
    
    We map ranks to numeric values:
       A: 14 (and also 1 if needed), K: 13, Q: 12, ..., 2: 2.
    """
    rank_values = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
                   "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}
    
    values = set()
    for card in cards:
        r = card[0]
        val = rank_values[r]
        values.add(val)
        # Treat Ace as low as well
        if r == "A":
            values.add(1)
    
    sorted_values = sorted(values)
    # Look for any 5 consecutive numbers
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
      hand (str): A hand string, for example, "T9o", "T8o", "T7o", "T6o", or "QJo".
                  The first two characters are the card ranks.
                  The third character indicates 'o' for offsuit or 's' for suited.
      
      simulations (int): Number of simulations for each run.
    
    Returns:
      A float representing the probability of ending up with a straight 
      (using the best 5 out of 7 cards) in this simulation.
    """
    # For simulation purposes, assign suits as follows:
    # If the hand is suited (last char == 's'), assign both cards the same suit (e.g., hearts).
    # Otherwise, assign different suits (e.g., first card hearts, second card diamonds).
    hole_cards = []
    if len(hand) == 3:
        rank1, rank2, style = hand[0], hand[1], hand[2]
        if style == 's':
            hole_cards = [(rank1, "h"), (rank2, "h")]
        else:
            hole_cards = [(rank1, "h"), (rank2, "d")]
    elif len(hand) == 2:
        # Pocket pair or incomplete info – assign two different suits.
        hole_cards = [(hand[0], "h"), (hand[1], "d")]
    else:
        return 0.0
    
    success = 0
    # Build deck excluding the hole cards
    deck = build_deck(hole_cards)
    
    for _ in range(simulations):
        board = random.sample(deck, 5)
        seven_cards = hole_cards + board
        if has_straight(seven_cards):
            success += 1
    
    return success / simulations

if __name__ == "__main__":
    # Create a "simulation" folder next to this file if it doesn't exist.
    this_dir = os.path.dirname(os.path.abspath(__file__))
    # sim_dir = os.path.join(this_dir, "simulation")
    # os.makedirs(sim_dir, exist_ok=True)
    
    # Define the test hands (each representing different gap configurations)
    test_hands = ["T9o", "T8o", "T7o", "T6o", "QJo"]
    
    num_runs = 25
    simulations_per_run = 10000
    
    for hand in test_hands:
        results = []
        for run in range(num_runs):
            prob = simulate_straight_probability(hand, simulations=simulations_per_run)
            results.append(prob)
        avg_probability = sum(results) / len(results)
        
        # Write the results to a file for this hand.
        output_file = os.path.join(this_dir, f"straight_results_{hand}.txt")
        with open(output_file, "w") as f:
            f.write(f"Straight probability results for {hand} ({num_runs} runs of {simulations_per_run} simulations each):\n\n")
            for i, prob in enumerate(results, 1):
                f.write(f"Run {i}: {prob:.4f}\n")
            f.write("\n")
            f.write(f"Average Probability: {avg_probability:.4f}\n")
        
        # Print to the console as well.
        print(f"Results for {hand}:")
        print(f"Individual probabilities: {results}")
        print(f"Average Straight Probability ({hand}) over {num_runs} runs: {avg_probability:.4f}\n")
