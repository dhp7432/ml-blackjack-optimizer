"""
Demo script for Enhanced Blackjack Counter GUI with Shoe Recording
================================================================
This script demonstrates the new shoe recording functionality integrated into the GUI.
"""

import sys
import os

def demo_features():
    """Display information about the enhanced GUI features."""
    print("🎰 Enhanced Blackjack Counter GUI")
    print("="*50)
    print()
    
    print("🚀 NEW FEATURES ADDED:")
    print("• 🃏 Card Flow Recorder - automatic capture from Card Counter")
    print("• 📹 Simple recording controls in main tab")
    print("• 🎲 Auto-generated shoe IDs (no setup required)")
    print("• 📊 Live flow display and analysis")
    print("• 💾 Auto-save to JSON files")
    print("• 🔍 Pattern analysis and clustering detection")
    print()
    
    print("📋 HOW TO USE:")
    print("🃏 SIMPLIFIED CARD FLOW RECORDING:")
    print("1. Launch GUI: python blackjack_counter_gui.py")
    print("2. Click '📹 Start Recording' (Card Counter OR Card Flow tab)")
    print("3. Deal cards normally (type/click cards as usual)")
    print("4. Cards automatically recorded: 9 9 10 J K A 2 7...")
    print("5. Switch to '🃏 Card Flow' tab to see live sequence")
    print("6. Click '⏹️ Stop Recording' when done (OR use 🔄 New Shoe)")
    print("7. Auto-saves as: shoe_SHOE_12345_timestamp.json")
    print()
    print("🔄 SMART SHOE MANAGEMENT:")
    print("• Click '🔄 New Shoe' → Auto-saves current recording")
    print("• Automatically starts fresh shoe with new random ID")
    print("• No data loss - previous shoe safely saved")
    print()
    print("📂 CARD FLOW TAB FEATURES:")
    print("• 📹 Start Recording - Same as Card Counter tab")
    print("• 📂 Load Previous Shoe - View any saved shoe")
    print("• 🗑️ Clear Display - Reset without saving")
    print("• ⏹️ Stop Recording - Save current shoe")
    print()
    print("✨ KEY BENEFITS:")
    print("• No setup required - just click Start Recording")
    print("• Auto-generates random shoe ID (SHOE_12345)")
    print("• Auto-save on shoe reset - never lose data")
    print("• Recording controls on both tabs")
    print("• Perfect sequence for ML analysis: 9 9 10 J K A 2 7 9 6...")
    print()
    
    print("🎯 ANALYSIS FEATURES:")
    print("• ML prediction accuracy")
    print("• Expected value comparisons")
    print("• Hand-by-hand breakdown")
    print("• Common disagreement patterns")
    print("• Performance improvement suggestions")
    print("• Card clustering detection")
    print("• Count progression tracking")
    print("• Pattern recognition (high/low/neutral)")
    print("• Real-time penetration monitoring")
    print()
    
    print("💡 BENEFITS:")
    print("• Track real casino performance")
    print("• Learn from ML recommendations")
    print("• Improve decision-making")
    print("• Validate counting strategies")
    print("• Analyze composition-dependent effects")
    print()
    
    print("📁 FILE OUTPUTS:")
    print("• Shoe data saved as JSON files")
    print("• Analysis reports in GUI")
    print("• Batch analysis of multiple shoes")
    print()
    
    print("🔧 REQUIREMENTS:")
    if check_requirements():
        print("✅ All requirements met!")
    else:
        print("❌ Some requirements missing - see above")
    
    print()
    print("Ready to use! Launch with: python blackjack_counter_gui.py")

def check_requirements():
    """Check if all requirements are available."""
    all_good = True
    
    print("Checking requirements...")
    
    # Check core dependencies
    try:
        import tkinter
        print("✅ tkinter - GUI framework")
    except ImportError:
        print("❌ tkinter - Install Python tkinter support")
        all_good = False
    
    # Check blackjack counter
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core.blackjack_card_counter import BlackjackCardCounter
        print("✅ BlackjackCardCounter - Core counting logic")
    except ImportError:
        print("❌ BlackjackCardCounter - Check core module path")
        all_good = False
    
    # Check shoe recording
    try:
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blackjack_ev_ml'))
        from shoe_recorder import ShoeRecorder
        print("✅ ShoeRecorder - Recording functionality")
    except ImportError:
        print("⚠️  ShoeRecorder - Limited functionality (recording disabled)")
        # This is not critical for basic GUI operation
    
    return all_good

def run_gui():
    """Launch the enhanced GUI."""
    try:
        # Import and run the GUI
        from blackjack_counter_gui import main
        print("🚀 Launching Enhanced Blackjack Counter GUI...")
        main()
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        print("Make sure you're in the gui directory and all dependencies are installed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        run_gui()
    else:
        demo_features()
        
        print("\n" + "="*50)
        response = input("Launch GUI now? [y/n]: ").strip().lower()
        if response in ['y', 'yes', '']:
            run_gui()
