import tkinter as tk
import random

# -------------------------------
# Helper Functions for Poker Logic
# -------------------------------

# List of card ranks (from highest to lowest)
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def generate_random_hand():
    """
    Generate a random Texas Hold'em starting hand.
    For non-pairs, ensure that the higher-ranked card appears first.
    e.g., instead of "3Qs" it returns "Q3s".
    """
    card1 = random.choice(RANKS)
    card2 = random.choice(RANKS)
    if card1 == card2:
        return card1 + card2  # e.g., "AA"
    else:
        # Ensure the higher card comes first (lower index in RANKS means higher rank)
        if RANKS.index(card1) > RANKS.index(card2):
            card1, card2 = card2, card1
        suited = random.choice([True, False])
        return card1 + card2 + ("s" if suited else "o")

def evaluate_hand_strength(hand):
    """
    A very simplified heuristic to assign a strength (0 to 1) to a hand.
    Pairs: strength proportional to the rank (AA = 1.0, 22 is low).
    Non-pairs: use the average of the two card values (normalized) plus a small bonus if suited.
    """
    rank_values = {"A":14, "K":13, "Q":12, "J":11, "T":10,
                   "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    
    if len(hand) == 2:  # Pair (e.g., "AA")
        value = rank_values[hand[0]]
        return value / 14.0
    elif len(hand) == 3:
        card1, card2, style = hand[0], hand[1], hand[2]
        avg = (rank_values[card1] + rank_values[card2]) / 28.0  # normalize average
        bonus = 0.05 if style == "s" else 0.0
        return min(avg + bonus, 1.0)
    else:
        return 0.0

def decide_correct_action(hand, scenario):
    """
    Decide the optimal action based on the hand's strength and scenario.
    
    Scenarios:
      - "SB": (Small Blind) Options: Fold, Call, Raise.
          * If strength >= 0.70 -> raise
          * If strength is between 0.40 and 0.70 -> call
          * Otherwise -> fold
      - "BB_RAISE": (Big Blind facing an opponent raise)
          * Same thresholds as SB.
      - "BB_LIMP": (Big Blind facing an opponent limp)
          * Options: Check or Raise.
          * If strength >= 0.60 -> raise; else check.
    """
    strength = evaluate_hand_strength(hand)
    if scenario in ["SB", "BB_RAISE"]:
        if strength >= 0.70:
            return "raise"
        elif strength >= 0.40:
            return "call"
        else:
            return "fold"
    elif scenario == "BB_LIMP":
        if strength >= 0.60:
            return "raise"
        else:
            return "check"
    else:
        return "fold"  # fallback

# -------------------------------
# The Tkinter GUI Application
# -------------------------------

class PokerTrainerApp:
    def __init__(self, master):
        self.master = master
        master.title("Poker Trainer")
        
        # Track progress
        self.correct_count = 0
        self.wrong_count = 0
        
        # Labels for scenario info and progress tracking
        self.info_label = tk.Label(master, text="Scenario info will appear here", font=("Helvetica", 14))
        self.info_label.pack(pady=5)
        
        self.position_label = tk.Label(master, text="", font=("Helvetica", 12))
        self.position_label.pack(pady=5)
        
        self.hand_label = tk.Label(master, text="", font=("Helvetica", 16))
        self.hand_label.pack(pady=5)
        
        self.progress_label = tk.Label(master, text="Progress - Correct: 0, Wrong: 0", font=("Helvetica", 12))
        self.progress_label.pack(pady=5)
        
        self.result_label = tk.Label(master, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=5)
        
        # Frame for decision buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)
        
        self.fold_button = tk.Button(self.button_frame, text="Fold", command=lambda: self.make_decision("fold"), width=10)
        self.fold_button.grid(row=0, column=0, padx=5)
        
        self.call_button = tk.Button(self.button_frame, text="Call", command=lambda: self.make_decision("call"), width=10)
        self.call_button.grid(row=0, column=1, padx=5)
        
        self.raise_button = tk.Button(self.button_frame, text="Raise", command=lambda: self.make_decision("raise"), width=10)
        self.raise_button.grid(row=0, column=2, padx=5)
        
        # Button to advance to the next hand
        self.next_button = tk.Button(master, text="Next Hand", command=self.next_hand, width=10)
        self.next_button.pack(pady=10)
        self.next_button.config(state="disabled")
        
        # Initialize scenario variables
        self.player_stack = 20
        self.opponent_stack = 20
        self.hand = ""
        self.scenario_type = ""  # One of "SB", "BB_RAISE", "BB_LIMP"
        self.correct_action = ""
        
        self.generate_scenario()
        
    def generate_scenario(self):
        """
        Generate a new random scenario:
          - Random chip stacks (5 to 50 bb)
          - A random hand for you (with cards sorted in descending order)
          - Randomly assign your position:
              * If Small Blind (SB): you act first (Fold, Call, Raise)
              * If Big Blind (BB): simulate an opponent action (Raise or Limp)
                - If opponent raises, options: Fold, Call, Raise.
                - If opponent limps, options: Check, Raise.
          - Determine the optimal action using our simple heuristic.
        """
        self.player_stack = random.randint(5, 50)
        self.opponent_stack = random.randint(5, 50)
        self.hand = generate_random_hand()
        
        # Randomly choose your position
        position = random.choice(["SB", "BB"])
        if position == "SB":
            self.scenario_type = "SB"
            scenario_text = f"Your Stack: {self.player_stack} bb   |   Opponent's Stack: {self.opponent_stack} bb"
            position_text = "Your Position: Small Blind (act first)"
        else:
            # For BB, simulate opponent action randomly: raise or limp.
            self.scenario_type = random.choice(["BB_RAISE", "BB_LIMP"])
            scenario_text = f"Your Stack: {self.player_stack} bb   |   Opponent's Stack: {self.opponent_stack} bb"
            if self.scenario_type == "BB_RAISE":
                position_text = "Your Position: Big Blind | Opponent Action: RAISE"
            else:
                position_text = "Your Position: Big Blind | Opponent Action: LIMP"
        
        # Determine the optimal action for this scenario
        self.correct_action = decide_correct_action(self.hand, self.scenario_type)
        
        # Update displayed labels
        self.info_label.config(text=scenario_text)
        self.position_label.config(text=position_text)
        self.hand_label.config(text=f"Your Hand: {self.hand}")
        self.result_label.config(text="")
        self.progress_label.config(text=f"Progress - Correct: {self.correct_count}, Wrong: {self.wrong_count}")
        
        # Set up the decision buttons for the current scenario
        self.update_buttons()
        self.next_button.config(state="disabled")
        
    def update_buttons(self):
        """
        Update the decision buttons based on the current scenario.
          - For SB and BB_RAISE: options are Fold, Call, Raise.
          - For BB_LIMP: only Check and Raise are allowed.
            * The 'fold' button is disabled and the 'call' button is re-labeled as 'Check'.
        """
        if self.scenario_type in ["SB", "BB_RAISE"]:
            self.fold_button.config(text="Fold", state="normal")
            self.call_button.config(text="Call", state="normal")
            self.raise_button.config(text="Raise", state="normal")
        elif self.scenario_type == "BB_LIMP":
            self.fold_button.config(text="Fold", state="disabled")
            self.call_button.config(text="Check", state="normal")
            self.raise_button.config(text="Raise", state="normal")
        
    def make_decision(self, decision):
        """
        Called when a decision button is clicked.
        Compares your decision to the correct action, updates progress, and shows feedback.
        In BB_LIMP, if you click the 'Call' button it is treated as 'Check'.
        """
        normalized_decision = decision.lower()
        # In BB_LIMP, our available choices are "check" and "raise"
        if self.scenario_type == "BB_LIMP" and normalized_decision == "call":
            normalized_decision = "check"
        
        # Disable decision buttons after your choice
        self.fold_button.config(state="disabled")
        self.call_button.config(state="disabled")
        self.raise_button.config(state="disabled")
        
        # Check your decision against the optimal play
        if normalized_decision == self.correct_action:
            self.result_label.config(text=f"Correct! Optimal play: {self.correct_action.upper()}.")
            self.correct_count += 1
        else:
            self.result_label.config(text=f"Incorrect. Correct play was: {self.correct_action.upper()}.")
            self.wrong_count += 1
            
        self.progress_label.config(text=f"Progress - Correct: {self.correct_count}, Wrong: {self.wrong_count}")
        self.next_button.config(state="normal")
        
    def next_hand(self):
        """
        Move on to the next scenario.
        """
        self.generate_scenario()

# -------------------------------
# Main: Run the Trainer Application
# -------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTrainerApp(root)
    root.mainloop()
