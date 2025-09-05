# 🎰 Recording Real Blackjack Shoes for ML Analysis

Your ML system is designed to analyze real card sequences from actual casino play. This guide shows you how to record shoe data and feed it to your model for analysis.

## 📋 Quick Start

### 1. **Live Recording** (Interactive)
```bash
python record_live_shoe.py
```
This launches an interactive tool that guides you through recording each hand as you play.

### 2. **Batch Analysis** (After Recording)
```bash
python batch_analyzer.py
```
Analyzes all recorded shoes and generates comprehensive reports.

### 3. **Demo** (Test the System)
```bash
python shoe_recorder.py
```
Runs a demo with sample hands to test the recording system.

---

## 🃏 How to Record Live Play

### Step 1: Start Recording
When you sit down at a blackjack table, run:
```bash
python record_live_shoe.py
```

The tool will ask for:
- **Casino name** (e.g., "Bellagio")
- **Table info** (e.g., "Table 5, $25 min")
- **Number of decks** (usually 8)
- **Notes** (any observations)

### Step 2: Record Each Hand
For every hand you play, enter:

**Cards Format**: Use ranks only (2,3,4,5,6,7,8,9,10,J,Q,K,A)
- ✅ Good: `K 7` or `A 6` or `10 10`
- ❌ Bad: `KH 7S` or `King Seven`

**Actions**: hit, stand, double, split, surrender
- Shortcuts: h, s, d, p, r

**Outcomes**: win, lose, push
- Shortcuts: w, l, p

### Step 3: Example Recording Session
```
Command [h/f/q/?]: h

📝 Hand #1
-------------------------
Player cards (e.g., 'K 7'): K 7
Dealer cards (e.g., '6 10'): 6 10
Action [hit/stand/double/split/surrender]: stand
Outcome [win/lose/push]: win
Bet amount [$1]: 25
Profit/Loss (e.g., +25, -25) [$0]: +25

✅ Hand recorded!
```

### Step 4: Finish Shoe
When the shoe is shuffled or you're done playing:
```
Command [h/f/q/?]: f
```

The tool will:
- Save your shoe data to a JSON file
- Optionally run ML analysis
- Show prediction accuracy and disagreements

---

## 📊 Understanding the Analysis

### ML Accuracy
- **Prediction Accuracy**: % of times ML agreed with your decisions
- **Expected Value**: Predicted vs actual profit per hand
- **Action Analysis**: Performance breakdown by action type

### Key Insights
1. **High Accuracy (>80%)**: Your play aligns well with optimal strategy
2. **Low Accuracy (<60%)**: Consider following ML recommendations more closely
3. **EV Difference**: Shows potential profit improvement with ML guidance

### Common Disagreements
The analysis shows hands where ML disagreed with your action:
```
Hand 3: ['10', '6'] vs 7: You=hit, ML=stand
Hand 7: ['A', '6'] vs 6: You=hit, ML=double
```

---

## 🔍 Advanced Analysis

### Batch Analysis of Multiple Shoes
```bash
# Analyze all recorded shoes
python batch_analyzer.py

# Custom pattern
python batch_analyzer.py --pattern "bellagio_*.json"

# Generate report without plots
python batch_analyzer.py --no-plots
```

### Manual Analysis
```python
from shoe_recorder import ShoeAnalyzer

analyzer = ShoeAnalyzer()
shoe = analyzer.load_shoe("shoe_20240904_123456.json")
analysis = analyzer.analyze_shoe(shoe)

print(f"Accuracy: {analysis['summary_stats']['prediction_accuracy']:.1%}")
```

---

## 📁 File Formats

### Shoe Data (JSON)
Each recorded shoe is saved as a JSON file:
```json
{
  "shoe_id": "shoe_20240904_123456",
  "timestamp": "2024-09-04T12:34:56",
  "casino": "Bellagio",
  "table_info": "Table 5, $25 min",
  "num_decks": 8,
  "hands": [
    {
      "hand_number": 1,
      "player_cards": ["K", "7"],
      "dealer_cards": ["6", "10"],
      "action_taken": "stand",
      "outcome": "win",
      "profit": 25.0,
      "cards_before_hand": []
    }
  ],
  "all_cards_dealt": ["K", "7", "6", "10"],
  "final_penetration": 0.077
}
```

---

## 💡 Pro Tips

### 1. **Record Everything**
- Don't skip hands - sequence matters!
- Include all player and dealer cards
- Note side bets if you take them

### 2. **Timing Matters**
- Record hands in real-time if possible
- The exact card order affects EV calculations
- Don't forget dealer hole cards

### 3. **Be Accurate**
- Double-check card entries
- Accurate profit/loss tracking helps validation
- Note any unusual table rules

### 4. **Use ML Insights**
- Pay attention to common disagreements
- Practice hands where ML suggests different actions
- Track improvement over time

---

## 🚨 Important Notes

### Card Order Effects
Your ML model captures subtle effects that basic strategy misses:

**Example: Double Down on 11 vs 6**
- **Traditional**: Always double (based on general probabilities)
- **Your ML**: Considers recent cards
  - If last 8 cards were all high (10,J,Q,K,A): ML might suggest hit
  - If last 8 cards were all low (2,3,4,5,6): ML strongly favors double

### Sequence Features
The model tracks:
- **Last 8 cards dealt** (position-specific)
- **High/low/neutral card ratios** in recent sequence
- **Streak patterns** (consecutive high or low cards)
- **Depletion effects** (temporary scarcity of certain ranks)

### Why This Matters
- **Same count, different decision**: Two situations with identical Hi-Lo counts can have different optimal strategies based on recent card patterns
- **Composition-dependent play**: Your ML goes beyond counting to actual composition analysis
- **Real-time adaptation**: Adjusts strategy based on exact shoe state

---

## 🎯 Example Analysis Output

```
📊 ANALYSIS COMPLETE
==============================
Shoes: 3
Hands: 47
Profit: $+125.00
ML Accuracy: 78.7%

🤔 ML Disagreements (10 hands):
   Hand 12: [10, 6] vs 7: You=hit, ML=stand
   Hand 23: [A, 6] vs 6: You=hit, ML=double
   Hand 31: [8, 8] vs 10: You=stand, ML=split
   ...

📈 Potential Improvement: +$23.50 per shoe with ML guidance
```

This shows that following ML recommendations could have improved profit by $23.50 per shoe - that's the power of composition-dependent strategy!

---

## 🔧 Troubleshooting

### Model Not Found
```
❌ ML model not found. Please train the model first:
   python data_generator.py
   python ml_model.py
```

### Import Errors
Make sure you have the required packages:
```bash
pip install -r requirements.txt
```

### File Issues
- Shoe files are saved in the current directory
- Use absolute paths if moving files
- JSON format is human-readable for manual inspection

---

Ready to start recording? Run `python record_live_shoe.py` and take your blackjack game to the next level! 🚀
