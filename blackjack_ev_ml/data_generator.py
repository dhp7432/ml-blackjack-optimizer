"""
Blackjack EV ML Training Data Generator
=====================================
Generates training data for machine learning model to predict Expected Values
in blackjack based on hand configuration, shoe composition, and card sequences.
"""

import random
import numpy as np
import pandas as pd
from copy import deepcopy
from typing import Dict, List, Tuple, Any
import json
from tqdm import tqdm

class BlackjackDataGenerator:
    """Generate training data for blackjack EV prediction model."""
    
    def __init__(self, num_decks=8):
        self.num_decks = num_decks
        self.ranks = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        self.face_to_ten = {'10', 'J', 'Q', 'K'}
        
        # Hi-Lo values for counting
        self.counting_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
        
        # Initialize fresh shoe
        self.reset_shoe()
        
    def reset_shoe(self):
        """Reset to fresh 8-deck shoe."""
        self.card_counts = {rank: 4 * self.num_decks for rank in self.ranks}
        self.cards_dealt = []
        self.running_count = 0
        self.remaining_cards = self.num_decks * 52
        
    def deal_card(self, card: str) -> bool:
        """Deal a card from shoe. Returns True if successful."""
        if self.card_counts.get(card, 0) > 0:
            self.card_counts[card] -= 1
            self.cards_dealt.append(card)
            self.running_count += self.counting_values[card]
            self.remaining_cards -= 1
            return True
        return False
    
    def get_true_count(self) -> float:
        """Calculate true count."""
        remaining_decks = self.remaining_cards / 52
        return self.running_count / remaining_decks if remaining_decks > 0 else 0.0
    
    def card_value(self, rank: str) -> int:
        """Get card value for blackjack."""
        if rank == 'A': 
            return 11
        if rank in self.face_to_ten: 
            return 10
        return int(rank)
    
    def simulate_hand_ev(self, player_total: int, dealer_upcard: str, 
                        is_soft: bool, is_pair: bool, trials: int = 10000) -> Dict[str, float]:
        """
        Monte Carlo simulation to get true EVs for current shoe state.
        This is our ground truth for training.
        """
        if dealer_upcard not in self.ranks:
            return {}
            
        evs = {}
        actions = ['hit', 'stand']
        
        # Add double if applicable
        if (not is_pair and (9 <= player_total <= 11 or (is_soft and 13 <= player_total <= 18))):
            actions.append('double')
            
        # Add split if pair
        if is_pair:
            actions.append('split')
        
        for action in actions:
            total_profit = 0.0
            valid_trials = 0
            
            for _ in range(trials):
                # Create temporary shoe state for simulation
                temp_counts = deepcopy(self.card_counts)
                
                # Remove dealer upcard
                if temp_counts[dealer_upcard] > 0:
                    temp_counts[dealer_upcard] -= 1
                    profit = self._simulate_action(player_total, dealer_upcard, is_soft, 
                                                 is_pair, action, temp_counts)
                    total_profit += profit
                    valid_trials += 1
            
            if valid_trials > 0:
                evs[action] = total_profit / valid_trials
        
        return evs
    
    def _simulate_action(self, player_total: int, dealer_upcard: str, is_soft: bool,
                        is_pair: bool, action: str, shoe_counts: Dict[str, int]) -> float:
        """Simulate a single action and return profit/loss."""
        rng = random.Random()
        
        # Simple simulation - this is a simplified version
        # In practice, you'd want full game simulation
        if action == 'stand':
            dealer_total = self._simulate_dealer_hand(dealer_upcard, shoe_counts, rng)
            return self._settle_hand(player_total, dealer_total)
            
        elif action == 'hit':
            # Draw one card for player
            new_card = self._draw_random_card(shoe_counts, rng)
            if new_card:
                new_total = player_total + self.card_value(new_card)
                if new_card == 'A' and not is_soft:
                    is_soft = True
                # Handle soft ace conversion
                if new_total > 21 and is_soft:
                    new_total -= 10
                    is_soft = False
                    
                if new_total > 21:
                    return -1.0  # Bust
                else:
                    dealer_total = self._simulate_dealer_hand(dealer_upcard, shoe_counts, rng)
                    return self._settle_hand(new_total, dealer_total)
            return -1.0
            
        elif action == 'double':
            # Double down - one card only, double bet
            new_card = self._draw_random_card(shoe_counts, rng)
            if new_card:
                new_total = player_total + self.card_value(new_card)
                if new_card == 'A' and not is_soft:
                    is_soft = True
                if new_total > 21 and is_soft:
                    new_total -= 10
                    is_soft = False
                    
                if new_total > 21:
                    return -2.0  # Bust with double bet
                else:
                    dealer_total = self._simulate_dealer_hand(dealer_upcard, shoe_counts, rng)
                    return 2.0 * self._settle_hand(new_total, dealer_total)
            return -2.0
            
        elif action == 'split':
            # Simplified split simulation
            if is_pair:
                hand1_profit = self._simulate_split_hand(player_total // 2, shoe_counts, rng)
                hand2_profit = self._simulate_split_hand(player_total // 2, shoe_counts, rng)
                dealer_total = self._simulate_dealer_hand(dealer_upcard, shoe_counts, rng)
                return hand1_profit + hand2_profit
            return -1.0
        
        return 0.0
    
    def _draw_random_card(self, shoe_counts: Dict[str, int], rng) -> str:
        """Draw random card from remaining cards."""
        available_cards = []
        for rank, count in shoe_counts.items():
            available_cards.extend([rank] * count)
        
        if available_cards:
            card = rng.choice(available_cards)
            shoe_counts[card] -= 1
            return card
        return None
    
    def _simulate_dealer_hand(self, upcard: str, shoe_counts: Dict[str, int], rng) -> int:
        """Simulate dealer hand to completion."""
        total = self.card_value(upcard)
        soft_aces = 1 if upcard == 'A' else 0
        
        # Dealer hits soft 17 or less
        while total < 17 or (total == 17 and soft_aces > 0):
            card = self._draw_random_card(shoe_counts, rng)
            if not card:
                break
                
            value = self.card_value(card)
            if card == 'A':
                soft_aces += 1
                
            total += value
            
            # Convert soft aces if busting
            while total > 21 and soft_aces > 0:
                total -= 10
                soft_aces -= 1
                
        return total
    
    def _simulate_split_hand(self, start_card_value: int, shoe_counts: Dict[str, int], rng) -> float:
        """Simulate one hand after split."""
        total = start_card_value
        
        # Draw one more card
        card = self._draw_random_card(shoe_counts, rng)
        if card:
            total += self.card_value(card)
            # Basic strategy: hit if under 17
            if total < 17:
                card2 = self._draw_random_card(shoe_counts, rng)
                if card2:
                    total += self.card_value(card2)
        
        return total if total <= 21 else 0  # Return 0 if bust, will be settled against dealer
    
    def _settle_hand(self, player_total: int, dealer_total: int) -> float:
        """Settle hand and return profit/loss."""
        if player_total > 21:
            return -1.0
        if dealer_total > 21:
            return 1.0
        if player_total > dealer_total:
            return 1.0
        elif player_total < dealer_total:
            return -1.0
        else:
            return 0.0  # Push
    
    def extract_features(self) -> Dict[str, Any]:
        """Extract all features for current shoe state."""
        # Basic composition features
        features = {
            # Card counts (normalized)
            **{f'count_{rank}': self.card_counts[rank] / (4 * self.num_decks) for rank in self.ranks},
            
            # Count information
            'running_count': self.running_count,
            'true_count': self.get_true_count(),
            'remaining_cards': self.remaining_cards,
            'remaining_decks': self.remaining_cards / 52,
            'penetration': len(self.cards_dealt) / (self.num_decks * 52),
        }
        
        # Recent card sequence features (last 8 cards)
        recent_cards = self.cards_dealt[-8:] if len(self.cards_dealt) >= 8 else self.cards_dealt
        
        # One-hot encode recent cards
        for i in range(8):
            if i < len(recent_cards):
                card = recent_cards[-(i+1)]  # Most recent first
                for rank in self.ranks:
                    features[f'recent_{i}_{rank}'] = 1 if card == rank else 0
            else:
                # Pad with zeros if not enough cards dealt yet
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
        low_total = sum(self.card_counts[card] for card in ['2','3','4','5','6'])
        neutral_total = sum(self.card_counts[card] for card in ['7','8','9'])
        high_total = sum(self.card_counts[card] for card in ['10','J','Q','K','A'])
        
        features.update({
            'remaining_low_total': low_total,
            'remaining_neutral_total': neutral_total, 
            'remaining_high_total': high_total,
            'low_ratio': low_total / (low_total + neutral_total + high_total) if (low_total + neutral_total + high_total) > 0 else 0,
            'neutral_ratio': neutral_total / (low_total + neutral_total + high_total) if (low_total + neutral_total + high_total) > 0 else 0,
            'high_ratio': high_total / (low_total + neutral_total + high_total) if (low_total + neutral_total + high_total) > 0 else 0,
        })
        
        return features
    
    def _count_streak(self, values: List[int], target_value: int) -> int:
        """Count current streak of target value from start of list."""
        streak = 0
        for value in values:
            if value == target_value:
                streak += 1
            else:
                break
        return streak
    
    def generate_training_data(self, num_samples: int = 50000) -> pd.DataFrame:
        """Generate training dataset."""
        data = []
        
        print(f"Generating {num_samples} training samples...")
        
        with tqdm(total=num_samples) as pbar:
            while len(data) < num_samples:
                # Reset shoe periodically to get varied shoe states
                if len(data) % 1000 == 0 or self.remaining_cards < 100:
                    self.reset_shoe()
                    # Deal some random cards to get varied shoe states
                    cards_to_deal = random.randint(50, 300)
                    for _ in range(cards_to_deal):
                        available_ranks = [r for r in self.ranks if self.card_counts[r] > 0]
                        if available_ranks:
                            self.deal_card(random.choice(available_ranks))
                
                # Generate random hand scenario
                player_total = random.randint(4, 21)
                dealer_upcard = random.choice(self.ranks)
                is_soft = random.choice([True, False]) if player_total <= 11 else False
                is_pair = random.choice([True, False]) if player_total % 2 == 0 and 4 <= player_total <= 20 else False
                
                # Skip impossible hands
                if is_pair and is_soft:
                    is_soft = False  # Pairs override soft
                if is_soft and player_total < 13:
                    continue  # Soft hands start at A,2 = 13
                
                # Extract features
                features = self.extract_features()
                
                # Add hand-specific features
                features.update({
                    'player_total': player_total,
                    'dealer_upcard_value': self.card_value(dealer_upcard),
                    'is_soft': int(is_soft),
                    'is_pair': int(is_pair),
                })
                
                # Add one-hot encoding for dealer upcard
                for rank in self.ranks:
                    features[f'dealer_{rank}'] = 1 if dealer_upcard == rank else 0
                
                # Calculate true EVs using Monte Carlo
                try:
                    evs = self.simulate_hand_ev(player_total, dealer_upcard, is_soft, is_pair, trials=5000)
                    
                    if evs:  # Only add if we got valid EVs
                        # Add target variables
                        features.update({
                            f'{action}_ev': ev for action, ev in evs.items()
                        })
                        
                        # Find optimal action and EV
                        if evs:
                            optimal_action = max(evs.keys(), key=lambda k: evs[k])
                            features['optimal_action'] = optimal_action
                            features['optimal_ev'] = evs[optimal_action]
                        
                        data.append(features)
                        pbar.update(1)
                        
                except Exception as e:
                    continue  # Skip this sample if simulation fails
                
                # Deal a random card to advance shoe state
                available_ranks = [r for r in self.ranks if self.card_counts[r] > 0]
                if available_ranks:
                    self.deal_card(random.choice(available_ranks))
        
        df = pd.DataFrame(data)
        print(f"Generated {len(df)} training samples with {len(df.columns)} features")
        return df

if __name__ == "__main__":
    # Generate training data
    generator = BlackjackDataGenerator()
    
    # Generate dataset
    df = generator.generate_training_data(num_samples=25000)
    
    # Save to CSV
    df.to_csv('blackjack_training_data.csv', index=False)
    print("Training data saved to 'blackjack_training_data.csv'")
    
    # Print basic statistics
    print(f"\nDataset shape: {df.shape}")
    print(f"Features: {len([col for col in df.columns if not col.endswith('_ev') and col != 'optimal_action'])}")
    print(f"Target variables: {[col for col in df.columns if col.endswith('_ev') or col == 'optimal_action']}")
    
    if 'optimal_action' in df.columns:
        print(f"\nAction distribution:")
        print(df['optimal_action'].value_counts())
    
    if 'optimal_ev' in df.columns:
        print(f"\nEV statistics:")
        print(df['optimal_ev'].describe())
