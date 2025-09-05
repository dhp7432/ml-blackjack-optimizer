"""
Batch Shoe Analysis Tool
=======================
Analyze multiple recorded shoes for patterns and ML performance.
"""

import json
import glob
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any
from pathlib import Path
from shoe_recorder import ShoeRecord, HandRecord, ShoeAnalyzer

class BatchAnalyzer:
    """Analyzes multiple recorded shoes for insights."""
    
    def __init__(self, model_path: str = 'blackjack_ev_model'):
        self.analyzer = ShoeAnalyzer(model_path)
        
    def load_all_shoes(self, pattern: str = "shoe_*.json") -> List[ShoeRecord]:
        """Load all shoe files matching pattern."""
        shoe_files = glob.glob(pattern)
        shoes = []
        
        print(f"📂 Loading shoes from pattern: {pattern}")
        
        for filename in shoe_files:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Convert back to dataclasses
                hands = [HandRecord(**hand) for hand in data['hands']]
                data['hands'] = hands
                shoe = ShoeRecord(**data)
                shoes.append(shoe)
                
                print(f"   ✅ Loaded {filename}: {len(shoe.hands)} hands")
                
            except Exception as e:
                print(f"   ❌ Error loading {filename}: {e}")
        
        print(f"\n📊 Total: {len(shoes)} shoes loaded")
        return shoes
    
    def analyze_all_shoes(self, shoes: List[ShoeRecord]) -> Dict[str, Any]:
        """Run comprehensive analysis on all shoes."""
        print(f"\n🤖 Analyzing {len(shoes)} shoes with ML model...")
        
        all_analyses = []
        total_hands = 0
        total_profit = 0.0
        
        for i, shoe in enumerate(shoes, 1):
            print(f"   Processing shoe {i}/{len(shoes)}: {shoe.shoe_id}")
            
            analysis = self.analyzer.analyze_shoe(shoe)
            all_analyses.append(analysis)
            
            total_hands += len(shoe.hands)
            total_profit += analysis['shoe_info']['total_profit']
        
        # Combine results
        combined_analysis = self._combine_analyses(all_analyses)
        combined_analysis['overview'] = {
            'total_shoes': len(shoes),
            'total_hands': total_hands,
            'total_profit': total_profit,
            'average_hands_per_shoe': total_hands / len(shoes) if shoes else 0,
            'average_profit_per_shoe': total_profit / len(shoes) if shoes else 0,
            'average_profit_per_hand': total_profit / total_hands if total_hands else 0
        }
        
        return combined_analysis
    
    def _combine_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple shoe analyses."""
        
        # Collect all hand analyses
        all_hands = []
        shoe_summaries = []
        
        for analysis in analyses:
            all_hands.extend(analysis['hand_analyses'])
            shoe_summaries.append(analysis['summary_stats'])
        
        # Calculate combined statistics
        if all_hands:
            correct_predictions = sum(1 for h in all_hands if h['prediction_correct'])
            total_hands = len(all_hands)
            total_ml_ev = sum(h['ml_result'].get('optimal_ev', 0) for h in all_hands)
            total_actual_profit = sum(h['actual_profit'] for h in all_hands)
            
            combined_stats = {
                'total_hands': total_hands,
                'prediction_accuracy': correct_predictions / total_hands,
                'ml_predicted_ev': total_ml_ev / total_hands,
                'actual_ev': total_actual_profit / total_hands,
                'ev_difference': (total_actual_profit - total_ml_ev) / total_hands
            }
        else:
            combined_stats = {
                'total_hands': 0,
                'prediction_accuracy': 0,
                'ml_predicted_ev': 0,
                'actual_ev': 0,
                'ev_difference': 0
            }
        
        return {
            'combined_stats': combined_stats,
            'all_hands': all_hands,
            'shoe_summaries': shoe_summaries,
            'individual_analyses': analyses
        }
    
    def generate_report(self, analysis: Dict[str, Any], output_file: str = "batch_analysis_report.txt"):
        """Generate detailed text report."""
        
        with open(output_file, 'w') as f:
            f.write("BLACKJACK SHOE ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Overview
            overview = analysis['overview']
            f.write("OVERVIEW\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Shoes Analyzed: {overview['total_shoes']}\n")
            f.write(f"Total Hands Played: {overview['total_hands']}\n")
            f.write(f"Total Profit/Loss: ${overview['total_profit']:+.2f}\n")
            f.write(f"Average Hands per Shoe: {overview['average_hands_per_shoe']:.1f}\n")
            f.write(f"Average Profit per Shoe: ${overview['average_profit_per_shoe']:+.2f}\n")
            f.write(f"Average Profit per Hand: ${overview['average_profit_per_hand']:+.4f}\n\n")
            
            # ML Performance
            stats = analysis['combined_stats']
            f.write("ML PERFORMANCE\n")
            f.write("-" * 20 + "\n")
            f.write(f"Prediction Accuracy: {stats['prediction_accuracy']:.1%}\n")
            f.write(f"ML Predicted EV: {stats['ml_predicted_ev']:+.4f}\n")
            f.write(f"Actual EV: {stats['actual_ev']:+.4f}\n")
            f.write(f"EV Difference: {stats['ev_difference']:+.4f}\n\n")
            
            # Action Analysis
            f.write("ACTION ANALYSIS\n")
            f.write("-" * 20 + "\n")
            action_stats = self._analyze_actions(analysis['all_hands'])
            for action, stats_dict in action_stats.items():
                f.write(f"{action.upper()}:\n")
                f.write(f"  Count: {stats_dict['count']}\n")
                f.write(f"  ML Accuracy: {stats_dict['accuracy']:.1%}\n")
                f.write(f"  Avg Profit: ${stats_dict['avg_profit']:+.3f}\n\n")
            
            # Common Disagreements
            f.write("COMMON ML DISAGREEMENTS\n")
            f.write("-" * 30 + "\n")
            disagreements = [h for h in analysis['all_hands'] if not h['prediction_correct']]
            disagreement_patterns = self._analyze_disagreement_patterns(disagreements)
            
            for pattern, count in disagreement_patterns.most_common(10):
                f.write(f"{pattern}: {count} times\n")
            
        print(f"📄 Report saved to: {output_file}")
    
    def _analyze_actions(self, hands: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by action type."""
        action_stats = {}
        
        for hand in hands:
            action = hand['action_taken']
            if action not in action_stats:
                action_stats[action] = {
                    'count': 0,
                    'correct': 0,
                    'total_profit': 0.0
                }
            
            action_stats[action]['count'] += 1
            if hand['prediction_correct']:
                action_stats[action]['correct'] += 1
            action_stats[action]['total_profit'] += hand['actual_profit']
        
        # Calculate derived stats
        for action, stats in action_stats.items():
            stats['accuracy'] = stats['correct'] / stats['count'] if stats['count'] > 0 else 0
            stats['avg_profit'] = stats['total_profit'] / stats['count'] if stats['count'] > 0 else 0
        
        return action_stats
    
    def _analyze_disagreement_patterns(self, disagreements: List[Dict[str, Any]]) -> Any:
        """Find common patterns in ML disagreements."""
        from collections import Counter
        
        patterns = []
        for hand in disagreements:
            # Create pattern string
            player_total = sum(self._card_value(card) for card in hand['player_cards'])
            pattern = f"{player_total} vs {hand['dealer_upcard']}: You={hand['action_taken']}, ML={hand['ml_recommended']}"
            patterns.append(pattern)
        
        return Counter(patterns)
    
    def _card_value(self, card: str) -> int:
        """Get card value."""
        if card == 'A':
            return 11
        elif card in ['J', 'Q', 'K']:
            return 10
        else:
            return int(card)
    
    def create_visualizations(self, analysis: Dict[str, Any], output_dir: str = "analysis_plots"):
        """Create visualization plots."""
        Path(output_dir).mkdir(exist_ok=True)
        
        hands = analysis['all_hands']
        if not hands:
            print("No hands to visualize.")
            return
        
        # 1. Accuracy by hand number (to see if performance changes during shoe)
        plt.figure(figsize=(12, 6))
        
        hand_numbers = [h['hand_number'] for h in hands]
        accuracies = [1 if h['prediction_correct'] else 0 for h in hands]
        
        # Rolling average accuracy
        window = 10
        rolling_acc = pd.Series(accuracies).rolling(window, min_periods=1).mean()
        
        plt.subplot(1, 2, 1)
        plt.plot(hand_numbers, rolling_acc)
        plt.title(f'ML Accuracy vs Hand Number\n(Rolling {window}-hand average)')
        plt.xlabel('Hand Number')
        plt.ylabel('Accuracy')
        plt.grid(True, alpha=0.3)
        
        # 2. Profit by hand number
        profits = [h['actual_profit'] for h in hands]
        cumulative_profit = pd.Series(profits).cumsum()
        
        plt.subplot(1, 2, 2)
        plt.plot(hand_numbers, cumulative_profit)
        plt.title('Cumulative Profit vs Hand Number')
        plt.xlabel('Hand Number') 
        plt.ylabel('Cumulative Profit ($)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_trends.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        # 3. Action frequency and accuracy
        action_stats = self._analyze_actions(hands)
        
        plt.figure(figsize=(10, 6))
        
        actions = list(action_stats.keys())
        counts = [action_stats[a]['count'] for a in actions]
        accuracies = [action_stats[a]['accuracy'] for a in actions]
        
        x = range(len(actions))
        
        plt.subplot(1, 2, 1)
        plt.bar(x, counts)
        plt.title('Action Frequency')
        plt.xlabel('Action')
        plt.ylabel('Count')
        plt.xticks(x, actions, rotation=45)
        
        plt.subplot(1, 2, 2)
        plt.bar(x, accuracies)
        plt.title('ML Accuracy by Action')
        plt.xlabel('Action')
        plt.ylabel('Accuracy')
        plt.xticks(x, actions, rotation=45)
        plt.ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/action_analysis.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Visualizations saved to: {output_dir}/")

def main():
    """Main entry point for batch analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch analyze recorded blackjack shoes')
    parser.add_argument('--pattern', default='shoe_*.json', 
                       help='File pattern for shoe files (default: shoe_*.json)')
    parser.add_argument('--report', default='batch_analysis_report.txt',
                       help='Output report file (default: batch_analysis_report.txt)')
    parser.add_argument('--plots', default='analysis_plots',
                       help='Output directory for plots (default: analysis_plots)')
    parser.add_argument('--no-plots', action='store_true',
                       help='Skip generating plots')
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = BatchAnalyzer()
        
        # Load shoes
        shoes = analyzer.load_all_shoes(args.pattern)
        if not shoes:
            print("❌ No shoes found. Record some shoes first with record_live_shoe.py")
            return
        
        # Analyze
        analysis = analyzer.analyze_all_shoes(shoes)
        
        # Generate report
        analyzer.generate_report(analysis, args.report)
        
        # Generate plots
        if not args.no_plots:
            try:
                analyzer.create_visualizations(analysis, args.plots)
            except ImportError:
                print("⚠️  matplotlib not available. Skipping plots.")
            except Exception as e:
                print(f"⚠️  Error creating plots: {e}")
        
        # Print summary
        overview = analysis['overview']
        stats = analysis['combined_stats']
        
        print(f"\n📊 ANALYSIS COMPLETE")
        print(f"=" * 30)
        print(f"Shoes: {overview['total_shoes']}")
        print(f"Hands: {overview['total_hands']}")
        print(f"Profit: ${overview['total_profit']:+.2f}")
        print(f"ML Accuracy: {stats['prediction_accuracy']:.1%}")
        print(f"Report: {args.report}")
        
    except FileNotFoundError:
        print("❌ ML model not found. Please train the model first:")
        print("   python data_generator.py")
        print("   python ml_model.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
