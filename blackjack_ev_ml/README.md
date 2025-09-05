# Blackjack Expected Value Machine Learning Model

A complete machine learning system to predict Expected Values (EV) for blackjack hands based on shoe composition, card sequences, and hand configuration.

## 🎯 Overview

This project trains a neural network to predict optimal Expected Values for blackjack decisions, going beyond traditional basic strategy by incorporating:

- **Real-time shoe composition** (remaining cards)
- **Card sequence patterns** (order of recent cards)
- **Count information** (Hi-Lo running/true count)
- **Positional context** (penetration level, cards dealt)

## 🚀 Key Features

### Data Generation
- **Monte Carlo simulation** for ground truth EV calculation
- **Comprehensive feature extraction** (150+ features)
- **Sequence modeling** of last 8 cards dealt
- **Composition-dependent analysis** using actual shoe state

### Machine Learning Model
- **Deep Neural Network** with 512→256→128→64 architecture
- **Sequence-aware variant** with LSTM for card order modeling
- **Multi-output regression** predicting EV for all actions
- **Advanced regularization** (BatchNorm, Dropout, Early Stopping)

### Production Inference
- **Real-time prediction** engine
- **Batch processing** for multiple hands
- **Basic strategy comparison** 
- **Feature preprocessing** pipeline

## 📊 Training Data Features

### Core Hand Features (4)
- `player_total` (2-21)
- `dealer_upcard_value` (2-11) 
- `is_soft` (boolean)
- `is_pair` (boolean)

### Shoe Composition (26)
- Individual card counts (normalized): `count_2`, `count_3`, ..., `count_A`
- Dealer upcard one-hot: `dealer_2`, `dealer_3`, ..., `dealer_A`

### Count Information (5)
- `running_count` (-50 to +50)
- `true_count` (-10 to +10)
- `remaining_cards` (52-416)
- `remaining_decks` (1.0-8.0)
- `penetration` (0.0-1.0)

### Card Sequence Features (104)
- Recent 8 cards one-hot encoded: `recent_0_2`, `recent_0_3`, ..., `recent_7_A`
- Pattern recognition: `recent_high_ratio`, `recent_low_ratio`, `recent_neutral_ratio`
- Streak detection: `recent_streak_high`, `recent_streak_low`

### Composition Analysis (6)
- Group totals: `remaining_low_total`, `remaining_neutral_total`, `remaining_high_total`
- Ratios: `low_ratio`, `neutral_ratio`, `high_ratio`

### Target Variables
- `hit_ev`, `stand_ev`, `double_ev`, `split_ev` (when applicable)
- `optimal_action` (categorical)
- `optimal_ev` (best available EV)

## 🛠️ Installation

```bash
# Create virtual environment
python -m venv blackjack_ml_env
source blackjack_ml_env/bin/activate  # Windows: blackjack_ml_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📈 Usage

### 1. Generate Training Data
```bash
python data_generator.py
```
Creates `blackjack_training_data.csv` with 25,000 samples by default.

### 2. Train Model
```bash
python ml_model.py
```
Trains neural network and saves model files:
- `blackjack_ev_model.h5` (Keras model)
- `blackjack_ev_model_scaler.pkl` (feature scaler)
- `blackjack_ev_model_metadata.json` (column info)

### 3. Run Inference
```bash
python inference_engine.py
```
Demonstrates real-time EV prediction on test hands.

## 🔍 Example Usage

```python
from inference_engine import BlackjackInferenceEngine

# Load trained model
engine = BlackjackInferenceEngine()

# Predict EVs for a hand
result = engine.predict(
    player_total=16,
    dealer_upcard='10',
    is_soft=False,
    is_pair=False,
    card_counts={'2': 28, '3': 31, '4': 32, ...},  # Current shoe state
    cards_dealt=['K', '7', 'A', '5', 'Q', '2'],    # Recent cards
    num_decks=8
)

print(result)
# Output:
# {
#   'hit': -0.5423,
#   'stand': -0.5401, 
#   'optimal_action': 'stand',
#   'optimal_ev': -0.5401
# }
```

## 📊 Model Performance

Expected performance metrics:
- **MAE**: ~0.02-0.05 (Mean Absolute Error)
- **MSE**: ~0.001-0.01 (Mean Squared Error)
- **Action Accuracy**: ~85-95% match with optimal play

## 🧠 Model Architecture

### Standard Model
```
Input (150+ features)
   ↓
Dense(512) + BatchNorm + Dropout(0.3)
   ↓
Dense(256) + BatchNorm + Dropout(0.3)
   ↓
Dense(128) + BatchNorm + Dropout(0.2)
   ↓
Dense(64) + Dropout(0.1)
   ↓
Output(2-4 actions)
```

### Sequence-Enhanced Model
```
Input Features
   ↓
[Sequence Features] → Reshape(8,13) → LSTM(32) → Dropout(0.2)
   ↓                                              ↓
[Other Features] ────────────────────→ Concatenate
                                          ↓
                                    Dense Layers
                                          ↓
                                       Output
```

## 🎲 Monte Carlo Simulation

Ground truth EVs generated using:
- **10,000 trials** per hand configuration
- **Full game simulation** (player strategy + dealer play)
- **Composition-dependent** card drawing
- **Proper rule modeling** (S17, no DAS, no surrender)

## 🔧 Customization

### Adjust Training Parameters
```python
# In ml_model.py
history = predictor.train(
    df, 
    epochs=100,        # Training epochs
    batch_size=256,    # Batch size
    test_size=0.2      # Train/test split
)
```

### Modify Feature Sets
```python
# In data_generator.py
def extract_features(self):
    # Add custom features
    features['custom_feature'] = custom_calculation()
    return features
```

### Change Model Architecture
```python
# In ml_model.py
def build_model(self, input_dim, output_dim):
    # Modify network architecture
    x = layers.Dense(1024, activation='relu')(inputs)  # Larger layer
    # ... add more layers
```

## 🎯 Applications

1. **Advanced Card Counting**: Supplement Hi-Lo with ML predictions
2. **Strategy Optimization**: Fine-tune play based on exact shoe composition
3. **Educational Tool**: Understand EV differences between actions
4. **Research Platform**: Analyze blackjack mathematics
5. **Casino Analysis**: Study game profitability under various conditions

## 📝 Technical Notes

### Why This Approach Works
- **Composition Dependency**: ML captures removal effects ignored by basic strategy
- **Sequence Patterns**: Learns short-term card clumping and flow patterns  
- **Count Integration**: Incorporates Hi-Lo information with other factors
- **Non-linear Modeling**: Neural networks capture complex interactions

### Limitations
- **Training Data Quality**: Limited by Monte Carlo simulation accuracy
- **Generalization**: May not adapt well to different rule variations
- **Computational Cost**: More expensive than lookup tables
- **Overfitting Risk**: Complex model may memorize training patterns

## 🔮 Future Enhancements

1. **Multi-Rule Training**: Train on various casino rule sets
2. **Count System Integration**: Support KO, Omega II, etc.
3. **Bankroll Management**: Integrate Kelly Criterion betting
4. **Real-time Adaptation**: Online learning from actual play
5. **Ensemble Methods**: Combine multiple model types
6. **Shuffle Tracking**: Model non-random card distributions

## 📚 References

- Professional Blackjack by Stanford Wong
- The Theory of Blackjack by Peter Griffin  
- Wizard of Odds (WizardOfOdds.com)
- Blackjack Bluebook II by Fred Renzey

## ⚖️ Legal Notice

This software is for **educational and research purposes only**. Users are responsible for compliance with local laws and casino policies. The authors do not encourage or endorse gambling.

---

**Built with ❤️ for the blackjack mathematics community**
