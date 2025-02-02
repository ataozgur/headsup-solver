import random
import itertools
import os

# -------------------------------
# Helper Functions for Card and Deck Management
# -------------------------------

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]
SUITS = ["h", "d", "c", "s"]

# Map ranks to numeric values for evaluation.
RANK_VALUES = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10,
               "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}

def build_deck(exclude_cards=None):
    """Build a 52-card deck as a list of (rank, suit) tuples, excluding any cards in exclude_cards."""
    deck = [(r, s) for r in RANKS for s in SUITS]
    if exclude_cards:
        deck = [card for card in deck if card not in exclude_cards]
    return deck

def parse_hand(hand_str):
    """
    Converts a hand string into two card tuples.
    Format assumptions:
      - Pocket pairs: "AA", "44", etc. (we assign different suits, e.g., ("A","h"), ("A","d"))
      - Non-pairs: e.g., "Q7o" or "Q7s".
          * For suited, assign both cards the same suit (here "h").
          * For offsuit, assign different suits (here "h" and "d").
    """
    if len(hand_str) == 2:
        return [(hand_str[0], "h"), (hand_str[1], "d")]
    elif len(hand_str) == 3:
        rank1, rank2, style = hand_str[0], hand_str[1], hand_str[2]
        if style.lower() == "s":
            return [(rank1, "h"), (rank2, "h")]
        else:
            return [(rank1, "h"), (rank2, "d")]
    else:
        raise ValueError("Invalid hand string format.")

# -------------------------------
# Simple 5-Card Hand Evaluator
# -------------------------------

def evaluate_5card_hand(cards):
    """
    Given 5 cards (each a tuple (rank, suit)), returns a tuple (category, tiebreaker)
    where a higher tuple means a stronger hand.
    
    Categories (higher is better):
      9: Straight flush
      8: Four of a kind
      7: Full house
      6: Flush
      5: Straight
      4: Three of a kind
      3: Two pair
      2: One pair
      1: High card
    
    The tiebreaker is a tuple of card values in descending order.
    """
    # Get sorted ranks (numeric) and suits.
    values = sorted([RANK_VALUES[card[0]] for card in cards], reverse=True)
    suits = [card[1] for card in cards]
    
    # Check for flush.
    is_flush = len(set(suits)) == 1
    
    # For straights, account for Ace as low.
    sorted_vals = sorted(set(values))
    is_straight = False
    straight_high = None
    # Check normal straight:
    if len(sorted_vals) >= 5:
        for i in range(len(sorted_vals) - 4):
            if sorted_vals[i+4] - sorted_vals[i] == 4:
                is_straight = True
                straight_high = sorted_vals[i+4]
    # Check Ace-low straight (A, 2, 3, 4, 5)
    if not is_straight and set([14, 2, 3, 4, 5]).issubset(set(values)):
        is_straight = True
        straight_high = 5

    # Count duplicates.
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    counts_items = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    # counts_items is list of (value, count) sorted by count then value.
    
    # Determine hand category.
    if is_straight and is_flush:
        return (9, (straight_high,))  # Straight flush.
    elif counts_items[0][1] == 4:
        # Four of a kind.
        quad = counts_items[0][0]
        kicker = max([v for v in values if v != quad])
        return (8, (quad, kicker))
    elif counts_items[0][1] == 3 and counts_items[1][1] >= 2:
        # Full house.
        triple = counts_items[0][0]
        pair = counts_items[1][0]
        return (7, (triple, pair))
    elif is_flush:
        return (6, tuple(sorted(values, reverse=True)))
    elif is_straight:
        return (5, (straight_high,))
    elif counts_items[0][1] == 3:
        # Three of a kind.
        triple = counts_items[0][0]
        kickers = sorted([v for v in values if v != triple], reverse=True)
        return (4, (triple,) + tuple(kickers))
    elif counts_items[0][1] == 2 and counts_items[1][1] == 2:
        # Two pair.
        pair1 = counts_items[0][0]
        pair2 = counts_items[1][0]
        kicker = max([v for v in values if v != pair1 and v != pair2])
        return (3, (pair1, pair2, kicker))
    elif counts_items[0][1] == 2:
        # One pair.
        pair = counts_items[0][0]
        kickers = sorted([v for v in values if v != pair], reverse=True)
        return (2, (pair,) + tuple(kickers))
    else:
        return (1, tuple(values))

def best_hand_value(seven_cards):
    """
    Given 7 cards, returns the best 5-card hand value (as returned by evaluate_5card_hand).
    """
    best = (0, ())
    for combo in itertools.combinations(seven_cards, 5):
        value = evaluate_5card_hand(combo)
        if value > best:
            best = value
    return best

# -------------------------------
# Equity Simulator
# -------------------------------

class EquitySimulator:
    def __init__(self, hero_hand_str, simulations=10000):
        """
        Initialize with hero's hand (e.g., "Q7o") and number of simulations.
        """
        self.hero_hand_str = hero_hand_str
        self.simulations = simulations
        self.hero_cards = parse_hand(hero_hand_str)
    
    def simulate(self):
        """
        Run simulations to determine the equity of the hero's hand versus a random opponent hand.
        
        Process:
          - Build a deck, removing hero's cards.
          - Randomly choose 2 cards for opponent (ensuring no overlap).
          - Deal 5 board cards.
          - Compute best 5-card hand for hero and opponent.
          - Count win, tie, and loss.
        
        Returns:
          Equity as a float: win fraction + (tie fraction)/2.
        """
        wins = 0
        ties = 0
        losses = 0
        
        for _ in range(self.simulations):
            deck = build_deck(self.hero_cards)
            # Randomly sample 2 opponent cards.
            opp_cards = random.sample(deck, 2)
            # Remove opponent cards from deck.
            deck = build_deck(self.hero_cards + opp_cards)
            # Randomly sample 5 board cards.
            board = random.sample(deck, 5)
            
            hero_seven = self.hero_cards + board
            opp_seven = opp_cards + board
            
            hero_value = best_hand_value(hero_seven)
            opp_value = best_hand_value(opp_seven)
            
            if hero_value > opp_value:
                wins += 1
            elif hero_value == opp_value:
                ties += 1
            else:
                losses += 1
        
        total = wins + ties + losses
        equity = (wins + 0.5 * ties) / total if total else 0
        return equity

if __name__ == "__main__":
    # Create a folder for simulation results if it doesn't exist.
    this_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(this_dir, "equity_simulation_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Example: test a few hero hands.
    test_hands = ["AA", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o",
              "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s"]
    num_runs = 10  # Number of runs per hand.
    sims_per_run = 10000  # Simulations per run.
    
    results_summary = {}
    
    for hand in test_hands:
        run_results = []
        simulator = EquitySimulator(hand, simulations=sims_per_run)
        for run in range(num_runs):
            eq = simulator.simulate()
            run_results.append(eq)
        avg_equity = sum(run_results) / len(run_results)
        results_summary[hand] = {"avg_equity": avg_equity, "run_results": run_results}
        
        # Save the results to a text file.
        output_file = os.path.join(results_dir, f"equity_results_{hand}.txt")
        with open(output_file, "w") as f:
            f.write(f"Equity simulation results for {hand} over {num_runs} runs of {sims_per_run} simulations each:\n\n")
            for i, eq in enumerate(run_results, 1):
                f.write(f"Run {i}: {eq:.4f}\n")
            f.write("\n")
            f.write(f"Average Equity: {avg_equity:.4f}\n")
        
        print(f"Results for {hand}: Average Equity: {avg_equity:.4f}")
    
    # Optionally, here you could build a mapping from hand strings to equity values.
    # You can then use these equity values to inform your pot-odds calculations and further refine your model.
