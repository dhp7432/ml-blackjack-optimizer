#!/usr/bin/env python3
"""
Blackjack Card Counter & Strategy Advisor
Main entry point for the application.
"""

import tkinter as tk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.blackjack_counter_gui import BlackjackCounterGUI

def main():
    """Main entry point for the Blackjack Card Counter application."""
    # Create the main window
    root = tk.Tk()
    
    # Initialize the GUI application
    app = BlackjackCounterGUI(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
