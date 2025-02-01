import tkinter as tk
import random

# -------------------------------
# Helper Functions for the Poker Logic
# -------------------------------

# List of card ranks (highest to lowest)
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def generate_random_hand():
    """
    Generates a random Texas Hold'em starting hand.
    If the two cards have the same rank, returns a pair (e.g., "AA").
    Otherwise, appends 's' for suited or 'o' for offsuit.
    """
    card1 = random.choice(RANKS)
    card2 = random.choice(RANKS)
    if card1 == card2:
        return card1 + card2  # e.g. "AA"
    else:
        suited = random.choice([True, False])
        return card1 + card2 + ("s" if suited else "o")

def evaluate_hand_strength(hand):
    """
    A very simplified heuristic to assign a "strength" (between 0 and 1) to a given hand.
    The idea is:
      - Pairs: strength proportional to the rank (e.g., AA is best, 22 is worst).
      - Offsuit: average the two rank values (normalized), no bonus.
      - Suited: same as offsuit but add a small bonus.
    
    This is for demonstration only.
    """
    # Map each rank to a numeric value (Ace high)
    rank_values = {"A":14, "K":13, "Q":12, "J":11, "T":10,
                   "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    
    # If hand is a pair, e.g., "AA" or "77"
    if len(hand) == 2:
        value = rank_values[hand[0]]
        strength = value / 14  # Normalize so that AA=1.0, 22 ~ 0.14
        return strength
    elif len(hand) == 3:
        # Hand is of the form "Q7o" or "Q7s"
        card1, card2, style = hand[0], hand[1], hand[2]
        value1 = rank_values[card1]
        value2 = rank_values[card2]
        # Normalize the average value (max average is (14+13)/2 = 13.5)
        avg = (value1 + value2) / (14 + 14)  # Dividing by 28 yields a number roughly between 0 and 1
        bonus = 0.05 if style == "s" else 0.0
        return min(avg + bonus, 1.0)
    else:
        return 0.0

def decide_correct_action(hand, player_stack, opponent_stack):
    """
    Using a very basic heuristic (which you can refine later), decide what
    the "optimal" play is given your hand and the chip stacks.
    
    For this demonstration we use fixed thresholds:
      - If hand strength >= 0.70: raise
      - If hand strength is between 0.40 and 0.70: call
      - If hand strength < 0.40: fold
    
    (In real ICM/push-fold scenarios these thresholds would depend on stack sizes,
    position, tournament dynamics, etc.)
    """
    strength = evaluate_hand_strength(hand)
    if strength >= 0.70:
        return "raise"
    elif strength >= 0.40:
        return "call"
    else:
        return "fold"

# -------------------------------
# The Tkinter GUI Application
# -------------------------------

class PokerTrainerApp:
    def __init__(self, master):
        self.master = master
        master.title("Poker Trainer")
        
        # Labels to display scenario information
        self.info_label = tk.Label(master, text="Scenario info will appear here", font=("Helvetica", 14))
        self.info_label.pack(pady=10)
        
        self.hand_label = tk.Label(master, text="", font=("Helvetica", 16))
        self.hand_label.pack(pady=10)
        
        self.result_label = tk.Label(master, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=10)
        
        # Frame to hold decision buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=20)
        
        self.fold_button = tk.Button(self.button_frame, text="Fold", command=lambda: self.make_decision("fold"), width=10)
        self.fold_button.grid(row=0, column=0, padx=5)
        
        self.call_button = tk.Button(self.button_frame, text="Call", command=lambda: self.make_decision("call"), width=10)
        self.call_button.grid(row=0, column=1, padx=5)
        
        self.raise_button = tk.Button(self.button_frame, text="Raise", command=lambda: self.make_decision("raise"), width=10)
        self.raise_button.grid(row=0, column=2, padx=5)
        
        # Button to generate the next hand
        self.next_button = tk.Button(master, text="Next Hand", command=self.next_hand, width=10)
        self.next_button.pack(pady=10)
        self.next_button.config(state="disabled")  # Disabled until after you make a decision
        
        # Initialize scenario variables
        self.player_stack = 20
        self.opponent_stack = 20
        self.hand = ""
        self.correct_action = ""
        
        # Generate the first scenario
        self.generate_scenario()
        
    def generate_scenario(self):
        """
        Generates a new random scenario.
          - Random chip stacks for both players (between 5 and 50 bb)
          - A random hand for you
          - Computes the correct action (using our simple heuristic)
        """
        self.player_stack = random.randint(5, 50)
        self.opponent_stack = random.randint(5, 50)
        self.hand = generate_random_hand()
        self.correct_action = decide_correct_action(self.hand, self.player_stack, self.opponent_stack)
        
        # Update displayed labels
        scenario_text = f"Your Stack: {self.player_stack} bb   |   Opponent's Stack: {self.opponent_stack} bb"
        self.info_label.config(text=scenario_text)
        self.hand_label.config(text=f"Your Hand: {self.hand}")
        self.result_label.config(text="")
        self.next_button.config(state="disabled")
        
        # Re-enable decision buttons
        self.fold_button.config(state="normal")
        self.call_button.config(state="normal")
        self.raise_button.config(state="normal")
        
    def make_decision(self, decision):
        """
        Called when the user clicks one of the decision buttons.
        Compares the chosen decision with the correct one and displays feedback.
        """
        # Disable buttons to prevent double-clicking
        self.fold_button.config(state="disabled")
        self.call_button.config(state="disabled")
        self.raise_button.config(state="disabled")
        
        # Compare the user's decision with the computed optimal action
        if decision == self.correct_action:
            result_text = f"Correct! The optimal play is {self.correct_action.upper()}."
        else:
            result_text = f"Incorrect. The correct play was {self.correct_action.upper()}."
            
        # Also show the hand's evaluated strength for transparency
        strength = evaluate_hand_strength(self.hand)
        result_text += f" (Hand Strength: {strength:.2f})"
        self.result_label.config(text=result_text)
        
        # Enable the Next Hand button to allow moving on
        self.next_button.config(state="normal")
        
    def next_hand(self):
        """
        Called when the Next Hand button is clicked.
        Generates a new scenario.
        """
        self.generate_scenario()
        
# -------------------------------
# Main: Run the Trainer Application
# -------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTrainerApp(root)
    root.mainloop()
