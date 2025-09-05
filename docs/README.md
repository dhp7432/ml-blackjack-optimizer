# Blackjack Card Counter

A Python implementation of a Blackjack card counting system using the Hi-Lo method with 8 decks.

## Features

- **Hi-Lo Counting System**: Implements the popular Hi-Lo card counting method
- **8-Deck Shoe**: Tracks cards across 8 decks (416 total cards)
- **Running Count**: Tracks the raw count as cards are dealt
- **True Count**: Converts running count to true count based on remaining decks
- **Betting Recommendations**: Provides betting advice based on current count
- **Interactive Mode**: Command-line interface for real-time card counting
- **Programmatic API**: Can be imported and used in other Python scripts

## How It Works

### Hi-Lo Counting Values
- **Low cards (2-6)**: +1 point
- **Neutral cards (7-9)**: 0 points  
- **High cards (10, J, Q, K, A)**: -1 point

### Count Types
- **Running Count**: Raw sum of all card values dealt
- **True Count**: Running count divided by remaining decks (more accurate for betting decisions)

## Usage

### Interactive Mode
Run the main script for an interactive card counting session:

```bash
python blackjack_card_counter.py
```

**Commands:**
- Enter card values: `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `J`, `Q`, `K`, `A`
- `status` - Show current count and status
- `reset` - Start fresh with new 6-deck shoe
- `quit` - Exit the program

### Programmatic Usage
Import and use the `BlackjackCardCounter` class in your own scripts:

```python
from blackjack_card_counter import BlackjackCardCounter

# Initialize counter
counter = BlackjackCardCounter(8)

# Deal cards
running_count, true_count, remaining_decks = counter.deal_card('A')
running_count, true_count, remaining_decks = counter.deal_card('5')

# Get current status
status = counter.get_current_status()
print(f"Running count: {status['running_count']}")
print(f"True count: {status['true_count']}")

# Get betting advice
advice = counter.get_betting_recommendation()
print(advice)
```

### Example Script
Run the example script to see the card counter in action:

```bash
python example_usage.py
```

## Betting Recommendations

- **True Count ≥ 3**: High count - Consider increasing bet size
- **True Count ≥ 1**: Positive count - Slight advantage, normal bet
- **True Count ≥ -1**: Neutral count - House advantage, minimum bet
- **True Count < -1**: Negative count - House advantage, minimum bet or skip

## Files

- `blackjack_card_counter.py` - Main card counting class and interactive program
- `example_usage.py` - Example usage and demonstrations
- `README.md` - This documentation file

## Requirements

- Python 3.6 or higher
- No external dependencies required

## Important Notes

- This is for educational purposes only
- Card counting may not be legal in all jurisdictions
- Casinos actively work to prevent card counting
- The system tracks remaining cards and prevents dealing more cards than available
- Use responsibly and in accordance with local laws and regulations

## How to Count Cards

1. Start with a fresh 6-deck shoe
2. As each card is dealt, mentally add its Hi-Lo value
3. Keep track of the running count
4. Divide by remaining decks to get the true count
5. Use the true count to make betting and playing decisions
6. Reset when the shoe is shuffled

## Example Session

```
=== Blackjack Card Counter (6 Decks) ===

Initial status:
Running count: 0
True count: 0.0
Remaining decks: 8.0
Total cards: 416

Enter cards as they are dealt (2-10, J, Q, K, A)
Type 'status' to see current count, 'reset' to start new shoe, 'quit' to exit

Enter card (or command): A
Card A dealt:
Running count: -1
True count: -0.13
Remaining decks: 7.98
Betting recommendation: Negative count - House advantage, minimum bet or skip

Enter card (or command): 5
Card 5 dealt:
Running count: 0
True count: 0.0
Remaining decks: 7.96
Betting recommendation: Neutral count - House advantage, minimum bet
```
