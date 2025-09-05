"""
Batch Training Data Generator
===========================
Generates training data in resumable batches to avoid losing progress.
"""

import os
import pandas as pd
import json
from enhanced_data_generator import EnhancedBlackjackDataGenerator
from tqdm import tqdm

class BatchDataGenerator:
    """Generate training data in resumable batches."""
    
    def __init__(self, batch_size: int = 10000):
        self.batch_size = batch_size
        self.generator = EnhancedBlackjackDataGenerator()
        self.progress_file = "analysis/data/generation_progress.json"
        self.batch_dir = "analysis/data/batches/"
        
        # Create directories
        os.makedirs(self.batch_dir, exist_ok=True)
        os.makedirs("analysis/data", exist_ok=True)
    
    def save_progress(self, batch_num: int, total_target: int):
        """Save generation progress."""
        progress = {
            "batch_num": batch_num,
            "total_target": total_target,
            "samples_completed": batch_num * self.batch_size,
            "batch_size": self.batch_size
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def load_progress(self):
        """Load previous progress if exists."""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return None
    
    def generate_batches(self, total_samples: int):
        """Generate training data in batches."""
        
        print(f"🚀 Batch Training Data Generator")
        print(f"📊 Target: {total_samples:,} samples")
        print(f"📦 Batch size: {self.batch_size:,} samples")
        
        # Check for existing progress
        progress = self.load_progress()
        start_batch = 0
        
        if progress and progress["total_target"] == total_samples:
            start_batch = progress["batch_num"]
            print(f"🔄 Resuming from batch {start_batch}")
            print(f"✅ Already completed: {progress['samples_completed']:,} samples")
        
        total_batches = (total_samples + self.batch_size - 1) // self.batch_size
        
        for batch_num in range(start_batch, total_batches):
            
            # Calculate samples for this batch
            remaining_samples = total_samples - (batch_num * self.batch_size)
            current_batch_size = min(self.batch_size, remaining_samples)
            
            print(f"\n📦 Generating batch {batch_num + 1}/{total_batches}")
            print(f"   🎯 Samples in this batch: {current_batch_size:,}")
            
            # Generate batch
            try:
                df_batch = self.generator.generate_enhanced_training_data(
                    num_samples=current_batch_size
                )
                
                # Save batch
                batch_file = f"{self.batch_dir}batch_{batch_num:03d}.csv"
                df_batch.to_csv(batch_file, index=False)
                
                print(f"   ✅ Saved: {batch_file}")
                print(f"   📈 Features: {len(df_batch.columns)}")
                
                # Save progress
                self.save_progress(batch_num + 1, total_samples)
                
                # Show overall progress
                completed_samples = (batch_num + 1) * self.batch_size
                if completed_samples > total_samples:
                    completed_samples = total_samples
                    
                progress_pct = (completed_samples / total_samples) * 100
                print(f"   🎯 Overall progress: {completed_samples:,}/{total_samples:,} ({progress_pct:.1f}%)")
                
            except KeyboardInterrupt:
                print(f"\n⏹️  Interrupted after batch {batch_num}")
                print(f"✅ Progress saved. Resume with same command.")
                return None
            except Exception as e:
                print(f"❌ Error in batch {batch_num}: {e}")
                continue
        
        print(f"\n🎉 All batches complete!")
        return self.combine_batches(total_samples)
    
    def combine_batches(self, total_samples: int):
        """Combine all batch files into final dataset."""
        
        print(f"\n🔗 Combining batches into final dataset...")
        
        batch_files = sorted([f for f in os.listdir(self.batch_dir) if f.endswith('.csv')])
        
        if not batch_files:
            print("❌ No batch files found!")
            return None
        
        # Combine all batches
        combined_data = []
        total_rows = 0
        
        for batch_file in tqdm(batch_files, desc="Combining batches"):
            batch_path = os.path.join(self.batch_dir, batch_file)
            df_batch = pd.read_csv(batch_path)
            combined_data.append(df_batch)
            total_rows += len(df_batch)
        
        # Create final dataset
        df_final = pd.concat(combined_data, ignore_index=True)
        
        # Save final dataset
        final_file = f"analysis/data/blackjack_training_data_enhanced_{total_samples//1000}k.csv"
        df_final.to_csv(final_file, index=False)
        
        print(f"✅ Final dataset created!")
        print(f"   📊 Total samples: {len(df_final):,}")
        print(f"   📈 Total features: {len(df_final.columns)}")
        print(f"   💾 Saved to: {final_file}")
        
        # Clean up progress file
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        
        # Optionally clean up batch files
        cleanup = input("\n🗑️  Delete batch files? (y/n): ").lower().strip() == 'y'
        if cleanup:
            for batch_file in batch_files:
                os.remove(os.path.join(self.batch_dir, batch_file))
            print("✅ Batch files cleaned up")
        
        return df_final


def main():
    """Main batch generation function."""
    
    print("🚀 Resumable Batch Training Data Generator")
    print("=" * 50)
    
    # Get target samples
    total_samples = int(input("Enter total samples (e.g., 100000, 500000): ") or "100000")
    batch_size = int(input("Enter batch size (e.g., 10000): ") or "10000")
    
    generator = BatchDataGenerator(batch_size=batch_size)
    
    print(f"\n📋 Configuration:")
    print(f"   🎯 Total samples: {total_samples:,}")
    print(f"   📦 Batch size: {batch_size:,}")
    print(f"   🔄 Resumable: Yes")
    print(f"   ⏹️  Safe to interrupt: Yes (Ctrl+C)")
    
    # Generate data
    df_final = generator.generate_batches(total_samples)
    
    if df_final is not None:
        print(f"\n🎉 Training data generation complete!")
        print(f"Ready to train enhanced ML model with {len(df_final):,} samples!")


if __name__ == "__main__":
    main()
