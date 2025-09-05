"""
Blackjack EV Machine Learning Model
==================================
Neural network model to predict Expected Values for blackjack hands
based on shoe composition, card sequences, and hand configuration.
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import joblib
import json

class BlackjackEVPredictor:
    """Machine Learning model for predicting blackjack Expected Values."""
    
    def __init__(self):
        self.feature_scaler = StandardScaler()
        self.action_encoder = LabelEncoder()
        self.model = None
        self.feature_columns = None
        self.target_columns = None
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare data for training."""
        # Identify feature and target columns
        target_cols = [col for col in df.columns if col.endswith('_ev')]
        action_col = 'optimal_action' if 'optimal_action' in df.columns else None
        
        # Feature columns (everything except targets)
        feature_cols = [col for col in df.columns if col not in target_cols and col != action_col and col != 'optimal_ev']
        
        print(f"Feature columns: {len(feature_cols)}")
        print(f"Target columns: {target_cols}")
        
        # Prepare features
        X = df[feature_cols].fillna(0).values
        
        # Prepare targets (EVs for each action)
        y_ev = df[target_cols].fillna(0).values
        
        # Store column information
        self.feature_columns = feature_cols
        self.target_columns = target_cols
        
        return X, y_ev, feature_cols
    
    def build_model(self, input_dim: int, output_dim: int) -> keras.Model:
        """Build neural network architecture."""
        
        # Input layer
        inputs = keras.Input(shape=(input_dim,), name='features')
        
        # Feature extraction layers
        x = layers.Dense(512, activation='relu', name='dense_1')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(256, activation='relu', name='dense_2')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(128, activation='relu', name='dense_3')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        
        x = layers.Dense(64, activation='relu', name='dense_4')(x)
        x = layers.Dropout(0.1)(x)
        
        # Output layer for EV prediction
        ev_outputs = layers.Dense(output_dim, activation='linear', name='ev_prediction')(x)
        
        # Create model
        model = keras.Model(inputs=inputs, outputs=ev_outputs, name='blackjack_ev_predictor')
        
        return model
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2, epochs: int = 100, batch_size: int = 256):
        """Train the model."""
        print("Preparing data...")
        X, y, feature_cols = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=None
        )
        
        print(f"Training set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        # Scale features
        X_train_scaled = self.feature_scaler.fit_transform(X_train)
        X_test_scaled = self.feature_scaler.transform(X_test)
        
        # Build model
        print("Building model...")
        self.model = self.build_model(input_dim=X_train.shape[1], output_dim=y_train.shape[1])
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        # Print model summary
        print(self.model.summary())
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss', 
                patience=15, 
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', 
                factor=0.5, 
                patience=10, 
                min_lr=1e-6
            ),
            keras.callbacks.ModelCheckpoint(
                'best_model.h5',
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=False
            )
        ]
        
        # Train model
        print("Training model...")
        history = self.model.fit(
            X_train_scaled, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_test_scaled, y_test),
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate
        print("Evaluating model...")
        train_loss, train_mae = self.model.evaluate(X_train_scaled, y_train, verbose=0)
        test_loss, test_mae = self.model.evaluate(X_test_scaled, y_test, verbose=0)
        
        print(f"Training - Loss: {train_loss:.4f}, MAE: {train_mae:.4f}")
        print(f"Test - Loss: {test_loss:.4f}, MAE: {test_mae:.4f}")
        
        # Plot training history
        self.plot_training_history(history)
        
        # Detailed evaluation
        self.evaluate_predictions(X_test_scaled, y_test)
        
        return history
    
    def plot_training_history(self, history):
        """Plot training curves."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Loss
        ax1.plot(history.history['loss'], label='Training Loss')
        ax1.plot(history.history['val_loss'], label='Validation Loss')
        ax1.set_title('Model Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # MAE
        ax2.plot(history.history['mae'], label='Training MAE')
        ax2.plot(history.history['val_mae'], label='Validation MAE')
        ax2.set_title('Model MAE')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Mean Absolute Error')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def evaluate_predictions(self, X_test: np.ndarray, y_test: np.ndarray):
        """Detailed evaluation of model predictions."""
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics for each action
        action_metrics = {}
        for i, action in enumerate(self.target_columns):
            mse = mean_squared_error(y_test[:, i], y_pred[:, i])
            mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
            action_metrics[action] = {'MSE': mse, 'MAE': mae}
            print(f"{action}: MSE={mse:.4f}, MAE={mae:.4f}")
        
        # Plot predictions vs actual for each action
        n_actions = len(self.target_columns)
        fig, axes = plt.subplots(2, (n_actions + 1) // 2, figsize=(15, 10))
        axes = axes.flatten() if n_actions > 1 else [axes]
        
        for i, action in enumerate(self.target_columns):
            if i < len(axes):
                axes[i].scatter(y_test[:, i], y_pred[:, i], alpha=0.5, s=1)
                axes[i].plot([-1, 1], [-1, 1], 'r--', lw=2)
                axes[i].set_xlabel(f'Actual {action}')
                axes[i].set_ylabel(f'Predicted {action}')
                axes[i].set_title(f'{action} Predictions')
                axes[i].grid(True)
        
        # Hide unused subplots
        for i in range(n_actions, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        plt.savefig('prediction_scatter.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return action_metrics
    
    def predict_ev(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Predict EVs for a given hand configuration."""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert features to array
        feature_array = np.array([[features.get(col, 0) for col in self.feature_columns]])
        
        # Scale features
        feature_array_scaled = self.feature_scaler.transform(feature_array)
        
        # Predict
        predictions = self.model.predict(feature_array_scaled, verbose=0)[0]
        
        # Return as dictionary
        result = {}
        for i, action in enumerate(self.target_columns):
            action_name = action.replace('_ev', '')
            result[action_name] = float(predictions[i])
        
        # Find optimal action
        if result:
            optimal_action = max(result.keys(), key=lambda k: result[k])
            result['optimal_action'] = optimal_action
            result['optimal_ev'] = result[optimal_action]
        
        return result
    
    def save_model(self, model_path: str = 'blackjack_ev_model'):
        """Save the trained model and preprocessors."""
        if self.model is None:
            raise ValueError("No model to save!")
        
        # Save Keras model
        self.model.save(f'{model_path}.h5')
        
        # Save preprocessors
        joblib.dump(self.feature_scaler, f'{model_path}_scaler.pkl')
        
        # Save metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'target_columns': self.target_columns
        }
        with open(f'{model_path}_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {model_path}.h5")
    
    def load_model(self, model_path: str = 'blackjack_ev_model'):
        """Load a trained model and preprocessors."""
        # Load Keras model
        self.model = keras.models.load_model(f'{model_path}.h5')
        
        # Load preprocessors
        self.feature_scaler = joblib.load(f'{model_path}_scaler.pkl')
        
        # Load metadata
        with open(f'{model_path}_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        self.feature_columns = metadata['feature_columns']
        self.target_columns = metadata['target_columns']
        
        print(f"Model loaded from {model_path}.h5")

class SequenceBasedEVPredictor(BlackjackEVPredictor):
    """Enhanced model that uses LSTM for sequence modeling."""
    
    def build_model(self, input_dim: int, output_dim: int) -> keras.Model:
        """Build enhanced model with sequence processing."""
        
        # Main features input
        main_input = keras.Input(shape=(input_dim,), name='main_features')
        
        # Extract sequence features (recent cards)
        # Assuming we have 8 recent cards * 13 ranks = 104 sequence features
        sequence_features = 8 * 13  # recent_0_2, recent_0_3, ..., recent_7_A
        
        if input_dim >= sequence_features:
            # Separate sequence and non-sequence features
            sequence_input = layers.Lambda(lambda x: x[:, :sequence_features])(main_input)
            other_input = layers.Lambda(lambda x: x[:, sequence_features:])(main_input)
            
            # Reshape sequence input for LSTM (batch, timesteps, features)
            sequence_reshaped = layers.Reshape((8, 13))(sequence_input)
            
            # LSTM for sequence processing
            lstm_out = layers.LSTM(32, return_sequences=False)(sequence_reshaped)
            lstm_out = layers.Dropout(0.2)(lstm_out)
            
            # Combine sequence and other features
            combined = layers.Concatenate()([lstm_out, other_input])
        else:
            combined = main_input
        
        # Dense layers
        x = layers.Dense(256, activation='relu')(combined)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(128, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.1)(x)
        
        # Output
        ev_outputs = layers.Dense(output_dim, activation='linear', name='ev_prediction')(x)
        
        model = keras.Model(inputs=main_input, outputs=ev_outputs, name='sequence_ev_predictor')
        
        return model

if __name__ == "__main__":
    # Load training data
    print("Loading training data...")
    df = pd.read_csv('blackjack_training_data.csv')
    
    print(f"Loaded {len(df)} samples with {len(df.columns)} columns")
    
    # Initialize and train model
    print("Initializing model...")
    predictor = BlackjackEVPredictor()
    
    # Train model
    history = predictor.train(df, epochs=50, batch_size=256)
    
    # Save model
    predictor.save_model('blackjack_ev_model')
    
    # Test prediction
    print("\nTesting prediction...")
    sample_features = df.iloc[0].drop([col for col in df.columns if col.endswith('_ev') or col in ['optimal_action', 'optimal_ev']]).to_dict()
    
    prediction = predictor.predict_ev(sample_features)
    print("Sample prediction:", prediction)
    
    print("\nTraining completed!")
