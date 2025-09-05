"""
Complete Training Pipeline
========================
Run this script to generate data, train model, and test inference.
"""

import os
import sys
import time
from datetime import datetime

def main():
    """Run complete training pipeline."""
    
    print("🃏 Blackjack EV ML Training Pipeline")
    print("=====================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Generate training data
    print("\n📊 Step 1: Generating training data...")
    print("-" * 40)
    
    try:
        from data_generator import BlackjackDataGenerator
        
        generator = BlackjackDataGenerator()
        df = generator.generate_training_data(num_samples=25000)
        
        # Save data
        df.to_csv('blackjack_training_data.csv', index=False)
        print(f"✅ Generated {len(df)} samples with {len(df.columns)} features")
        print(f"💾 Saved to: blackjack_training_data.csv")
        
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False
    
    # Step 2: Train model
    print("\n🧠 Step 2: Training neural network...")
    print("-" * 40)
    
    try:
        from ml_model import BlackjackEVPredictor
        
        predictor = BlackjackEVPredictor()
        
        # Train with reasonable settings
        history = predictor.train(
            df, 
            epochs=50,
            batch_size=256,
            test_size=0.2
        )
        
        # Save model
        predictor.save_model('blackjack_ev_model')
        print("✅ Model training completed")
        print("💾 Model saved to: blackjack_ev_model.*")
        
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        return False
    
    # Step 3: Test inference
    print("\n🎯 Step 3: Testing inference engine...")
    print("-" * 40)
    
    try:
        from inference_engine import BlackjackInferenceEngine
        
        engine = BlackjackInferenceEngine()
        
        # Test prediction
        test_result = engine.predict(
            player_total=16,
            dealer_upcard='10',
            is_soft=False,
            is_pair=False
        )
        
        print("✅ Inference engine working")
        print(f"🧪 Test prediction: {test_result}")
        
    except Exception as e:
        print(f"❌ Inference test failed: {e}")
        return False
    
    # Success summary
    print("\n🎉 Training Pipeline Completed Successfully!")
    print("=" * 50)
    print("Files created:")
    print("📄 blackjack_training_data.csv - Training dataset")
    print("🧠 blackjack_ev_model.h5 - Trained neural network")
    print("⚙️  blackjack_ev_model_scaler.pkl - Feature scaler")
    print("📋 blackjack_ev_model_metadata.json - Model metadata")
    print("📊 training_history.png - Training curves")
    print("📈 prediction_scatter.png - Prediction analysis")
    
    print(f"\n⏱️  Total time: {time.time() - start_time:.1f} seconds")
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🚀 Next steps:")
    print("1. Run 'python inference_engine.py' for demo")
    print("2. Import BlackjackInferenceEngine in your code")
    print("3. Experiment with different hand scenarios")
    
    return True

if __name__ == "__main__":
    start_time = time.time()
    
    # Check dependencies
    try:
        import numpy, pandas, tensorflow, sklearn
        print("✅ All dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run pipeline
    success = main()
    
    if not success:
        print("\n❌ Pipeline failed. Check error messages above.")
        sys.exit(1)
    else:
        print("\n✅ All systems ready for blackjack EV prediction!")
        sys.exit(0)
