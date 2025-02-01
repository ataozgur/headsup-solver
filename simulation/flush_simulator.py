import os
import random

class FlushSimulator:
    def __init__(self, hand, simulations=10000):
        """
        Initializes the simulator.
        
        Parameters:
            hand (str): A two‑card hold’em hand string (e.g., "AKh" means Ace and King of hearts).
            simulations (int): Number of Monte Carlo simulations to run.
        """
        self.hand = hand
        self.simulations = simulations
        # Parse the hand
        self.card1 = hand[0:2] if len(hand) == 3 and hand[1].isdigit() else hand[0] + hand[1]
        self.suit = hand[-1].lower()  # e.g., 'h' for hearts

    def build_deck(self):
        """Builds a deck of 52 cards as tuples (rank, suit) and removes the cards in self.hand."""
        suits = ['h', 'd', 'c', 's']
        ranks = ["A","K","Q","J","T","9","8","7","6","5","4","3","2"]
        deck = [(r, s) for r in ranks for s in suits]
        
        # Remove the two specific suited cards in our hand.
        # E.g., if self.hand is "AKh", we assume the two cards are ("A","h") and ("K","h").
        hand_cards = [(self.hand[0], self.suit), (self.hand[1], self.suit)]
        deck = [card for card in deck if card not in hand_cards]
        return deck

    def simulate_flush_probability(self):
        """
        Simulate the probability of making a flush with a suited 2-card hand.
        (We need at least 3 more of our suit in the 5 community cards.)
        
        Returns:
            float: The estimated flush probability.
        """
        deck = self.build_deck()
        flush_count = 0
        
        for _ in range(self.simulations):
            board = random.sample(deck, 5)
            # Count how many cards on the board match our suit
            suit_count = sum(1 for card in board if card[1] == self.suit)
            if suit_count >= 3:
                flush_count += 1
        
        return flush_count / self.simulations

if __name__ == "__main__":
    # We'll run the simulation multiple times and average the results.
    simulator = FlushSimulator("AKh", simulations=10000)
    
    num_runs = 25
    results = []
    
    for i in range(num_runs):
        probability = simulator.simulate_flush_probability()
        results.append(probability)
    
    avg_probability = sum(results) / num_runs
    
    # Create a "simulation" folder next to this file if it doesn't exist
    this_dir = os.path.dirname(os.path.abspath(__file__))
    sim_dir = os.path.join(this_dir)
    os.makedirs(sim_dir, exist_ok=True)
    
    # Write the results to a file in that folder
    output_file = os.path.join(sim_dir, "flush_results.txt")
    with open(output_file, "w") as f:
        f.write("Flush probability results for AKh (25 runs):\n\n")
        for i, prob in enumerate(results, 1):
            f.write(f"Run {i}: {prob:.4f}\n")
        f.write("\n")
        f.write(f"Average Probability: {avg_probability:.4f}\n")
    
    # Print to console as well
    print(f"Individual probabilities: {results}")
    print(f"Average Flush Probability (AKh) over {num_runs} runs: {avg_probability:.4f}")
