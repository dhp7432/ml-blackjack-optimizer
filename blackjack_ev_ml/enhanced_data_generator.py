"""
Enhanced Blackjack EV ML Training Data Generator
==============================================
Improved version that scales to 500K+ samples with advanced features.
Works immediately without requiring real shoe recordings.
"""

import random
import numpy as np
import pandas as pd
from copy import deepcopy
from typing import Dict, List, Tuple, Any, Optional
import json
import os
from tqdm import tqdm
from pathlib import Path

# Import the existing generator as base
import sys
sys.path.append('.')
from data_generator import BlackjackDataGenerator

class EnhancedBlackjackDataGenerator(BlackjackDataGenerator):
    """Enhanced generator with 500K+ samples and advanced features."""
    
    def __init__(self, num_decks=8):
        super().__init__(num_decks)
        
        # Enhanced tracking for advanced features
        self.max_running_count = 0
        self.min_running_count = 0
        self.max_true_count = 0.0
        self.min_true_count = 0.0
        
    def reset_shoe(self):
        """Reset shoe with enhanced tracking."""
        super().reset_shoe()
        self.max_running_count = 0
        self.min_running_count = 0
        self.max_true_count = 0.0
        self.min_true_count = 0.0
        
    def deal_card(self, card: str) -> bool:
        """Enhanced card dealing with extremes tracking."""
        success = super().deal_card(card)
        
        if success:
            # Track extremes
            self.max_running_count = max(self.max_running_count, self.running_count)
            self.min_running_count = min(self.min_running_count, self.running_count)
            
            true_count = self.get_true_count()
            self.max_true_count = max(self.max_true_count, true_count)
            self.min_true_count = min(self.min_true_count, true_count)
            
        return success
    
    def extract_enhanced_features(self) -> Dict[str, float]:
        """Extract comprehensive features including advanced patterns."""
        # Start with base features
        features = self.extract_features()
        
        # Add advanced tracking features
        features.update({
            'max_running_count': self.max_running_count,
            'min_running_count': self.min_running_count,
            'max_true_count': self.max_true_count,
            'min_true_count': self.min_true_count,
            'count_volatility': self.max_running_count - self.min_running_count,
            'true_count_range': self.max_true_count - self.min_true_count,
        })
        
        # Advanced sequence pattern features
        recent_cards = self.cards_dealt[-8:] if len(self.cards_dealt) >= 8 else self.cards_dealt
        
        if len(recent_cards) > 0:
            # Pattern detection features
            features.update({
                'recent_clumping_index': self._calculate_clumping_index(recent_cards),
                'recent_alternating_score': self._calculate_alternating_score(recent_cards),
                'recent_high_streak': self._calculate_streak(recent_cards, 'high'),
                'recent_low_streak': self._calculate_streak(recent_cards, 'low'),
                'dealer_favor_bias': self._calculate_dealer_bias(recent_cards),
                'player_favor_bias': 1.0 - self._calculate_dealer_bias(recent_cards),
            })
        else:
            # Default values when no recent cards
            features.update({
                'recent_clumping_index': 0.0,
                'recent_alternating_score': 0.0,
                'recent_high_streak': 0,
                'recent_low_streak': 0,
                'dealer_favor_bias': 0.5,
                'player_favor_bias': 0.5,
            })
        
        # Penetration-adjusted features
        penetration = features.get('penetration', 0.0)
        features.update({
            'penetration_adjusted_count': features.get('true_count', 0.0) * (penetration ** 0.5),
            'late_game_factor': 1.0 if penetration > 0.3 else penetration / 0.3,
            'pattern_significance': 1.0 if penetration > 0.3 else 0.0,  # Your 30% rule!
        })
        
        return features
    
    def _calculate_clumping_index(self, cards: List[str]) -> float:
        """Calculate how much cards are clumped vs randomly distributed."""
        if len(cards) < 3:
            return 0.0
        
        # Count consecutive same-type cards
        clumps = 0
        current_type = self._get_card_type(cards[0])
        
        for i in range(1, len(cards)):
            if self._get_card_type(cards[i]) == current_type:
                clumps += 1
            else:
                current_type = self._get_card_type(cards[i])
        
        # Normalize by maximum possible clumps
        max_clumps = len(cards) - 1
        return clumps / max_clumps if max_clumps > 0 else 0.0
    
    def _calculate_alternating_score(self, cards: List[str]) -> float:
        """Calculate how much high/low cards alternate."""
        if len(cards) < 2:
            return 0.0
        
        alternations = 0
        for i in range(1, len(cards)):
            prev_type = self._get_card_type(cards[i-1])
            curr_type = self._get_card_type(cards[i])
            
            if ((prev_type == 'high' and curr_type == 'low') or 
                (prev_type == 'low' and curr_type == 'high')):
                alternations += 1
        
        max_alternations = len(cards) - 1
        return alternations / max_alternations if max_alternations > 0 else 0.0
    
    def _calculate_streak(self, cards: List[str], card_type: str) -> int:
        """Calculate longest streak of high or low cards."""
        if not cards:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for card in cards:
            if self._get_card_type(card) == card_type:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_dealer_bias(self, cards: List[str]) -> float:
        """Calculate bias toward dealer-favorable cards in recent sequence."""
        if not cards:
            return 0.5
        
        # Cards that generally favor dealer (help avoid bust)
        dealer_favorable = ['5', '6', '7', '8', '9']
        dealer_favor_count = sum(1 for card in cards if card in dealer_favorable)
        
        return dealer_favor_count / len(cards)
    
    def _get_card_type(self, card: str) -> str:
        """Classify card as high, low, or neutral."""
        if card in ['2', '3', '4', '5', '6']:
            return 'low'
        elif card in ['10', 'J', 'Q', 'K', 'A']:
            return 'high'
        else:
            return 'neutral'
    
    def generate_enhanced_training_data(self, num_samples: int = 500000) -> pd.DataFrame:
        """Generate massive enhanced training dataset."""
        
        print(f"🚀 Generating {num_samples:,} enhanced training samples...")
        data = []
        
        with tqdm(total=num_samples, desc="Generating samples") as pbar:
            while len(data) < num_samples:
                
                # Reset shoe with enhanced diversity strategies
                if len(data) % 1000 == 0 or self.remaining_cards < 100:
                    self.reset_shoe()
                    
                    # Create diverse shoe states with different strategies
                    strategy = random.choice(['random', 'high_early', 'low_early', 'balanced', 'extreme_count'])
                    penetration_target = random.uniform(0.05, 0.75)  # 5% to 75% penetration
                    cards_to_deal = int((self.num_decks * 52) * penetration_target)
                    
                    self._create_diverse_shoe_state(strategy, cards_to_deal)
                
                # Generate sample with enhanced features
                sample_data = self._generate_enhanced_sample()
                if sample_data:
                    data.append(sample_data)
                    pbar.update(1)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        print(f"\n✅ Generated {len(df):,} samples with {len(df.columns)} features")
        
        return df
    
    def _create_diverse_shoe_state(self, strategy: str, cards_to_deal: int):
        """Create diverse shoe states for better training coverage."""
        
        for _ in range(cards_to_deal):
            available_ranks = [r for r in self.ranks if self.card_counts[r] > 0]
            if not available_ranks:
                break
            
            if strategy == 'high_early':
                # Bias toward high cards early in shoe
                high_cards = [r for r in available_ranks if r in ['10', 'J', 'Q', 'K', 'A']]
                card = random.choice(high_cards if high_cards and random.random() < 0.6 else available_ranks)
                
            elif strategy == 'low_early':
                # Bias toward low cards early in shoe  
                low_cards = [r for r in available_ranks if r in ['2', '3', '4', '5', '6']]
                card = random.choice(low_cards if low_cards and random.random() < 0.6 else available_ranks)
                
            elif strategy == 'extreme_count':
                # Try to create extreme count situations
                if self.running_count < 10:
                    # Push toward positive count
                    low_cards = [r for r in available_ranks if r in ['2', '3', '4', '5', '6']]
                    card = random.choice(low_cards if low_cards and random.random() < 0.7 else available_ranks)
                elif self.running_count > -10:
                    # Push toward negative count
                    high_cards = [r for r in available_ranks if r in ['10', 'J', 'Q', 'K', 'A']]
                    card = random.choice(high_cards if high_cards and random.random() < 0.7 else available_ranks)
                else:
                    card = random.choice(available_ranks)
                    
            else:  # 'random' or 'balanced'
                card = random.choice(available_ranks)
            
            self.deal_card(card)
    
    def _generate_enhanced_sample(self) -> Optional[Dict[str, Any]]:
        """Generate a single enhanced training sample."""
        
        # Enhanced hand generation focusing on important scenarios
        scenario_type = random.choice(['random', 'edge_case', 'common_decision', 'count_dependent'])
        
        if scenario_type == 'edge_case':
            # Focus on difficult decisions
            edge_scenarios = [
                (16, ['7', '8', '9', '10', 'A']),  # Hard 16 vs high cards
                (15, ['10', 'A']),                 # Hard 15 vs 10 or A
                (12, ['2', '3', '4']),             # Hard 12 vs low dealer
                (11, ['A']),                       # 11 vs Ace
                (13, ['2']),                       # A,2 vs 2 (soft doubling)
                (18, ['9', '10', 'A']),            # A,7 vs strong dealer
            ]
            player_total, dealer_options = random.choice(edge_scenarios)
            dealer_upcard = random.choice(dealer_options)
            is_soft = player_total in [13, 14, 15, 16, 17, 18] and random.random() < 0.7
            is_pair = False
            
        elif scenario_type == 'count_dependent':
            # Scenarios where count matters most
            count_scenarios = [
                (16, ['10']),     # 16 vs 10 (surrender in high counts)
                (15, ['10']),     # 15 vs 10
                (12, ['2', '3']), # 12 vs low (hit in negative counts)
                (11, ['A']),      # 11 vs A (double in positive counts)
                (10, ['A']),      # 10 vs A
            ]
            player_total, dealer_options = random.choice(count_scenarios)
            dealer_upcard = random.choice(dealer_options)
            is_soft = False
            is_pair = False
            
        elif scenario_type == 'common_decision':
            # Most frequent decision points
            common_hands = [
                (17, False, False), (18, False, False), (19, False, False), (20, False, False),
                (9, False, False), (10, False, False), (11, False, False),
                (13, True, False), (14, True, False), (15, True, False), (16, True, False), (17, True, False), (18, True, False),
                (12, False, True), (14, False, True), (16, False, True), (18, False, True), (20, False, True),
            ]
            player_total, is_soft, is_pair = random.choice(common_hands)
            dealer_upcard = random.choice(self.ranks)
            
        else:  # random
            player_total = random.randint(4, 21)
            dealer_upcard = random.choice(self.ranks)
            is_soft = random.choice([True, False]) if player_total <= 18 else False
            is_pair = random.choice([True, False]) if player_total % 2 == 0 and 4 <= player_total <= 20 else False
        
        # Validate hand
        if is_pair and is_soft:
            is_soft = False
        if is_soft and player_total < 13:
            return None
        
        # Extract enhanced features
        features = self.extract_enhanced_features()
        
        # Add hand-specific features
        features.update({
            'player_total': player_total,
            'dealer_upcard_value': self.card_value(dealer_upcard),
            'is_soft': int(is_soft),
            'is_pair': int(is_pair),
        })
        
        # Add dealer upcard one-hot encoding
        for rank in self.ranks:
            features[f'dealer_{rank}'] = 1 if dealer_upcard == rank else 0
        
        # Calculate EVs with higher precision for better training
        try:
            evs = self.simulate_hand_ev(player_total, dealer_upcard, is_soft, is_pair, trials=8000)
            
            if evs:
                features.update({
                    'hit_ev': evs.get('hit', 0.0),
                    'stand_ev': evs.get('stand', 0.0),
                    'double_ev': evs.get('double', 0.0),
                    'split_ev': evs.get('split', 0.0),
                    'optimal_action': evs.get('optimal_action', 'stand'),
                    'optimal_ev': evs.get('optimal_ev', 0.0),
                })
                
                return features
        except Exception as e:
            pass
        
        return None


def main():
    """Generate enhanced training data."""
    print("🚀 Enhanced Blackjack Training Data Generator")
    print("=" * 50)
    
    generator = EnhancedBlackjackDataGenerator()
    
    # Generate samples
    sample_size = int(input("Enter number of samples (e.g., 50000, 500000): ") or "50000")
    
    print(f"\n📊 Generating {sample_size:,} enhanced samples...")
    df = generator.generate_enhanced_training_data(num_samples=sample_size)
    
    # Save the data
    save_path = f"analysis/data/blackjack_training_data_enhanced_{sample_size//1000}k.csv"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)
    
    print(f"\n✅ Training data generated successfully!")
    print(f"   📈 Total samples: {len(df):,}")
    print(f"   🎯 Total features: {len(df.columns)}")
    print(f"   💾 Saved to: {save_path}")
    
    # Show feature summary
    new_features = [col for col in df.columns if any(x in col for x in [
        'clumping', 'alternating', 'streak', 'bias', 'volatility', 'max_', 'min_', 'pattern_'
    ])]
    
    if new_features:
        print(f"\n🆕 New enhanced features ({len(new_features)}):")
        for feature in new_features:
            print(f"   • {feature}")
    
    # Show sample statistics
    print(f"\n📊 Sample Statistics:")
    print(f"   • Penetration range: {df['penetration'].min():.1%} - {df['penetration'].max():.1%}")
    print(f"   • True count range: {df['true_count'].min():.1f} - {df['true_count'].max():.1f}")
    print(f"   • Count volatility range: {df['count_volatility'].min():.1f} - {df['count_volatility'].max():.1f}")
    
    return df


if __name__ == "__main__":
    df = main()
