# generate_starting_hand_lists.py

RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def generate_starting_hand_lists():
    """
    Generates a dictionary of starting hand lists.
    
    For each top card r1 (from A down to 2), creates a list:
      - The pocket pair r1r1 (e.g., "AA")
      - For every lower rank r2 (where r2 comes after r1 in RANKS), add:
           r1r2o (offsuit) and r1r2s (suited)
           
    This produces the 169 unique hand strings in canonical order.
    """
    starting_hands = {}
    for i, r1 in enumerate(RANKS):
        hands = []
        # Add pocket pair.
        hands.append(r1 * 2)
        # For every lower rank (i.e. hands where r1 is highest):
        for r2 in RANKS[i+1:]:
            # Offsuit version.
            hands.append(r1 + r2 + "o")
            # Suited version.
            hands.append(r1 + r2 + "s")
        starting_hands[r1] = hands
    return starting_hands

if __name__ == "__main__":
    starting_hand_lists = generate_starting_hand_lists()
    # Print each list on a separate line.
    for top_card in RANKS:
        hands = starting_hand_lists[top_card]
        print(f"Hands with {top_card} as the highest card:")
        print('", "'.join(hands))
        print()
