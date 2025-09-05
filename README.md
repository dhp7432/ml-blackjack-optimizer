# 🃏 Advanced Blackjack ML System

A comprehensive machine learning system for blackjack Expected Value (EV) prediction and card pattern analysis, featuring real-time GUI, advanced data generation, and neural network models.

## 🎯 Features

### 🎮 Interactive GUI
- **Real-time card counting** with Hi-Lo system
- **Monte Carlo EV simulation** for optimal decision making
- **Card flow recording** with placeholder system for dealer hidden cards
- **Shoe pattern analysis** with penetration tracking
- **Advanced statistics** including count volatility and extremes

### 🧠 Machine Learning Models
- **Deep Neural Networks** (512→256→128→64 architecture)
- **LSTM sequence modeling** for card order dependencies
- **Enhanced feature engineering** (165+ features)
- **Batch training system** for massive datasets (500K+ samples)
- **Real shoe data integration** for validation

### 📊 Advanced Data Generation
- **Monte Carlo ground truth** with 8,000+ trials per sample
- **Diverse shoe states** with multiple penetration levels
- **Pattern detection features** (clumping, alternating, streaks)
- **Count volatility tracking** and bias analysis
- **Resumable batch generation** to prevent data loss

## 🚀 Quick Start

### 1. Launch the GUI
```bash
python3 gui/blackjack_counter_gui.py
```

### 2. Generate Training Data
```bash
# For massive dataset (resumable)
python3 blackjack_ev_ml/batch_data_generator.py

# For quick testing
python3 blackjack_ev_ml/enhanced_data_generator.py
```

### 3. Train ML Model
```bash
python3 blackjack_ev_ml/run_training.py
```

## 📁 Project Structure

```
📦 Advanced Blackjack ML System
├── 🎮 gui/
│   ├── blackjack_counter_gui.py     # Main GUI application
│   └── demo_enhanced_gui.py         # GUI feature demos
├── 🧠 blackjack_ev_ml/              # Advanced ML System
│   ├── ml_model.py                  # Neural network architectures
│   ├── data_generator.py            # Base training data generation
│   ├── enhanced_data_generator.py   # Enhanced features (165+)
│   ├── batch_data_generator.py      # Resumable batch generation
│   ├── inference_engine.py          # Real-time ML inference
│   └── run_training.py              # Model training pipeline
├── 🎯 core/
│   └── blackjack_card_counter.py    # Core counting & simulation logic
├── 📊 analysis/
│   └── data/                        # Training datasets
├── 🃏 recorded_shoes/               # Real casino shoe recordings
├── 📖 docs/                         # Documentation
└── 🔧 examples/                     # Usage examples
```

## 🎯 Key Capabilities

### Pattern Detection
- **Clumping Analysis**: Detect when cards cluster vs random distribution
- **Alternating Patterns**: Identify high-low-high-low sequences
- **Streak Detection**: Track consecutive high/low card runs
- **Dealer Bias**: Analyze dealer-favorable card sequences

### Advanced Features
- **Count Volatility**: Track extreme swings in running count
- **Penetration-Adjusted Counts**: Weight decisions by shoe depth
- **30% Rule**: Pattern analysis becomes significant after 30% penetration
- **Hidden Card System**: Maintain chronological accuracy with `+` placeholders

### Real-Time Analysis
- **Monte Carlo EV**: 10,000+ trial simulations for ground truth
- **Neural Network Predictions**: <50ms inference for real-time play
- **Multi-Action Support**: Hit, Stand, Double, Split EVs
- **Composition-Dependent**: Accounts for exact remaining cards

## 📈 Training Data

### Current Dataset
- **25,000 samples** with Monte Carlo ground truth
- **150+ features** including sequence patterns
- **All game scenarios** from basic strategy to extreme counts

### Enhanced Dataset
- **500,000+ samples** with advanced diversity
- **165+ features** including pattern detection
- **Edge case coverage** for difficult decisions
- **Real shoe integration** for validation

## 🛠️ Technical Specifications

### Neural Network Architecture
```python
Input (165+ features)
   ↓
Dense(512) + BatchNorm + Dropout(0.3)
   ↓
Dense(256) + BatchNorm + Dropout(0.3)
   ↓
Dense(128) + BatchNorm + Dropout(0.2)
   ↓
Dense(64) + Dropout(0.1)
   ↓
Output(4 actions: Hit, Stand, Double, Split)
```

### LSTM Sequence Model
```python
Sequence Features → Reshape(8,13) → LSTM(32) → Dropout(0.2)
   ↓                                              ↓
Other Features ────────────────────→ Concatenate
                                          ↓
                                    Dense Layers
                                          ↓
                                       Output
```

## 🎮 GUI Usage

### Card Flow Recording
1. Click **"Start Recording"** in Card Counter tab
2. Enter cards as dealt: `8 J K Q A 6 7 4 5`
3. Use `+` for dealer hidden cards
4. Use `CARD+` (e.g., `5+`) when revealed
5. Click **"New Shoe"** to auto-save and start fresh

### Real-Time Analysis
- **Running Count**: Hi-Lo system tracking
- **True Count**: Adjusted for remaining decks
- **EV Analysis**: Optimal move with Monte Carlo simulation
- **Pattern Stats**: Clumping, alternating, streaks

## 📊 Performance Metrics

- **Prediction Speed**: <50ms per hand
- **Training Accuracy**: 95%+ optimal action matching
- **Mean Absolute Error**: ~0.02-0.05 EV units
- **Real-Time GUI**: Smooth 60fps interface

## 🔬 Research Applications

### Card Pattern Analysis
- Validate traditional counting systems
- Discover new exploitable patterns
- Analyze penetration effects on pattern significance
- Compare casino vs theoretical distributions

### Strategy Optimization
- Composition-dependent basic strategy
- Count-adjusted index numbers
- Sequence-aware betting strategies
- Real-time adaptation algorithms

## 🚀 Future Enhancements

- **Attention mechanisms** for advanced pattern recognition
- **Ensemble methods** combining multiple model types
- **Real-time casino integration** via computer vision
- **Multi-deck composition tracking** for shoe games
- **Advanced betting strategy** ML models

## 📝 Requirements

```
Python 3.7+
tensorflow>=2.8.0
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
tkinter (built-in)
tqdm>=4.62.0
matplotlib>=3.5.0
```

## 🤝 Contributing

This is an active research project combining:
- **Traditional card counting** methods
- **Modern machine learning** techniques  
- **Real casino data** validation
- **Pattern detection** algorithms

## 📄 License

Research and educational use. Advanced blackjack ML system for pattern analysis and EV optimization.

---

**🎯 Built for serious blackjack analysis and ML research**
