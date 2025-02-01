import tkinter as tk
import random

# ====================================================
# Global Thresholds (toy numbers – adjust as needed)
# ====================================================
# For SB (player in Small Blind)
SB_RAISE_THRESHOLD = 0.70   # If hand strength ≥0.70, optimal action is raise.
SB_CALL_THRESHOLD  = 0.40   # If hand strength is between 0.40 and 0.70, optimal is call.
                           # Otherwise, fold.
# For BB scenarios:
BB_ALLIN_THRESHOLD = 0.55   # Against an all‑in SB, call if hand strength ≥0.55; else, fold.
BB_LIMP_THRESHOLD  = 0.60   # Against an SB limp, raise if hand strength ≥0.60; else, check.
BB_RAISE_THRESHOLD = 0.50   # Against an SB raise to 2bb, call if hand strength ≥0.50; else, fold.

# ====================================================
# Helper Functions for Poker Logic
# ====================================================

# Ranks in descending order (highest first)
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

def generate_random_hand():
    """
    Generates a random Texas Hold'em starting hand.
    For non-pairs, ensure that the higher-ranked card appears first.
    e.g., instead of "3Qs" returns "Q3s".
    """
    card1 = random.choice(RANKS)
    card2 = random.choice(RANKS)
    if card1 == card2:
        return card1 + card2  # e.g., "AA"
    else:
        # Swap if necessary so that the higher card comes first.
        if RANKS.index(card1) > RANKS.index(card2):
            card1, card2 = card2, card1
        suited = random.choice([True, False])
        return card1 + card2 + ("s" if suited else "o")

def evaluate_hand_strength(hand):
    """
    A very simplified heuristic that assigns a strength between 0 and 1.
      - For pairs: strength is proportional to rank (AA = 1.0, 22 is very low).
      - For non-pairs: take the average of the two card values (normalized) and add a small bonus if suited.
    """
    rank_values = {"A":14, "K":13, "Q":12, "J":11, "T":10,
                   "9":9, "8":8, "7":7, "6":6, "5":5, "4":4, "3":3, "2":2}
    if len(hand) == 2:  # Pair, e.g., "AA"
        value = rank_values[hand[0]]
        return value / 14.0
    elif len(hand) == 3:
        card1, card2, style = hand[0], hand[1], hand[2]
        avg = (rank_values[card1] + rank_values[card2]) / 28.0
        bonus = 0.05 if style == "s" else 0.0
        return min(avg + bonus, 1.0)
    else:
        return 0.0

def decide_correct_action(hand, scenario, player_stack=None):
    """
    Determines the optimal action based on the hand strength, scenario, and (if applicable) player stack.
    
    Scenarios:
      - "SB": Player is in the Small Blind.
          * If player_stack ≤ 15, always push (raise).
          * Otherwise, if hand strength ≥0.70: raise; if ≥0.40: call; else: fold.
          
      - "BB_SB_ALLIN": (Player is BB, and SB went all‑in)
          * Options: Call or Fold. Call if hand strength ≥BB_ALLIN_THRESHOLD; else, fold.
          
      - "BB_SB_LIMP": (Player is BB, and SB limped)
          * Options: Check or Raise. Raise if hand strength ≥BB_LIMP_THRESHOLD; else, check.
          
      - "BB_SB_RAISE": (Player is BB, and SB raised to 2bb)
          * Options: Call or Fold. Call if hand strength ≥BB_RAISE_THRESHOLD; else, fold.
    """
    strength = evaluate_hand_strength(hand)
    if scenario == "SB":
        if player_stack is not None and player_stack <= 15:
            return "raise"  # When short-stacked as SB, always push all‑in.
        else:
            if strength >= SB_RAISE_THRESHOLD:
                return "raise"
            elif strength >= SB_CALL_THRESHOLD:
                return "call"
            else:
                return "fold"
    elif scenario == "BB_SB_ALLIN":
        return "call" if strength >= BB_ALLIN_THRESHOLD else "fold"
    elif scenario == "BB_SB_LIMP":
        return "raise" if strength >= BB_LIMP_THRESHOLD else "check"
    elif scenario == "BB_SB_RAISE":
        return "call" if strength >= BB_RAISE_THRESHOLD else "fold"
    else:
        return "fold"

def simulate_SB_action_for_BB():
    """
    Simulates the SB’s action (when player is BB) and returns:
      - The scenario type (one of "BB_SB_ALLIN", "BB_SB_LIMP", or "BB_SB_RAISE")
      - The SB’s stack (an integer between 5 and 50).
    
    Rules:
      - If SB’s stack ≤15: SB must go all‑in.
      - If SB’s stack ≥15:
          * With probability 0.2, SB goes all‑in.
          * Otherwise, randomly choose between SB limping and SB raising to 2bb
            (we use equal weight for these two).
    """
    sb_stack = random.randint(5, 50)
    if sb_stack <= 15:
        return "BB_SB_ALLIN", sb_stack
    else:
        r = random.random()
        if r < 0.2:
            return "BB_SB_ALLIN", sb_stack
        elif r < 0.2 + 0.4:
            return "BB_SB_LIMP", sb_stack
        else:
            return "BB_SB_RAISE", sb_stack

def debug_print(hand, strength, scenario, correct_action, player_stack, opponent_stack):
    """
    Prints detailed information about the current hand, thresholds, and decision math.
    """
    print("--------------------------------------------------")
    print(f"Scenario: {scenario}")
    print(f"Player Stack: {player_stack} bb, Opponent Stack: {opponent_stack} bb")
    print(f"Your Hand: {hand}")
    print(f"Evaluated Hand Strength: {strength:.2f}")
    if scenario == "SB":
        if player_stack <= 15:
            print("SB: Short-stacked (≤15bb) – Forced All-In (Raise)")
        else:
            print(f"SB Thresholds: Call if ≥ {SB_CALL_THRESHOLD:.2f}, Raise if ≥ {SB_RAISE_THRESHOLD:.2f}")
    elif scenario == "BB_SB_ALLIN":
        print(f"BB_SB_ALLIN Threshold: {BB_ALLIN_THRESHOLD:.2f}")
    elif scenario == "BB_SB_LIMP":
        print(f"BB_SB_LIMP Threshold: Raise if ≥ {BB_LIMP_THRESHOLD:.2f} (else Check)")
    elif scenario == "BB_SB_RAISE":
        print(f"BB_SB_RAISE Threshold: {BB_RAISE_THRESHOLD:.2f}")
    print(f"Computed Optimal Action: {correct_action.upper()}")
    print("--------------------------------------------------\n")

# ====================================================
# Tkinter GUI Application
# ====================================================

class PokerTrainerApp:
    def __init__(self, master):
        self.master = master
        master.title("Poker Trainer")
        
        # Progress tracking counters.
        self.correct_count = 0
        self.wrong_count = 0
        
        # Labels for scenario, hand, progress, etc.
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
        
        # Decision button frame.
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)
        
        self.fold_button = tk.Button(self.button_frame, text="Fold", command=lambda: self.make_decision("fold"), width=10)
        self.fold_button.grid(row=0, column=0, padx=5)
        
        self.call_button = tk.Button(self.button_frame, text="Call", command=lambda: self.make_decision("call"), width=10)
        self.call_button.grid(row=0, column=1, padx=5)
        
        self.raise_button = tk.Button(self.button_frame, text="Raise", command=lambda: self.make_decision("raise"), width=10)
        self.raise_button.grid(row=0, column=2, padx=5)
        
        # Next hand button.
        self.next_button = tk.Button(master, text="Next Hand", command=self.next_hand, width=10)
        self.next_button.pack(pady=10)
        self.next_button.config(state="disabled")
        
        # Initialize scenario variables.
        self.player_stack = 20
        self.opponent_stack = 20
        self.hand = ""
        self.scenario_type = ""  # One of "SB", "BB_SB_LIMP", "BB_SB_RAISE", "BB_SB_ALLIN"
        self.correct_action = ""
        
        self.generate_scenario()
        
    def generate_scenario(self):
        """
        Generate a new random scenario.
        
        For SB:
          - Player's stack is random between 5 and 50.
          - Opponent’s (BB) stack is random between 5 and 50.
          - Scenario: "SB" (player acts first).
        
        For BB:
          - Player's (BB) stack is random between 5 and 50.
          - Simulate SB’s action:
              * First, generate SB's stack (random 5–50).
              * If SB_stack ≤15: SB must go all‑in → scenario "BB_SB_ALLIN".
              * Else, if SB_stack ≥15:
                   – With probability 0.2: SB goes all‑in → "BB_SB_ALLIN".
                   – With probability 0.4: SB limps → "BB_SB_LIMP".
                   – With probability 0.4: SB raises to 2 bb → "BB_SB_RAISE".
        """
        # Randomly choose your position.
        position = random.choice(["SB", "BB"])
        self.hand = generate_random_hand()
        self.player_stack = random.randint(5, 50)
        
        if position == "SB":
            self.scenario_type = "SB"
            self.opponent_stack = random.randint(5, 50)
            scenario_text = f"Your Stack: {self.player_stack} bb   |   Opponent's Stack: {self.opponent_stack} bb"
            position_text = "Your Position: Small Blind (act first)"
        else:
            # Player is BB – simulate SB’s action.
            self.scenario_type, sb_stack = simulate_SB_action_for_BB()
            self.opponent_stack = sb_stack
            scenario_text = f"Your Stack: {self.player_stack} bb   |   SB's Stack: {self.opponent_stack} bb"
            if self.scenario_type == "BB_SB_ALLIN":
                position_text = "Your Position: Big Blind | SB Action: ALL-IN"
            elif self.scenario_type == "BB_SB_LIMP":
                position_text = "Your Position: Big Blind | SB Action: LIMPS"
            elif self.scenario_type == "BB_SB_RAISE":
                position_text = "Your Position: Big Blind | SB Action: RAISES to 2bb"
            else:
                position_text = "Your Position: Big Blind"
        
        # Compute the optimal action based on scenario.
        if self.scenario_type == "SB":
            self.correct_action = decide_correct_action(self.hand, self.scenario_type, self.player_stack)
        else:
            self.correct_action = decide_correct_action(self.hand, self.scenario_type)
        
        strength = evaluate_hand_strength(self.hand)
        debug_print(self.hand, strength, self.scenario_type, self.correct_action,
                    self.player_stack, self.opponent_stack)
        
        # Update GUI labels.
        self.info_label.config(text=scenario_text)
        self.position_label.config(text=position_text)
        self.hand_label.config(text=f"Your Hand: {self.hand}")
        self.result_label.config(text="")
        self.progress_label.config(text=f"Progress - Correct: {self.correct_count}, Wrong: {self.wrong_count}")
        
        self.update_buttons()
        self.next_button.config(state="disabled")
        
    def update_buttons(self):
        """
        Configure the decision buttons based on the current scenario.
        
        - For SB: All three actions are available: Fold, Call, Raise.
        - For BB_SB_ALLIN and BB_SB_RAISE: Only Fold and Call are available.
        - For BB_SB_LIMP: Only Check and Raise are available (the “call” button is re‑labeled as “Check”).
        """
        if self.scenario_type == "SB":
            self.fold_button.config(text="Fold", state="normal")
            self.call_button.config(text="Call", state="normal")
            self.raise_button.config(text="Raise", state="normal")
        elif self.scenario_type in ["BB_SB_ALLIN", "BB_SB_RAISE"]:
            self.fold_button.config(text="Fold", state="normal")
            self.call_button.config(text="Call", state="normal")
            self.raise_button.config(text="N/A", state="disabled")
        elif self.scenario_type == "BB_SB_LIMP":
            self.fold_button.config(text="N/A", state="disabled")
            self.call_button.config(text="Check", state="normal")
            self.raise_button.config(text="Raise", state="normal")
        
    def make_decision(self, decision):
        """
        Processes the user’s decision. It compares your choice with the computed optimal action,
        updates the progress counters, and prints detailed debug information.
        In BB_SB_LIMP, clicking the “Call” button is interpreted as “Check.”
        """
        normalized_decision = decision.lower()
        # For BB_SB_LIMP, the call button represents check.
        if self.scenario_type == "BB_SB_LIMP" and normalized_decision == "call":
            normalized_decision = "check"
        
        # Disable decision buttons.
        self.fold_button.config(state="disabled")
        self.call_button.config(state="disabled")
        self.raise_button.config(state="disabled")
        
        strength = evaluate_hand_strength(self.hand)
        if normalized_decision == self.correct_action:
            result_text = f"Correct! Optimal play: {self.correct_action.upper()}."
            self.correct_count += 1
        else:
            result_text = f"Incorrect. Correct play was: {self.correct_action.upper()}."
            self.wrong_count += 1
        
        # Print detailed decision math.
        print("User Decision Details:")
        print(f"Your Decision: {normalized_decision.upper()}")
        print(f"Optimal Decision: {self.correct_action.upper()}")
        print(f"Hand Strength: {strength:.2f}")
        if self.scenario_type == "SB":
            if self.player_stack <= 15:
                print("SB: Short-stacked (≤15bb) – Forced All-In (Raise)")
            else:
                print(f"SB Thresholds: Call if ≥ {SB_CALL_THRESHOLD:.2f}, Raise if ≥ {SB_RAISE_THRESHOLD:.2f}")
        elif self.scenario_type == "BB_SB_ALLIN":
            print(f"BB_SB_ALLIN Threshold: {BB_ALLIN_THRESHOLD:.2f}")
        elif self.scenario_type == "BB_SB_LIMP":
            print(f"BB_SB_LIMP Threshold: Raise if ≥ {BB_LIMP_THRESHOLD:.2f} (else Check)")
        elif self.scenario_type == "BB_SB_RAISE":
            print(f"BB_SB_RAISE Threshold: {BB_RAISE_THRESHOLD:.2f}")
        print("")
        
        self.result_label.config(text=result_text)
        self.progress_label.config(text=f"Progress - Correct: {self.correct_count}, Wrong: {self.wrong_count}")
        self.next_button.config(state="normal")
        
    def next_hand(self):
        """Generate the next hand scenario."""
        self.generate_scenario()

# ====================================================
# Main: Run the Trainer Application
# ====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTrainerApp(root)
    root.mainloop()
