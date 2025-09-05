"""
Live Shoe Recording Tool
=======================
Interactive command-line tool for recording real blackjack shoes.
"""

import sys
from shoe_recorder import ShoeRecorder, ShoeAnalyzer

class LiveShoeRecorder:
    """Interactive shoe recording interface."""
    
    def __init__(self):
        self.recorder = ShoeRecorder()
        self.ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        
    def run(self):
        """Main interactive loop."""
        print("🎰 Live Blackjack Shoe Recorder")
        print("===============================")
        print("Record real card sequences from casino play!")
        print()
        
        try:
            # Setup new shoe
            self._setup_shoe()
            
            # Record hands
            self._record_hands()
            
            # Finish and analyze
            self._finish_and_analyze()
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Recording stopped by user.")
            if self.recorder.current_shoe:
                self._save_current_shoe()
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _setup_shoe(self):
        """Setup new shoe with user input."""
        print("📋 Shoe Setup")
        print("-" * 15)
        
        casino = input("Casino name (optional): ").strip()
        table_info = input("Table info (e.g., 'Table 3, $25 min'): ").strip()
        
        while True:
            try:
                num_decks = input("Number of decks [8]: ").strip()
                num_decks = int(num_decks) if num_decks else 8
                if 1 <= num_decks <= 10:
                    break
                print("Please enter 1-10 decks.")
            except ValueError:
                print("Please enter a valid number.")
        
        notes = input("Notes (optional): ").strip()
        
        shoe_id = self.recorder.start_new_shoe(casino, table_info, num_decks, notes)
        print(f"\n✅ Started recording shoe: {shoe_id}")
        print()
    
    def _record_hands(self):
        """Interactive hand recording loop."""
        print("🃏 Hand Recording")
        print("-" * 20)
        print("Commands:")
        print("  'h' = record hand")
        print("  'f' = finish shoe") 
        print("  'q' = quit")
        print("  '?' = show this help")
        print()
        
        while True:
            cmd = input("Command [h/f/q/?]: ").strip().lower()
            
            if cmd == 'h' or cmd == '':
                self._record_single_hand()
            elif cmd == 'f':
                break
            elif cmd == 'q':
                raise KeyboardInterrupt()
            elif cmd == '?':
                self._show_help()
            else:
                print("Unknown command. Type '?' for help.")
    
    def _record_single_hand(self):
        """Record a single hand."""
        try:
            print(f"\n📝 Hand #{self.recorder.hand_count + 1}")
            print("-" * 25)
            
            # Get player cards
            player_cards = self._get_cards("Player cards (e.g., 'K 7'): ")
            if not player_cards:
                return
            
            # Get dealer cards  
            dealer_cards = self._get_cards("Dealer cards (e.g., '6 10'): ")
            if not dealer_cards:
                return
            
            # Get action
            action = self._get_action()
            if not action:
                return
            
            # Get outcome
            outcome = self._get_outcome()
            if not outcome:
                return
            
            # Get bet info (optional)
            bet_amount, profit = self._get_bet_info()
            
            # Record the hand
            self.recorder.record_hand(
                player_cards=player_cards,
                dealer_cards=dealer_cards,
                action_taken=action,
                outcome=outcome,
                bet_amount=bet_amount,
                profit=profit
            )
            
            print("✅ Hand recorded!")
            
        except Exception as e:
            print(f"❌ Error recording hand: {e}")
    
    def _get_cards(self, prompt: str) -> list:
        """Get card input from user."""
        while True:
            cards_str = input(prompt).strip().upper()
            if not cards_str:
                return []
            
            cards = cards_str.replace(',', ' ').split()
            
            # Validate cards
            valid_cards = []
            for card in cards:
                if card in self.ranks:
                    valid_cards.append(card)
                else:
                    print(f"Invalid card: {card}. Use: {', '.join(self.ranks)}")
                    break
            else:
                return valid_cards
    
    def _get_action(self) -> str:
        """Get action from user."""
        actions = ['hit', 'stand', 'double', 'split', 'surrender']
        
        while True:
            action = input("Action [hit/stand/double/split/surrender]: ").strip().lower()
            if action in actions:
                return action
            elif action == 'h':
                return 'hit'
            elif action == 's': 
                return 'stand'
            elif action == 'd':
                return 'double'
            elif action == 'p':
                return 'split'
            elif action == 'r':
                return 'surrender'
            else:
                print(f"Invalid action. Use: {', '.join(actions)} (or h/s/d/p/r)")
    
    def _get_outcome(self) -> str:
        """Get outcome from user."""
        outcomes = ['win', 'lose', 'push']
        
        while True:
            outcome = input("Outcome [win/lose/push]: ").strip().lower()
            if outcome in outcomes:
                return outcome
            elif outcome == 'w':
                return 'win'
            elif outcome == 'l':
                return 'lose'
            elif outcome == 'p':
                return 'push'
            else:
                print("Invalid outcome. Use: win/lose/push (or w/l/p)")
    
    def _get_bet_info(self) -> tuple:
        """Get bet amount and profit."""
        try:
            bet_str = input("Bet amount [$1]: ").strip()
            bet_amount = float(bet_str) if bet_str else 1.0
            
            profit_str = input("Profit/Loss (e.g., +25, -25) [$0]: ").strip()
            if profit_str:
                profit = float(profit_str.replace('$', '').replace('+', ''))
            else:
                profit = 0.0
            
            return bet_amount, profit
        except ValueError:
            print("Invalid number format. Using defaults.")
            return 1.0, 0.0
    
    def _show_help(self):
        """Show help information."""
        print("\n📖 Help")
        print("-" * 10)
        print("Card format: Use rank only (2,3,4,5,6,7,8,9,10,J,Q,K,A)")
        print("  Example: 'K 7' or 'A 6' or '10 10'")
        print()
        print("Actions: hit, stand, double, split, surrender")
        print("  Shortcuts: h, s, d, p, r")
        print()
        print("Outcomes: win, lose, push") 
        print("  Shortcuts: w, l, p")
        print()
        print("Bet/Profit: Enter numbers, use + or - for profit")
        print("  Example: Bet $25, won $25 → Bet: 25, Profit: +25")
        print()
    
    def _finish_and_analyze(self):
        """Finish shoe and run analysis."""
        if not self.recorder.current_shoe:
            print("No active shoe to finish.")
            return
        
        print(f"\n🏁 Finishing Shoe")
        print("-" * 20)
        
        shoe = self.recorder.finish_shoe()
        filename = self.recorder.save_shoe(shoe)
        
        # Ask about analysis
        analyze = input("\nRun ML analysis? [y/n]: ").strip().lower()
        if analyze in ['y', 'yes', '']:
            self._run_analysis(shoe)
        
        print(f"\n✅ Shoe saved as: {filename}")
    
    def _save_current_shoe(self):
        """Save current shoe if interrupted."""
        try:
            if self.recorder.current_shoe and self.recorder.current_shoe.hands:
                shoe = self.recorder.finish_shoe()
                filename = self.recorder.save_shoe(shoe)
                print(f"💾 Partial shoe saved as: {filename}")
        except Exception as e:
            print(f"Error saving shoe: {e}")
    
    def _run_analysis(self, shoe):
        """Run ML analysis on shoe."""
        try:
            print(f"\n🤖 Running ML Analysis...")
            print("-" * 25)
            
            analyzer = ShoeAnalyzer()
            analysis = analyzer.analyze_shoe(shoe)
            
            stats = analysis['summary_stats']
            
            print(f"📊 Summary Statistics:")
            print(f"   Hands Played: {analysis['shoe_info']['hands_played']}")
            print(f"   Penetration: {analysis['shoe_info']['final_penetration']:.1%}")
            print(f"   Total Profit: ${analysis['shoe_info']['total_profit']:+.2f}")
            print(f"   ML Accuracy: {stats['prediction_accuracy']:.1%}")
            print(f"   ML Predicted EV: {stats['ml_predicted_ev']:+.4f}")
            print(f"   Actual EV: {stats['actual_ev']:+.4f}")
            
            # Show hands where ML disagreed
            disagreements = [h for h in analysis['hand_analyses'] if not h['prediction_correct']]
            if disagreements:
                print(f"\n🤔 ML Disagreements ({len(disagreements)} hands):")
                for hand in disagreements[:5]:  # Show first 5
                    print(f"   Hand {hand['hand_number']}: {hand['player_cards']} vs {hand['dealer_upcard']}")
                    print(f"      You: {hand['action_taken']}, ML: {hand['ml_recommended']}")
                if len(disagreements) > 5:
                    print(f"   ... and {len(disagreements) - 5} more")
            
        except FileNotFoundError:
            print("❌ ML model not found. Train the model first:")
            print("   python data_generator.py")
            print("   python ml_model.py")
        except Exception as e:
            print(f"❌ Analysis error: {e}")

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Live Blackjack Shoe Recorder")
        print("===========================")
        print("Interactive tool to record real casino shoes and analyze with ML.")
        print()
        print("Usage: python record_live_shoe.py")
        print()
        print("The tool will guide you through:")
        print("1. Setting up shoe details (casino, table, decks)")
        print("2. Recording each hand (cards, actions, outcomes)")
        print("3. ML analysis of your decisions vs optimal play")
        print()
        return
    
    recorder = LiveShoeRecorder()
    recorder.run()

if __name__ == "__main__":
    main()
