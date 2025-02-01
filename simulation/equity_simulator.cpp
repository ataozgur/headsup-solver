// equity_simulator.cpp
#include <algorithm>
#include <array>
#include <chrono>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <filesystem> // C++17 (or use boost::filesystem)

using namespace std;

// Global constants for ranks and suits.
const string RANKS = "AKQJT98765432";
const string SUITS = "hdcs";

// Map rank characters to values.
const map<char, int> RANK_VALUES = {
    {'A', 14}, {'K', 13}, {'Q', 12}, {'J', 11},
    {'T', 10}, {'9', 9},  {'8', 8},  {'7', 7},
    {'6', 6},  {'5', 5},  {'4', 4},  {'3', 3},
    {'2', 2}
};

struct Card {
    char rank;
    char suit;
};

bool operator==(const Card &a, const Card &b) {
    return a.rank == b.rank && a.suit == b.suit;
}

string cardToString(const Card &c) {
    string s;
    s.push_back(c.rank);
    s.push_back(c.suit);
    return s;
}

// --------------------
// Parsing Hero Hand
// --------------------
/*
  parseHand accepts a hand string.
  Format:
   - For pocket pairs: e.g., "AA" (we assign different suits: "h" and "d")
   - For non-pairs: e.g., "AKo" or "AKs".
     For offsuit ("o") we assign "h" and "d". For suited ("s"), we assign both "h".
*/
vector<Card> parseHand(const string &handStr) {
    vector<Card> hand;
    if (handStr.size() == 2) { // Pocket pair.
        hand.push_back({handStr[0], 'h'});
        hand.push_back({handStr[1], 'd'});
    } else if (handStr.size() == 3) {
        char r1 = handStr[0], r2 = handStr[1], style = handStr[2];
        if (tolower(style) == 's') {
            hand.push_back({r1, 'h'});
            hand.push_back({r2, 'h'});
        } else {
            hand.push_back({r1, 'h'});
            hand.push_back({r2, 'd'});
        }
    }
    return hand;
}

// --------------------
// Build a Deck
// --------------------
vector<Card> buildDeck(const vector<Card> &exclude) {
    vector<Card> deck;
    for (char r : RANKS) {
        for (char s : SUITS) {
            Card c = {r, s};
            // Exclude if present in exclude list.
            if (find(exclude.begin(), exclude.end(), c) == exclude.end())
                deck.push_back(c);
        }
    }
    return deck;
}

// --------------------
// 5-Card Hand Evaluator
// --------------------
/*
  We define a hand value as a vector<int> where the first element is the hand category (higher is better):
    9: Straight flush
    8: Four of a kind
    7: Full house
    6: Flush
    5: Straight
    4: Three of a kind
    3: Two pair
    2: One pair
    1: High card
  Followed by kicker values in descending order.
  We then compare these vectors lexicographically.
*/
vector<int> evaluate5CardHand(const vector<Card> &cards) {
    vector<int> values;
    vector<char> suits;
    for (const Card &c : cards) {
        values.push_back(RANK_VALUES.at(c.rank));
        suits.push_back(c.suit);
    }
    sort(values.begin(), values.end(), greater<int>());
    bool isFlush = (count(suits.begin(), suits.end(), suits[0]) == 5);

    // Check for straight. Create a sorted unique list.
    vector<int> uniqueVals = values;
    sort(uniqueVals.begin(), uniqueVals.end());
    uniqueVals.erase(unique(uniqueVals.begin(), uniqueVals.end()), uniqueVals.end());
    bool isStraight = false;
    int straightHigh = 0;
    if (uniqueVals.size() >= 5) {
        for (size_t i = 0; i <= uniqueVals.size() - 5; i++) {
            if (uniqueVals[i+4] - uniqueVals[i] == 4) {
                isStraight = true;
                straightHigh = uniqueVals[i+4];
            }
        }
    }
    // Ace-low straight check: A,2,3,4,5
    if (!isStraight && 
        find(uniqueVals.begin(), uniqueVals.end(), 14) != uniqueVals.end() &&
        find(uniqueVals.begin(), uniqueVals.end(), 2) != uniqueVals.end() &&
        find(uniqueVals.begin(), uniqueVals.end(), 3) != uniqueVals.end() &&
        find(uniqueVals.begin(), uniqueVals.end(), 4) != uniqueVals.end() &&
        find(uniqueVals.begin(), uniqueVals.end(), 5) != uniqueVals.end())
    {
        isStraight = true;
        straightHigh = 5;
    }
    
    // Count occurrences.
    map<int,int> freq;
    for (int v : values) {
        freq[v]++;
    }
    
    // Create a vector of pairs (count, value) sorted by count then value.
    vector<pair<int,int>> countPairs;
    for (auto &p : freq) {
        countPairs.push_back({p.second, p.first});
    }
    sort(countPairs.begin(), countPairs.end(), [](auto a, auto b) {
        if (a.first == b.first)
            return a.second > b.second;
        return a.first > b.first;
    });
    
    vector<int> handValue;
    if (isStraight && isFlush) {
        handValue.push_back(9);
        handValue.push_back(straightHigh);
    } else if (countPairs[0].first == 4) {
        handValue.push_back(8);
        handValue.push_back(countPairs[0].second);
        // kicker: highest card not in quad.
        for (int v : values) {
            if (v != countPairs[0].second) {
                handValue.push_back(v);
                break;
            }
        }
    } else if (countPairs[0].first == 3 && countPairs.size() > 1 && countPairs[1].first >= 2) {
        handValue.push_back(7);
        handValue.push_back(countPairs[0].second);
        handValue.push_back(countPairs[1].second);
    } else if (isFlush) {
        handValue.push_back(6);
        for (int v : values) handValue.push_back(v);
    } else if (isStraight) {
        handValue.push_back(5);
        handValue.push_back(straightHigh);
    } else if (countPairs[0].first == 3) {
        handValue.push_back(4);
        handValue.push_back(countPairs[0].second);
        // Add kickers.
        for (int v : values) {
            if (v != countPairs[0].second)
                handValue.push_back(v);
        }
    } else if (countPairs[0].first == 2 && countPairs.size() >= 2 && countPairs[1].first == 2) {
        handValue.push_back(3);
        handValue.push_back(countPairs[0].second);
        handValue.push_back(countPairs[1].second);
        for (int v : values) {
            if (v != countPairs[0].second && v != countPairs[1].second) {
                handValue.push_back(v);
                break;
            }
        }
    } else if (countPairs[0].first == 2) {
        handValue.push_back(2);
        handValue.push_back(countPairs[0].second);
        for (int v : values) {
            if (v != countPairs[0].second)
                handValue.push_back(v);
        }
    } else {
        handValue.push_back(1);
        for (int v : values) handValue.push_back(v);
    }
    return handValue;
}

// Compare two hand value vectors lexicographically.
bool isBetterHand(const vector<int> &h1, const vector<int> &h2) {
    return lexicographical_compare(h2.begin(), h2.end(), h1.begin(), h1.end());
}

vector<int> bestHandValue(const vector<Card> &sevenCards) {
    vector<int> bestVal;
    bool first = true;
    // Choose 5 out of 7 cards (there are 21 combinations).
    vector<int> indices = {0, 1, 2, 3, 4, 5, 6};
    vector<int> comb(5);
    // Use 5 nested loops (since 7 choose 5 = 21, we can hardcode loops)
    for (int i = 0; i < 3; i++) {
        for (int j = i+1; j < 4; j++) {
            for (int k = j+1; k < 5; k++) {
                for (int l = k+1; l < 6; l++) {
                    for (int m = l+1; m < 7; m++) {
                        vector<Card> five = {sevenCards[i], sevenCards[j],
                                             sevenCards[k], sevenCards[l], sevenCards[m]};
                        vector<int> val = evaluate5CardHand(five);
                        if (first || isBetterHand(val, bestVal)) {
                            bestVal = val;
                            first = false;
                        }
                    }
                }
            }
        }
    }
    return bestVal;
}

// --------------------
// Equity Simulator Class
// --------------------
class EquitySimulator {
public:
    EquitySimulator(const string &heroHandStr, int simulations)
        : heroHandStr(heroHandStr), simulations(simulations)
    {
        heroHand = parseHand(heroHandStr);
    }

    // Run a simulation run and return the equity as a double.
    double simulate() {
        int wins = 0;
        int ties = 0;
        int losses = 0;
        random_device rd;
        mt19937 gen(rd());
        for (int i = 0; i < simulations; i++) {
            // Build deck excluding hero's cards.
            vector<Card> deck = buildDeck(heroHand);
            // Shuffle deck.
            shuffle(deck.begin(), deck.end(), gen);
            // Pick 2 opponent cards.
            vector<Card> oppHand = { deck[0], deck[1] };
            // Remove these two from deck.
            vector<Card> remaining(deck.begin()+2, deck.end());
            // Draw 5 board cards.
            vector<Card> board(remaining.begin(), remaining.begin() + 5);
            // Evaluate hero's best hand.
            vector<Card> heroSeven = heroHand;
            heroSeven.insert(heroSeven.end(), board.begin(), board.end());
            vector<int> heroVal = bestHandValue(heroSeven);
            // Evaluate opponent's best hand.
            vector<Card> oppSeven = oppHand;
            oppSeven.insert(oppSeven.end(), board.begin(), board.end());
            vector<int> oppVal = bestHandValue(oppSeven);
            
            if (heroVal > oppVal)
                wins++;
            else if (heroVal == oppVal)
                ties++;
            else
                losses++;
        }
        int total = wins + ties + losses;
        double equity = (wins + 0.5 * ties) / double(total);
        return equity;
    }

private:
    string heroHandStr;
    int simulations;
    vector<Card> heroHand;
};

// --------------------
// Main Function
// --------------------
int main() {
    // Define test hands (for example, all A-hands).
    vector<string> testHands = {
        "AA", "AKo", "AQo", "AJo", "ATo", "A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o",
        "AKs", "AQs", "AJs", "ATs", "A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s"
    };
    
    // Number of runs and simulations per run.
    int numRuns = 10;           // 10 runs per hand.
    int simsPerRun = 25000;       // 10,000 simulations per run.
    
    // Create results directory "equity_simulation_results" in the current directory.
    namespace fs = std::filesystem;
    fs::path currentDir = fs::current_path();
    fs::path resultsDir = currentDir / "equity_simulation_results";
    fs::create_directories(resultsDir);
    
    for (const auto &hand : testHands) {
        vector<double> runResults;
        double totalEquity = 0.0;
        for (int i = 0; i < numRuns; i++) {
            EquitySimulator sim(hand, simsPerRun);
            double eq = sim.simulate();
            runResults.push_back(eq);
            totalEquity += eq;
        }
        double avgEquity = totalEquity / numRuns;
        
        // Write results to file.
        fs::path outFile = resultsDir / ("equity_results_" + hand + ".txt");
        ofstream fout(outFile);
        if (!fout) {
            cerr << "Error opening file: " << outFile << "\n";
            continue;
        }
        fout << "Equity simulation results for " << hand << " over " 
             << numRuns << " runs of " << simsPerRun << " simulations each:\n\n";
        for (size_t i = 0; i < runResults.size(); i++) {
            fout << "Run " << (i+1) << ": " << runResults[i] << "\n";
        }
        fout << "\nAverage Equity: " << avgEquity << "\n";
        fout.close();
        
        // Also print to console.
        cout << "Results for " << hand << ": Average Equity: " << avgEquity << "\n";
    }
    
    return 0;
}
