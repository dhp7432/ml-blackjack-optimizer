"""
Blackjack EV Inference Engine
============================
Production-ready inference system for real-time EV predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import json
from ml_model import BlackjackEVPredictor

class BlackjackInferenceEngine:
    """Production inference engine for blackjack EV predictions."""
    
    def __init__(self, model_path: str = 'blackjack_ev_model'):
        self.predictor = BlackjackEVPredictor()
        self.predictor.load_model(model_path)
        self.ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        
        # Hi-Lo values
        self.counting_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
    
    def card_value(self, rank: str) -> int:
        """Get card value for blackjack."""
        if rank == 'A': 
            return 11
        if rank in {'10', 'J', 'Q', 'K'}: 
            return 10
        return int(rank)
    
    def prepare_features(self, 
                        player_total: int,
                        dealer_upcard: str, 
                        is_soft: bool,
                        is_pair: bool,
                        card_counts: Dict[str, int],
                        cards_dealt: List[str],
                        num_decks: int = 8) -> Dict[str, Any]:
        """Prepare features for inference."""
        
        # Calculate basic counts
        total_cards = num_decks * 52
        remaining_cards = sum(card_counts.values())
        running_count = sum(self.counting_values[card] for card in cards_dealt)
        true_count = running_count / (remaining_cards / 52) if remaining_cards > 0 else 0.0
        
        features = {
            # Hand features
            'player_total': player_total,
            'dealer_upcard_value': self.card_value(dealer_upcard),
            'is_soft': int(is_soft),
            'is_pair': int(is_pair),
        }
        
        # Dealer upcard one-hot
        for rank in self.ranks:
            features[f'dealer_{rank}'] = 1 if dealer_upcard == rank else 0
        
        # Card counts (normalized)
        for rank in self.ranks:
            features[f'count_{rank}'] = card_counts.get(rank, 0) / (4 * num_decks)
        
        # Count information
        features.update({
            'running_count': running_count,
            'true_count': true_count,
            'remaining_cards': remaining_cards,
            'remaining_decks': remaining_cards / 52,
            'penetration': len(cards_dealt) / total_cards,
        })
        
        # Recent card sequence (last 8 cards)
        recent_cards = cards_dealt[-8:] if len(cards_dealt) >= 8 else cards_dealt
        
        # One-hot encode recent cards
        for i in range(8):
            if i < len(recent_cards):
                card = recent_cards[-(i+1)]  # Most recent first
                for rank in self.ranks:
                    features[f'recent_{i}_{rank}'] = 1 if card == rank else 0
            else:
                # Pad with zeros
                for rank in self.ranks:
                    features[f'recent_{i}_{rank}'] = 0
        
        # Sequence pattern features
        if len(recent_cards) > 0:
            recent_values = [self.counting_values[card] for card in recent_cards]
            features.update({
                'recent_high_ratio': sum(1 for v in recent_values if v == -1) / len(recent_values),
                'recent_low_ratio': sum(1 for v in recent_values if v == 1) / len(recent_values),
                'recent_neutral_ratio': sum(1 for v in recent_values if v == 0) / len(recent_values),
                'recent_streak_high': self._count_streak(recent_values, -1),
                'recent_streak_low': self._count_streak(recent_values, 1),
            })
        else:
            features.update({
                'recent_high_ratio': 0.0, 'recent_low_ratio': 0.0, 'recent_neutral_ratio': 0.0,
                'recent_streak_high': 0, 'recent_streak_low': 0
            })
        
        # Remaining card group totals
        low_total = sum(card_counts.get(card, 0) for card in ['2','3','4','5','6'])
        neutral_total = sum(card_counts.get(card, 0) for card in ['7','8','9'])
        high_total = sum(card_counts.get(card, 0) for card in ['10','J','Q','K','A'])
        total_remaining = low_total + neutral_total + high_total
        
        features.update({
            'remaining_low_total': low_total,
            'remaining_neutral_total': neutral_total, 
            'remaining_high_total': high_total,
            'low_ratio': low_total / total_remaining if total_remaining > 0 else 0,
            'neutral_ratio': neutral_total / total_remaining if total_remaining > 0 else 0,
            'high_ratio': high_total / total_remaining if total_remaining > 0 else 0,
        })
        
        return features
    
    def _count_streak(self, values: List[int], target_value: int) -> int:
        """Count current streak from start of list."""
        streak = 0
        for value in values:
            if value == target_value:
                streak += 1
            else:
                break
        return streak
    
    def predict(self,
                player_total: int,
                dealer_upcard: str, 
                is_soft: bool = False,
                is_pair: bool = False,
                card_counts: Optional[Dict[str, int]] = None,
                cards_dealt: Optional[List[str]] = None,
                num_decks: int = 8) -> Dict[str, float]:
        """
        Predict EVs for a blackjack hand.
        
        Args:
            player_total: Player's hand total (2-21)
            dealer_upcard: Dealer's upcard ('2'-'10', 'J', 'Q', 'K', 'A')
            is_soft: Whether player hand is soft (contains usable Ace)
            is_pair: Whether player hand is a pair
            card_counts: Dictionary of remaining cards in shoe
            cards_dealt: List of cards dealt so far
            num_decks: Number of decks in shoe
            
        Returns:
            Dictionary with EVs for each action and optimal recommendation
        """
        
        # Use fresh shoe if no card information provided
        if card_counts is None:
            card_counts = {rank: 4 * num_decks for rank in self.ranks}
        
        if cards_dealt is None:
            cards_dealt = []
        
        # Prepare features
        features = self.prepare_features(
            player_total, dealer_upcard, is_soft, is_pair,
            card_counts, cards_dealt, num_decks
        )
        
        # Get prediction
        result = self.predictor.predict_ev(features)
        
        return result
    
    def batch_predict(self, hands: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Predict EVs for multiple hands at once."""
        results = []
        for hand in hands:
            try:
                result = self.predict(**hand)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        return results
    
    def compare_with_basic_strategy(self, 
                                   player_total: int,
                                   dealer_upcard: str, 
                                   is_soft: bool = False,
                                   is_pair: bool = False) -> Dict[str, Any]:
        """Compare ML prediction with basic strategy."""
        
        # Get ML prediction
        ml_result = self.predict(player_total, dealer_upcard, is_soft, is_pair)
        
        # Simple basic strategy logic
        basic_action = self._basic_strategy_action(player_total, dealer_upcard, is_soft, is_pair)
        
        return {
            'ml_prediction': ml_result,
            'basic_strategy_action': basic_action,
            'actions_match': ml_result.get('optimal_action') == basic_action,
            'ev_improvement': ml_result.get('optimal_ev', 0) - self._estimate_basic_strategy_ev(basic_action)
        }
    
    def _basic_strategy_action(self, player_total: int, dealer_upcard: str, 
                              is_soft: bool, is_pair: bool) -> str:
        """Simple basic strategy implementation."""
        dealer_val = self.card_value(dealer_upcard)
        
        if is_pair:
            if player_total == 22:  # A,A
                return 'split'
            elif player_total == 20:  # 10,10
                return 'stand'
            elif player_total == 18:  # 9,9
                return 'split' if dealer_val in [2,3,4,5,6,8,9] else 'stand'
            elif player_total == 16:  # 8,8
                return 'split'
            elif player_total in [14, 12]:  # 7,7 or 6,6
                return 'split' if dealer_val <= 7 else 'hit'
            else:
                return 'hit'
        
        if is_soft:
            if player_total >= 19:
                return 'stand'
            elif player_total == 18:
                if dealer_val in [3,4,5,6]:
                    return 'double'
                elif dealer_val in [2,7,8]:
                    return 'stand'
                else:
                    return 'hit'
            elif player_total in [17, 16, 15]:
                return 'double' if dealer_val in [4,5,6] else 'hit'
            elif player_total in [14, 13]:
                return 'double' if dealer_val in [5,6] else 'hit'
            else:
                return 'hit'
        
        # Hard hands
        if player_total >= 17:
            return 'stand'
        elif player_total >= 13:
            return 'stand' if dealer_val <= 6 else 'hit'
        elif player_total == 12:
            return 'stand' if dealer_val in [4,5,6] else 'hit'
        elif player_total == 11:
            return 'double'
        elif player_total == 10:
            return 'double' if dealer_val <= 9 else 'hit'
        elif player_total == 9:
            return 'double' if dealer_val in [3,4,5,6] else 'hit'
        else:
            return 'hit'
    
    def _estimate_basic_strategy_ev(self, action: str) -> float:
        """Rough EV estimate for basic strategy (for comparison)."""
        ev_estimates = {
            'hit': -0.1,
            'stand': -0.1, 
            'double': -0.05,
            'split': 0.0
        }
        return ev_estimates.get(action, -0.1)

def demo_inference():
    """Demonstrate the inference engine."""
    print("🃏 Blackjack EV Inference Engine Demo")
    print("=====================================")
    
    try:
        # Initialize engine
        print("Loading trained model...")
        engine = BlackjackInferenceEngine()
        print("✅ Model loaded successfully!")
        
        # Test scenarios
        test_hands = [
            {
                'player_total': 16,
                'dealer_upcard': '10',
                'is_soft': False,
                'is_pair': False,
                'description': 'Hard 16 vs 10 (classic difficult hand)'
            },
            {
                'player_total': 18,
                'dealer_upcard': '6',
                'is_soft': True,
                'is_pair': False,
                'description': 'Soft 18 vs 6 (A,7 vs 6)'
            },
            {
                'player_total': 16,
                'dealer_upcard': '7',
                'is_soft': False,
                'is_pair': True,
                'description': 'Pair of 8s vs 7'
            },
            {
                'player_total': 11,
                'dealer_upcard': 'A',
                'is_soft': False,
                'is_pair': False,
                'description': 'Hard 11 vs Ace'
            }
        ]
        
        for i, hand in enumerate(test_hands, 1):
            print(f"\n🎯 Test Hand {i}: {hand['description']}")
            print("-" * 50)
            
            # Remove description for prediction
            hand_data = {k: v for k, v in hand.items() if k != 'description'}
            
            # Get prediction
            result = engine.predict(**hand_data)
            
            print("ML Predictions:")
            for action, ev in result.items():
                if action not in ['optimal_action', 'optimal_ev']:
                    print(f"  {action.capitalize()}: {ev:+.4f}")
            
            print(f"\n🎯 Optimal Action: {result.get('optimal_action', 'Unknown')}")
            print(f"📊 Expected Value: {result.get('optimal_ev', 0):+.4f}")
            
            # Compare with basic strategy
            comparison = engine.compare_with_basic_strategy(**hand_data)
            print(f"📖 Basic Strategy: {comparison['basic_strategy_action']}")
            print(f"🤝 Actions Match: {comparison['actions_match']}")
            
        print(f"\n✅ Demo completed successfully!")
        
    except FileNotFoundError:
        print("❌ Model files not found. Please train the model first by running:")
        print("   python data_generator.py")
        print("   python ml_model.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_inference()
