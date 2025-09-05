"""
Blackjack Shoe Recorder
======================
Tool to record real card sequences from actual blackjack shoes
and analyze them with the ML model.
"""

import json
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from inference_engine import BlackjackInferenceEngine

@dataclass
class HandRecord:
    """Record of a single hand."""
    hand_number: int
    player_cards: List[str]
    dealer_cards: List[str]
    player_total: int
    dealer_total: int
    is_soft: bool
    is_pair: bool
    action_taken: str
    outcome: str  # 'win', 'lose', 'push'
    bet_amount: float
    profit: float
    cards_before_hand: List[str]  # All cards dealt before this hand
    
@dataclass  
class ShoeRecord:
    """Record of an entire shoe."""
    shoe_id: str
    timestamp: str
    casino: str
    table_info: str
    num_decks: int
    hands: List[HandRecord]
    all_cards_dealt: List[str]  # Complete sequence
    final_penetration: float
    notes: str

class ShoeRecorder:
    """Records and analyzes real blackjack shoes."""
    
    def __init__(self):
        self.current_shoe: Optional[ShoeRecord] = None
        self.cards_dealt: List[str] = []
        self.hand_count = 0
        self.ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        
    def start_new_shoe(self, casino: str = "", table_info: str = "", 
                      num_decks: int = 8, notes: str = "") -> str:
        """Start recording a new shoe."""
        shoe_id = f"shoe_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_shoe = ShoeRecord(
            shoe_id=shoe_id,
            timestamp=datetime.datetime.now().isoformat(),
            casino=casino,
            table_info=table_info,
            num_decks=num_decks,
            hands=[],
            all_cards_dealt=[],
            final_penetration=0.0,
            notes=notes
        )
        
        self.cards_dealt = []
        self.hand_count = 0
        
        print(f"🎯 Started recording new shoe: {shoe_id}")
        print(f"   Casino: {casino}")
        print(f"   Table: {table_info}")
        print(f"   Decks: {num_decks}")
        
        return shoe_id
    
    def record_hand(self, 
                   player_cards: List[str],
                   dealer_cards: List[str], 
                   action_taken: str,
                   outcome: str,
                   bet_amount: float = 1.0,
                   profit: float = 0.0) -> None:
        """Record a single hand."""
        
        if not self.current_shoe:
            raise ValueError("No active shoe. Call start_new_shoe() first.")
        
        # Calculate hand properties
        player_total = self._calculate_total(player_cards)
        dealer_total = self._calculate_total(dealer_cards)
        is_soft = self._is_soft_hand(player_cards)
        is_pair = len(player_cards) == 2 and player_cards[0] == player_cards[1]
        
        # Record cards dealt before this hand
        cards_before_hand = self.cards_dealt.copy()
        
        # Add new cards to sequence
        all_hand_cards = player_cards + dealer_cards
        self.cards_dealt.extend(all_hand_cards)
        
        self.hand_count += 1
        
        hand_record = HandRecord(
            hand_number=self.hand_count,
            player_cards=player_cards.copy(),
            dealer_cards=dealer_cards.copy(),
            player_total=player_total,
            dealer_total=dealer_total,
            is_soft=is_soft,
            is_pair=is_pair,
            action_taken=action_taken,
            outcome=outcome,
            bet_amount=bet_amount,
            profit=profit,
            cards_before_hand=cards_before_hand
        )
        
        self.current_shoe.hands.append(hand_record)
        self.current_shoe.all_cards_dealt = self.cards_dealt.copy()
        
        # Calculate penetration
        total_cards = self.current_shoe.num_decks * 52
        self.current_shoe.final_penetration = len(self.cards_dealt) / total_cards
        
        print(f"📝 Recorded hand #{self.hand_count}: {player_cards} vs {dealer_cards[0]}up")
        print(f"   Action: {action_taken}, Outcome: {outcome}, Profit: ${profit:+.2f}")
        print(f"   Penetration: {self.current_shoe.final_penetration:.1%}")
    
    def finish_shoe(self) -> ShoeRecord:
        """Finish recording current shoe."""
        if not self.current_shoe:
            raise ValueError("No active shoe to finish.")
        
        shoe = self.current_shoe
        print(f"✅ Finished shoe {shoe.shoe_id}")
        print(f"   Total hands: {len(shoe.hands)}")
        print(f"   Final penetration: {shoe.final_penetration:.1%}")
        
        self.current_shoe = None
        return shoe
    
    def save_shoe(self, shoe: ShoeRecord, filename: Optional[str] = None) -> str:
        """Save shoe record to JSON file."""
        if filename is None:
            filename = f"{shoe.shoe_id}.json"
        
        # Convert to dict for JSON serialization
        data = asdict(shoe)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved shoe to {filename}")
        return filename
    
    def load_shoe(self, filename: str) -> ShoeRecord:
        """Load shoe record from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Convert back to dataclasses
        hands = [HandRecord(**hand) for hand in data['hands']]
        data['hands'] = hands
        
        shoe = ShoeRecord(**data)
        print(f"📂 Loaded shoe {shoe.shoe_id} from {filename}")
        
        return shoe
    
    def _calculate_total(self, cards: List[str]) -> int:
        """Calculate hand total."""
        total = 0
        aces = 0
        
        for card in cards:
            if card == 'A':
                aces += 1
                total += 11
            elif card in ['10', 'J', 'Q', 'K']:
                total += 10
            else:
                total += int(card)
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def _is_soft_hand(self, cards: List[str]) -> bool:
        """Check if hand is soft (contains usable ace)."""
        has_ace = 'A' in cards
        if not has_ace:
            return False
        
        # Calculate total treating all aces as 1
        total = 0
        for card in cards:
            if card == 'A':
                total += 1
            elif card in ['10', 'J', 'Q', 'K']:
                total += 10
            else:
                total += int(card)
        
        # Can we use an ace as 11 without busting?
        return total + 10 <= 21

class ShoeAnalyzer:
    """Analyzes recorded shoes with ML predictions."""
    
    def __init__(self, model_path: str = 'blackjack_ev_model'):
        self.engine = BlackjackInferenceEngine(model_path)
    
    def analyze_shoe(self, shoe: ShoeRecord) -> Dict[str, Any]:
        """Analyze entire shoe with ML predictions."""
        
        analysis = {
            'shoe_info': {
                'shoe_id': shoe.shoe_id,
                'hands_played': len(shoe.hands),
                'final_penetration': shoe.final_penetration,
                'total_profit': sum(hand.profit for hand in shoe.hands)
            },
            'hand_analyses': [],
            'summary_stats': {}
        }
        
        correct_predictions = 0
        total_ml_ev = 0.0
        total_actual_profit = 0.0
        
        for hand in shoe.hands:
            hand_analysis = self._analyze_hand(hand, shoe.num_decks)
            analysis['hand_analyses'].append(hand_analysis)
            
            if hand_analysis['prediction_correct']:
                correct_predictions += 1
            
            total_ml_ev += hand_analysis['ml_result'].get('optimal_ev', 0)
            total_actual_profit += hand.profit
        
        # Summary statistics
        analysis['summary_stats'] = {
            'prediction_accuracy': correct_predictions / len(shoe.hands) if shoe.hands else 0,
            'ml_predicted_ev': total_ml_ev / len(shoe.hands) if shoe.hands else 0,
            'actual_ev': total_actual_profit / len(shoe.hands) if shoe.hands else 0,
            'ev_difference': (total_actual_profit - total_ml_ev) / len(shoe.hands) if shoe.hands else 0
        }
        
        return analysis
    
    def _analyze_hand(self, hand: HandRecord, num_decks: int) -> Dict[str, Any]:
        """Analyze single hand with ML predictions."""
        
        # Get remaining card counts at time of hand
        card_counts = {rank: 4 * num_decks for rank in self.engine.ranks}
        
        # Remove cards dealt before this hand
        for card in hand.cards_before_hand:
            if card_counts.get(card, 0) > 0:
                card_counts[card] -= 1
        
        # Remove dealer upcard
        dealer_upcard = hand.dealer_cards[0]
        if card_counts.get(dealer_upcard, 0) > 0:
            card_counts[dealer_upcard] -= 1
        
        # Get ML prediction
        ml_result = self.engine.predict(
            player_total=hand.player_total,
            dealer_upcard=dealer_upcard,
            is_soft=hand.is_soft,
            is_pair=hand.is_pair,
            card_counts=card_counts,
            cards_dealt=hand.cards_before_hand,
            num_decks=num_decks
        )
        
        # Check if ML recommended action matches what was taken
        ml_action = ml_result.get('optimal_action', 'unknown')
        prediction_correct = ml_action == hand.action_taken
        
        return {
            'hand_number': hand.hand_number,
            'player_cards': hand.player_cards,
            'dealer_upcard': dealer_upcard,
            'action_taken': hand.action_taken,
            'ml_recommended': ml_action,
            'prediction_correct': prediction_correct,
            'ml_result': ml_result,
            'actual_outcome': hand.outcome,
            'actual_profit': hand.profit,
            'cards_dealt_before': len(hand.cards_before_hand),
            'penetration_at_hand': len(hand.cards_before_hand) / (num_decks * 52)
        }

def demo_shoe_recording():
    """Demonstrate shoe recording and analysis."""
    print("🎰 Blackjack Shoe Recording Demo")
    print("=================================")
    
    # Create recorder
    recorder = ShoeRecorder()
    
    # Start new shoe
    shoe_id = recorder.start_new_shoe(
        casino="Demo Casino",
        table_info="Table 5, $25 min",
        num_decks=8,
        notes="Demo shoe for testing"
    )
    
    # Record some sample hands
    sample_hands = [
        {
            'player_cards': ['K', '7'], 
            'dealer_cards': ['6', '10'], 
            'action_taken': 'stand',
            'outcome': 'win',
            'profit': 1.0
        },
        {
            'player_cards': ['A', '6'], 
            'dealer_cards': ['9', 'J'], 
            'action_taken': 'hit',  # Got a 2, total 19
            'outcome': 'win',
            'profit': 1.0
        },
        {
            'player_cards': ['10', '6'], 
            'dealer_cards': ['10', '7'], 
            'action_taken': 'hit',  # Got a 9, busted
            'outcome': 'lose',
            'profit': -1.0
        },
        {
            'player_cards': ['8', '8'], 
            'dealer_cards': ['A', 'K'], 
            'action_taken': 'split',
            'outcome': 'lose',
            'profit': -2.0
        }
    ]
    
    print(f"\n📝 Recording {len(sample_hands)} sample hands...")
    
    for i, hand in enumerate(sample_hands, 1):
        recorder.record_hand(**hand)
    
    # Finish shoe
    shoe = recorder.finish_shoe()
    
    # Save shoe
    filename = recorder.save_shoe(shoe)
    
    # Analyze with ML
    print(f"\n🤖 Analyzing shoe with ML model...")
    try:
        analyzer = ShoeAnalyzer()
        analysis = analyzer.analyze_shoe(shoe)
        
        print(f"\n📊 Analysis Results:")
        print(f"   Prediction Accuracy: {analysis['summary_stats']['prediction_accuracy']:.1%}")
        print(f"   ML Predicted EV: {analysis['summary_stats']['ml_predicted_ev']:+.3f}")
        print(f"   Actual EV: {analysis['summary_stats']['actual_ev']:+.3f}")
        
        print(f"\n🔍 Hand-by-Hand Analysis:")
        for hand_analysis in analysis['hand_analyses']:
            print(f"   Hand {hand_analysis['hand_number']}: {hand_analysis['player_cards']} vs {hand_analysis['dealer_upcard']}")
            print(f"      Action: {hand_analysis['action_taken']}, ML Suggested: {hand_analysis['ml_recommended']}")
            print(f"      Correct: {'✅' if hand_analysis['prediction_correct'] else '❌'}")
        
    except FileNotFoundError:
        print("❌ ML model not found. Please train the model first.")
    
    return filename

if __name__ == "__main__":
    demo_shoe_recording()
