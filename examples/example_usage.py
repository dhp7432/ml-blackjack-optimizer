from blackjack_card_counter import BlackjackCardCounter

def example_game():
    """Example of using the card counter in a simulated game."""
    print("=== Example Blackjack Card Counting Game ===\n")
    
    # Initialize counter with 8 decks
    counter = BlackjackCardCounter(8)
    
    # Simulate dealing some cards
    cards_to_deal = ['A', 'K', '5', '2', '10', '7', '3', '8', '9', '4']
    
    print("Dealing cards and tracking count:\n")
    
    for i, card in enumerate(cards_to_deal, 1):
        try:
            running_count, true_count, remaining_decks = counter.deal_card(card)
            print(f"Card {i}: {card}")
            print(f"  Running count: {running_count}")
            print(f"  True count: {true_count}")
            print(f"  Remaining decks: {remaining_decks}")
            print(f"  Betting advice: {counter.get_betting_recommendation()}")
            print()
        except ValueError as e:
            print(f"Error dealing {card}: {e}")
    
    # Show final status
    print("=== Final Status ===")
    status = counter.get_current_status()
    print(f"Running count: {status['running_count']}")
    print(f"True count: {status['true_count']}")
    print(f"Remaining cards: {status['remaining_cards']}")
    print(f"Remaining decks: {status['remaining_decks']}")
    print(f"Betting recommendation: {counter.get_betting_recommendation()}")
    
    # Show remaining card distribution
    print("\nRemaining card distribution:")
    for card, count in status['card_counts'].items():
        if count > 0:
            print(f"  {card}: {count} cards")

def example_high_count_scenario():
    """Example showing how the count changes with many low cards."""
    print("\n=== High Count Scenario (Many Low Cards) ===\n")
    
    counter = BlackjackCardCounter(8)
    
    # Deal many low cards to create a high count
    low_cards = ['2', '3', '4', '5', '6'] * 3  # 15 low cards
    
    print("Dealing many low cards to create a high count:\n")
    
    for i, card in enumerate(low_cards, 1):
        running_count, true_count, remaining_decks = counter.deal_card(card)
        print(f"Card {i}: {card} (Running: {running_count}, True: {true_count})")
    
    print(f"\nFinal count after dealing {len(low_cards)} low cards:")
    status = counter.get_current_status()
    print(f"Running count: {status['running_count']}")
    print(f"True count: {status['true_count']}")
    print(f"Betting recommendation: {counter.get_betting_recommendation()}")

if __name__ == "__main__":
    example_game()
    example_high_count_scenario()
