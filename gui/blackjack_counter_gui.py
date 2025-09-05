import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import json
import datetime
from typing import Dict, List, Any, Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.blackjack_card_counter import BlackjackCardCounter
import math

# Try to import shoe recording functionality
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'blackjack_ev_ml'))
    from shoe_recorder import ShoeRecorder, ShoeAnalyzer, HandRecord, ShoeRecord
    SHOE_RECORDING_AVAILABLE = True
except ImportError:
    SHOE_RECORDING_AVAILABLE = False
    print("Shoe recording functionality not available. Please ensure blackjack_ev_ml module is accessible.")

class ToolTip:
    """Create a tooltip for a given widget."""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None

    def enter(self, event=None):
        self.showtip()

    def leave(self, event=None):
        self.hidetip()

    def showtip(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Arial", "9", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class BlackjackCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Card Counter & Strategy Advisor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a4d3a')  # Dark green casino color
        
        # Initialize the counter
        self.counter = BlackjackCardCounter(8)
        
        # Initialize card flow recording
        self.flow_recording = False
        self.card_flow = []
        self.current_shoe_id = None
        self.max_running_count = 0
        self.min_running_count = 0
        self.max_true_count = 0.0
        self.min_true_count = 0.0
        
        # Configure style
        self.setup_styles()
        
        # Create the main interface
        self.create_widgets()
        
        # Update the display
        self.update_display()
    
    def setup_styles(self):
        """Configure ttk styles for a modern casino look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=('Arial', 24, 'bold'), 
                       foreground='#ffd700',  # Gold
                       background='#0a4d3a')
        
        style.configure('Count.TLabel', 
                       font=('Arial', 17, 'bold'), 
                       foreground='#ffffff',
                       background='#0a4d3a')
        
        style.configure('Value.TLabel', 
                       font=('Arial', 15, 'bold'), 
                       foreground='#00ff00',  # Bright green
                       background='#0a4d3a')
        
        style.configure('Recommendation.TLabel', 
                       font=('Arial', 12), 
                       foreground='#ffff00',  # Yellow
                       background='#0a4d3a')
        
        style.configure('Card.TButton', 
                       font=('Arial', 14, 'bold'),
                       padding=8)
        
        style.configure('Action.TButton', 
                       font=('Arial', 12, 'bold'),
                       padding=8)
        
        style.configure('Input.TLabel', 
                       font=('Arial', 13), 
                       foreground='#ffffff',
                       background='#0a4d3a')
        
        style.configure('Result.TLabel', 
                       font=('Arial', 14, 'bold'), 
                       foreground='#00ffff',  # Cyan for results
                       background='#0a4d3a')
    
    def create_widgets(self):
        """Create and arrange all GUI widgets."""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#0a4d3a')
        title_frame.pack(pady=10)
        
        title_label = ttk.Label(title_frame, 
                               text="🃏 Blackjack Card Counter 🃏", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Hi-Lo Counting System (8 Decks)", 
                                  style='Recommendation.TLabel')
        subtitle_label.pack()
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#0a4d3a')
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')
        
        # Tab 1: Card Counter
        counter_frame = tk.Frame(notebook, bg='#0a4d3a')
        notebook.add(counter_frame, text="Card Counter")
        
        # Tab 2: Hand Analysis
        analysis_frame = tk.Frame(notebook, bg='#0a4d3a')
        notebook.add(analysis_frame, text="Hand Analysis")
        
        # Tab 3: Card Flow Recording
        flow_frame = tk.Frame(notebook, bg='#0a4d3a')
        notebook.add(flow_frame, text="🃏 Card Flow")
        
        # Setup counter tab
        self.setup_counter_tab(counter_frame)
        
        # Setup analysis tab
        self.setup_analysis_tab(analysis_frame)
        
        # Setup card flow tab
        self.setup_card_flow_tab(flow_frame)
    
    def setup_counter_tab(self, parent):
        """Setup the card counter tab."""
        # Create main container with centered content
        container = tk.Frame(parent, bg='#0a4d3a')
        container.pack(expand=True, fill='both')
        
        # Center the content horizontally and vertically
        counter_main = tk.Frame(container, bg='#0a4d3a')
        counter_main.place(relx=0.5, rely=0.5, anchor='center')
        
        # Left side - Card buttons
        self.create_card_section(counter_main)
        
        # Right side - Count display and recommendations  
        self.create_display_section(counter_main)
        
        # Bottom - Action buttons at the very bottom of the container
        self.create_action_section(container)
    
    def setup_analysis_tab(self, parent):
        """Setup the hand analysis tab."""
        # Create main container with centered content
        container = tk.Frame(parent, bg='#0a4d3a')
        container.pack(expand=True, fill='both')
        
        # Center the content
        analysis_main = tk.Frame(container, bg='#0a4d3a')
        analysis_main.place(relx=0.5, rely=0.5, anchor='center')
        
        # Create left and right panels
        left_panel = tk.Frame(analysis_main, bg='#0a4d3a')
        left_panel.pack(side='left', fill='both', padx=(0, 20))
        
        right_panel = tk.Frame(analysis_main, bg='#0a4d3a')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Left panel: Input and Results sections
        self.create_hand_input_section(left_panel)
        self.create_hand_results_section(left_panel)
        
        # Right panel: Analysis content
        self.create_hand_analysis_content(right_panel)
    
    def create_hand_input_section(self, parent):
        """Create the hand analysis input section."""
        input_frame = tk.LabelFrame(parent, 
                                   text="Hand Analysis Input", 
                                   bg='#0a4d3a', 
                                   fg='#ffd700',
                                   font=('Arial', 14, 'bold'))
        input_frame.pack(fill='x', pady=(0, 10))
        
        # Create input grid
        input_grid = tk.Frame(input_frame, bg='#0a4d3a')
        input_grid.pack(padx=20, pady=15)
        
        # Player Total
        ttk.Label(input_grid, text="Player Total:", style='Input.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        self.player_total_var = tk.StringVar(value="17")
        player_total_spinbox = tk.Spinbox(input_grid, from_=2, to=21, textvariable=self.player_total_var,
                                         width=10, font=('Arial', 11))
        player_total_spinbox.grid(row=0, column=1, padx=(0, 20), pady=5)
        
        # Dealer Upcard
        ttk.Label(input_grid, text="Dealer Upcard:", style='Input.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10), pady=5)
        self.dealer_upcard_var = tk.StringVar(value="10")
        dealer_combo = ttk.Combobox(input_grid, textvariable=self.dealer_upcard_var,
                                   values=['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'],
                                   width=8, font=('Arial', 11))
        dealer_combo.grid(row=0, column=3, padx=(0, 20), pady=5)
        
        # Soft Hand (Checkbox)
        self.soft_hand_var = tk.BooleanVar(value=False)
        soft_checkbox = tk.Checkbutton(input_grid, 
                                      text="Soft Hand",
                                      variable=self.soft_hand_var,
                                      bg='#0a4d3a', 
                                      fg='#ffffff',
                                      selectcolor='#0a4d3a',
                                      activebackground='#0a4d3a',
                                      activeforeground='#00ff00',
                                      font=('Arial', 11, 'bold'))
        soft_checkbox.grid(row=1, column=0, columnspan=2, sticky='w', padx=(0, 20), pady=5)
        
        # Pair (Checkbox)
        self.pair_var = tk.BooleanVar(value=False)
        pair_checkbox = tk.Checkbutton(input_grid, 
                                      text="Pair",
                                      variable=self.pair_var,
                                      bg='#0a4d3a', 
                                      fg='#ffffff',
                                      selectcolor='#0a4d3a',
                                      activebackground='#0a4d3a',
                                      activeforeground='#00ff00',
                                      font=('Arial', 11, 'bold'))
        pair_checkbox.grid(row=1, column=2, columnspan=2, sticky='w', padx=(0, 20), pady=5)
        
        # Analyze button
        analyze_btn = ttk.Button(input_grid, text="🎯 Analyze Hand", 
                                style='Action.TButton',
                                command=self.analyze_hand)
        analyze_btn.grid(row=2, column=0, columnspan=4, pady=15)
        ToolTip(analyze_btn, "Analyze current hand and get optimal move recommendation\nShows expected value and detailed strategy explanation")
        

    
    def create_hand_results_section(self, parent):
        """Create the hand analysis results section."""
        results_frame = tk.LabelFrame(parent, 
                                     text="Results", 
                                     bg='#0a4d3a', 
                                     fg='#ffd700',
                                     font=('Arial', 14, 'bold'))
        results_frame.pack(fill='x', pady=(10, 0))
        
        # Results display
        results_grid = tk.Frame(results_frame, bg='#0a4d3a')
        results_grid.pack(padx=20, pady=15)
        
        # Recommendation
        ttk.Label(results_grid, text="Recommended Move:", style='Count.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        self.recommendation_var = tk.StringVar(value="Stand")
        ttk.Label(results_grid, textvariable=self.recommendation_var, style='Result.TLabel').grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Expected Value
        ttk.Label(results_grid, text="Expected Value:", style='Count.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.ev_var = tk.StringVar(value="0.00")
        ttk.Label(results_grid, textvariable=self.ev_var, style='Result.TLabel').grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Current True Count
        ttk.Label(results_grid, text="Current True Count:", style='Count.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.analysis_true_count_var = tk.StringVar(value="0.00")
        ttk.Label(results_grid, textvariable=self.analysis_true_count_var, style='Value.TLabel').grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
    
    def create_hand_analysis_content(self, parent):
        """Create the analysis content section on the right side."""
        analysis_frame = tk.LabelFrame(parent, 
                                      text="Analysis Content", 
                                      bg='#0a4d3a', 
                                      fg='#ffd700',
                                      font=('Arial', 14, 'bold'))
        analysis_frame.pack(fill='both', expand=True)
        
        # Create container for analysis content
        content_container = tk.Frame(analysis_frame, bg='#0a4d3a')
        content_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Hand Analysis section
        hand_frame = tk.LabelFrame(content_container, 
                                  text="Hand Analysis", 
                                  bg='#0a4d3a', 
                                  fg='#ffffff',
                                  font=('Arial', 12, 'bold'))
        hand_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.hand_analysis_text = tk.Text(hand_frame, 
                                         height=6, 
                                         bg='#1a5a47', 
                                         fg='#ffffff',
                                         font=('Arial', 10, 'bold'),
                                         wrap='word',
                                         relief='flat')
        self.hand_analysis_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Available Options section
        options_frame = tk.LabelFrame(content_container, 
                                     text="Available Options", 
                                     bg='#0a4d3a', 
                                     fg='#ffffff',
                                     font=('Arial', 12, 'bold'))
        options_frame.pack(fill='both', expand=True)
        
        self.options_text = tk.Text(options_frame, 
                                   height=6, 
                                   bg='#1a5a47', 
                                   fg='#ffffff',
                                   font=('Arial', 10, 'bold'),
                                   wrap='word',
                                   relief='flat')
        self.options_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def analyze_hand(self):
        """Analyze the current hand and display results."""
        try:
            # Get input values
            player_total = int(self.player_total_var.get())
            dealer_upcard = self.dealer_upcard_var.get()
            is_soft = self.soft_hand_var.get()
            is_pair = self.pair_var.get()
            
            # Validate inputs
            if not (2 <= player_total <= 21):
                raise ValueError("Player total must be between 2 and 21")
            
            if dealer_upcard not in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                raise ValueError("Invalid dealer upcard")
            
            # Get recommendation and EV
            result = self.counter.get_move_with_ev(player_total, dealer_upcard, is_soft, is_pair)
            
            # Update display
            best_move = result.get('Best', 'Unknown')
            self.recommendation_var.set(best_move)
            
            # Get the EV for the best move, or show "N/A" if not available
            if best_move in result and isinstance(result[best_move], (int, float)):
                self.ev_var.set(f"{result[best_move]:.4f}")
            else:
                self.ev_var.set("N/A")
            
            self.analysis_true_count_var.set(f"{self.counter.true_count:.2f}")
            
            # Create explanation content
            hand_info, options_info = self.create_hand_explanation(player_total, dealer_upcard, is_soft, is_pair, result)
            
            # Update hand analysis text (left side)
            self.hand_analysis_text.delete('1.0', 'end')
            self.hand_analysis_text.insert('1.0', hand_info)
            
            # Update options text (right side)
            self.options_text.delete('1.0', 'end')
            self.options_text.insert('1.0', options_info)
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error analyzing hand: {str(e)}")
    

    
    def create_hand_explanation(self, player_total, dealer_upcard, is_soft, is_pair, result):
        """Create simplified explanation for the hand analysis split into two parts."""
        
        # Left side - Hand Analysis info
        hand_info = f"Hand Analysis:\n"
        hand_info += f"Player: {player_total}"
        if is_soft:
            hand_info += " (Soft)"
        if is_pair:
            hand_info += " (Pair)"
        hand_info += f"\nDealer: {dealer_upcard}\n"
        hand_info += f"True Count: {self.counter.true_count:.2f}\n\n"
        
        # Handle EV display and house/player advantage
        best_move = result.get('Best', 'Unknown')
        if best_move in result and isinstance(result[best_move], (int, float)):
            ev_value = result[best_move]
            
            if ev_value > 0:
                hand_info += "✅ This is a favorable situation for the player."
            elif ev_value == 0:
                hand_info += "⚪ This is a neutral situation."
            else:
                hand_info += "❌ This situation favors the house."
        
        # Right side - Available Options
        options_info = "All Available Options:\n"
        if any(isinstance(v, (int, float)) for k, v in result.items() if k not in ['Best', 'Info']):
            # Create list of moves with their EV values, excluding 'Best' and 'Info'
            moves_with_ev = []
            for move, ev in result.items():
                if move not in ['Best', 'Info'] and isinstance(ev, (int, float)):
                    moves_with_ev.append((move, ev))
            
            # Sort by EV in descending order (highest EV first)
            moves_with_ev.sort(key=lambda x: x[1], reverse=True)
            
            # Add sorted options to the display
            for move, ev in moves_with_ev:
                options_info += f"• {move}: {ev:.4f}\n"
        else:
            options_info += "No detailed EV data available"
        
        return hand_info, options_info
    
    def create_card_section(self, parent):
        """Create the card selection buttons."""
        card_frame = tk.Frame(parent, bg='#0a4d3a', width=350)
        card_frame.pack(side='left', padx=(0, 30), pady=15)
        
        # Card section title
        card_title = ttk.Label(card_frame, 
                              text="Deal Cards", 
                              style='Count.TLabel')
        card_title.pack(pady=(0, 15))
        
        # Card input section
        input_section = tk.Frame(card_frame, bg='#0a4d3a')
        input_section.pack(pady=10, fill='x')
        
        # Input label
        input_label = ttk.Label(input_section, 
                               text="Enter Card:", 
                               style='Input.TLabel')
        input_label.pack(pady=(0, 5))
        
        # Card input entry
        self.card_input_var = tk.StringVar()
        self.card_input = tk.Entry(input_section, 
                                  textvariable=self.card_input_var,
                                  font=('Arial', 14, 'bold'),
                                  width=10,
                                  justify='center',
                                  bg='#ffffff',
                                  fg='#000000')
        self.card_input.pack(pady=5)
        self.card_input.bind('<Return>', self.on_card_enter)
        self.card_input.bind('<KP_Enter>', self.on_card_enter)  # Numeric keypad Enter
        self.card_input.bind('<KeyRelease>', self.on_key_release)
        self.card_input.focus_set()  # Set focus to input box
        
        # Deal button
        deal_btn = ttk.Button(input_section, 
                             text="Deal Card", 
                             style='Action.TButton',
                             command=self.deal_card_from_input)
        deal_btn.pack(pady=5)
        

        
        # Last 10 cards dealt display
        self.create_last_cards_section(card_frame)
    
    def create_last_cards_section(self, parent):
        """Create just the last 10 cards display."""
        # Last 10 cards dealt display
        last_cards_frame = tk.LabelFrame(parent, 
                                        text="Last 10 Cards", 
                                        bg='#0a4d3a', 
                                        fg='#ffd700',
                                        font=('Arial', 10, 'bold'))
        last_cards_frame.pack(pady=15, fill='x')
        
        # Create a frame for colored card display
        self.cards_display_frame = tk.Frame(last_cards_frame, bg='#0a4d3a')
        self.cards_display_frame.pack(pady=8)
        
        # Initialize list to store last 8 cards
        self.last_cards_list = []
        self.card_labels = []  # Store the label widgets
        
        # Create initial "None dealt yet" label
        self.no_cards_label = tk.Label(self.cards_display_frame, 
                                      text="None dealt yet",
                                      bg='#0a4d3a', fg='#00ffff',
                                      font=('Arial', 12, 'bold'))
        self.no_cards_label.pack()
    
    def create_display_section(self, parent):
        """Create the count display and recommendations section."""
        display_frame = tk.Frame(parent, bg='#0a4d3a', width=450)
        display_frame.pack(side='right', padx=(30, 0), pady=15)
        
        # Create a horizontal container for counts and remaining cards
        top_container = tk.Frame(display_frame, bg='#0a4d3a')
        top_container.pack(fill='x', pady=(0, 10))
        
        # Count displays (left side)
        counts_frame = tk.LabelFrame(top_container, 
                                   text="Current Count", 
                                   bg='#0a4d3a', 
                                   fg='#ffd700',
                                   font=('Arial', 12, 'bold'))
        counts_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Running count
        running_frame = tk.Frame(counts_frame, bg='#0a4d3a')
        running_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(running_frame, 
                 text="Running Count:", 
                 style='Count.TLabel').pack(side='left')
        
        self.running_count_var = tk.StringVar(value="0")
        self.running_count_label = ttk.Label(running_frame, 
                                           textvariable=self.running_count_var,
                                           style='Value.TLabel')
        self.running_count_label.pack(side='right')
        
        # True count
        true_frame = tk.Frame(counts_frame, bg='#0a4d3a')
        true_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(true_frame, 
                 text="True Count:", 
                 style='Count.TLabel').pack(side='left')
        
        self.true_count_var = tk.StringVar(value="0.00")
        self.true_count_label = ttk.Label(true_frame, 
                                        textvariable=self.true_count_var,
                                        style='Value.TLabel')
        self.true_count_label.pack(side='right')
        
        # Remaining decks
        decks_frame = tk.Frame(counts_frame, bg='#0a4d3a')
        decks_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(decks_frame, 
                 text="Remaining Decks:", 
                 style='Count.TLabel').pack(side='left')
        
        self.remaining_decks_var = tk.StringVar(value="8.00")
        self.remaining_decks_label = ttk.Label(decks_frame, 
                                             textvariable=self.remaining_decks_var,
                                             style='Value.TLabel')
        self.remaining_decks_label.pack(side='right')
        
        # Hi-Lo group totals - one per line with color coding
        # Low cards
        low_frame = tk.Frame(counts_frame, bg='#0a4d3a')
        low_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(low_frame, 
                 text="Low:", 
                 style='Count.TLabel').pack(side='left')
        
        self.low_total_var = tk.StringVar(value="160")
        self.low_total_label = tk.Label(low_frame, 
                                       textvariable=self.low_total_var,
                                       bg='#0a4d3a', 
                                       fg='#00ff00',  # Green
                                       font=('Arial', 14, 'bold'))
        self.low_total_label.pack(side='right')
        
        # Neutral cards
        neutral_frame = tk.Frame(counts_frame, bg='#0a4d3a')
        neutral_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(neutral_frame, 
                 text="Neutral:", 
                 style='Count.TLabel').pack(side='left')
        
        self.neutral_total_var = tk.StringVar(value="96")
        self.neutral_total_label = tk.Label(neutral_frame, 
                                           textvariable=self.neutral_total_var,
                                           bg='#0a4d3a', 
                                           fg='#ffff00',  # Yellow
                                           font=('Arial', 14, 'bold'))
        self.neutral_total_label.pack(side='right')
        
        # High cards
        high_frame = tk.Frame(counts_frame, bg='#0a4d3a')
        high_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(high_frame, 
                 text="High:", 
                 style='Count.TLabel').pack(side='left')
        
        self.high_total_var = tk.StringVar(value="160")
        self.high_total_label = tk.Label(high_frame, 
                                        textvariable=self.high_total_var,
                                        bg='#0a4d3a', 
                                        fg='#ff6b6b',  # Red
                                        font=('Arial', 14, 'bold'))
        self.high_total_label.pack(side='right')
        
        # Card composition section (right side of top container)
        self.create_card_composition_section(top_container)
        
        # Recommendations (smaller)
        self.create_recommendations_section(display_frame)
    
    def create_recommendations_section(self, parent):
        """Create the betting recommendations section (smaller)."""
        rec_frame = tk.LabelFrame(parent, 
                                text="Betting Recommendation", 
                                bg='#0a4d3a', 
                                fg='#ffd700',
                                font=('Arial', 12, 'bold'))
        rec_frame.pack(fill='x', pady=10)
        
        # Betting recommendation only
        betting_frame = tk.Frame(rec_frame, bg='#0a4d3a')
        betting_frame.pack(fill='x', padx=10, pady=8)
        
        self.betting_rec_var = tk.StringVar(value="Neutral count - House advantage, minimum bet")
        self.betting_rec_label = ttk.Label(betting_frame, 
                                         textvariable=self.betting_rec_var,
                                         style='Recommendation.TLabel',
                                         wraplength=400)
        self.betting_rec_label.pack(anchor='w')
    

    
    def create_card_composition_section(self, parent):
        """Create the card composition display section."""
        comp_frame = tk.LabelFrame(parent, 
                                  text="Remaining Cards", 
                                  bg='#0a4d3a', 
                                  fg='#ffd700',
                                  font=('Arial', 12, 'bold'))
        comp_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Create direct frame for card counts (no scrolling)
        self.card_composition_frame = tk.Frame(comp_frame, bg='#0a4d3a')
        self.card_composition_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Store references for updating
        self.card_labels_dict = {}
        
        # Create initial card count display
        self.update_card_composition()
    
    def update_card_composition(self):
        """Update the card composition display with current card counts."""
        # Clear existing labels and frames completely
        for label in self.card_labels_dict.values():
            label.destroy()
        self.card_labels_dict = {}
        
        # Clear all child widgets from the composition frame
        for widget in self.card_composition_frame.winfo_children():
            widget.destroy()
        
        # Get current card counts
        card_counts = self.counter.get_current_status()['card_counts']
        
        # Group cards by type for better organization
        low_cards = ['2', '3', '4', '5', '6']
        neutral_cards = ['7', '8', '9']
        high_cards = ['10', 'J', 'Q', 'K', 'A']
        
        # Create fresh column frames
        col1_frame = tk.Frame(self.card_composition_frame, bg='#0a4d3a')
        col1_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        col2_frame = tk.Frame(self.card_composition_frame, bg='#0a4d3a')
        col2_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        # Column 1: Low and Neutral cards (no headers - color coding is enough)
        row1 = 0
        
        # Low cards in column 1
        for card in low_cards:
            count = card_counts[card]
            card_text = f"{card}: {count}"
            card_label = tk.Label(col1_frame, 
                                 text=card_text, 
                                 bg='#0a4d3a', fg='#00ff00', 
                                 font=('Arial', 12, 'bold'))
            card_label.grid(row=row1, column=0, sticky='w', padx=(8, 0), pady=4)
            self.card_labels_dict[f"{card}_combined"] = card_label
            row1 += 1
        
        # Add space between sections
        row1 += 1
        
        # Neutral cards in column 1
        for card in neutral_cards:
            count = card_counts[card]
            card_text = f"{card}: {count}"
            card_label = tk.Label(col1_frame, 
                                 text=card_text, 
                                 bg='#0a4d3a', fg='#ffff00', 
                                 font=('Arial', 12, 'bold'))
            card_label.grid(row=row1, column=0, sticky='w', padx=(8, 0), pady=4)
            self.card_labels_dict[f"{card}_combined"] = card_label
            row1 += 1
        
        # Column 2: High cards (no header - color coding is enough)
        row2 = 0
        
        for card in high_cards:
            count = card_counts[card]
            card_text = f"{card}: {count}"
            card_label = tk.Label(col2_frame, 
                                 text=card_text, 
                                 bg='#0a4d3a', fg='#ff6b6b', 
                                 font=('Arial', 12, 'bold'))
            card_label.grid(row=row2, column=0, sticky='w', padx=(8, 0), pady=4)
            self.card_labels_dict[f"{card}_combined"] = card_label
            row2 += 1
    
    def create_action_section(self, parent):
        """Create action buttons at the bottom."""
        action_frame = tk.Frame(parent, bg='#0a4d3a')
        action_frame.pack(side='bottom', fill='x', pady=20)
        
        # Center all buttons
        button_container = tk.Frame(action_frame, bg='#0a4d3a')
        button_container.pack()
        
        # Reset button
        reset_btn = ttk.Button(button_container, 
                              text="🔄 New Shoe", 
                              style='Action.TButton',
                              command=self.reset_shoe)
        reset_btn.pack(side='left', padx=5)
        ToolTip(reset_btn, "Start a new shoe with 8 fresh decks\nResets running count, true count, and all cards")
        
        # Recording buttons
        self.start_record_btn = ttk.Button(button_container, 
                                          text="📹 Start Recording", 
                                          style='Action.TButton',
                                          command=self.start_shoe_recording)
        self.start_record_btn.pack(side='left', padx=5)
        ToolTip(self.start_record_btn, "Start recording card flow for this shoe")
        
        self.stop_record_btn = ttk.Button(button_container, 
                                         text="⏹️ Stop Recording", 
                                         style='Action.TButton',
                                         command=self.stop_shoe_recording,
                                         state='disabled')
        self.stop_record_btn.pack(side='left', padx=5)
        ToolTip(self.stop_record_btn, "Stop recording and save shoe data")
        
        # Help button
        help_btn = ttk.Button(button_container, 
                             text="❓ Help", 
                             style='Action.TButton',
                             command=self.show_help)
        help_btn.pack(side='left', padx=5)
        
        # Exit button
        exit_btn = ttk.Button(button_container, 
                             text="❌ Exit", 
                             style='Action.TButton',
                             command=self.root.quit)
        exit_btn.pack(side='left', padx=5)
        ToolTip(help_btn, "Show detailed help and instructions\nIncludes Hi-Lo counting rules and betting strategy")
    
    def deal_card(self, card):
        """Deal a card and update the display."""
        try:
            # Handle special placeholder and replacement cases
            if card == '+':
                # Hidden card placeholder - don't affect count, just record
                if self.flow_recording:
                    self.card_flow.append(card)
                    self.update_flow_display()
                    self.update_flow_stats()
                
                # Update last card display with placeholder
                self.update_last_card_display(card)
                self.flash_button_feedback(card)
                return
            
            elif '+' in card and len(card) > 1:
                # Replacement format like "5+" - replace placeholder with actual card
                actual_card = card.replace('+', '')
                if self.replace_placeholder_with_card(actual_card):
                    # Process the actual card for counting
                    running_count, true_count, remaining_decks = self.counter.deal_card(actual_card)
                    self.update_display()
                    
                    # Track max and min counts
                    if self.flow_recording:
                        current_rc = self.counter.running_count
                        current_tc = self.counter.true_count
                        self.max_running_count = max(self.max_running_count, current_rc)
                        self.min_running_count = min(self.min_running_count, current_rc)
                        self.max_true_count = max(self.max_true_count, current_tc)
                        self.min_true_count = min(self.min_true_count, current_tc)
                        self.update_flow_display()
                        self.update_flow_stats()
                    
                    # Update last card display
                    self.update_last_card_display(actual_card)
                    self.flash_button_feedback(actual_card)
                else:
                    messagebox.showerror("Error", "No placeholder '+' found to replace!")
                return
            
            # Normal card processing
            running_count, true_count, remaining_decks = self.counter.deal_card(card)
            self.update_display()
            
            # Add to card flow if recording
            if self.flow_recording:
                self.card_flow.append(card)
                # Track max and min running counts
                current_rc = self.counter.running_count
                current_tc = self.counter.true_count
                self.max_running_count = max(self.max_running_count, current_rc)
                self.min_running_count = min(self.min_running_count, current_rc)
                self.max_true_count = max(self.max_true_count, current_tc)
                self.min_true_count = min(self.min_true_count, current_tc)
                self.update_flow_display()
                self.update_flow_stats()
            
            # Update last card display
            self.update_last_card_display(card)
            
            # Flash the card button to show it was clicked
            self.flash_button_feedback(card)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def replace_placeholder_with_card(self, actual_card):
        """Replace the most recent '+' placeholder with the actual card value."""
        if not self.flow_recording:
            return False
        
        # Find the most recent '+' placeholder in the card flow
        for i in range(len(self.card_flow) - 1, -1, -1):
            if self.card_flow[i] == '+':
                self.card_flow[i] = actual_card
                return True
        
        return False  # No placeholder found
    
    def deal_card_from_input(self):
        """Deal a card from the input box."""
        card = self.card_input_var.get().strip().upper()
        if card:
            # Convert numeric face card inputs
            card = self.convert_numeric_input(card)
            self.deal_card(card)
            self.card_input_var.set("")  # Clear input after dealing
            self.card_input.focus_set()  # Keep focus on input
    
    def convert_numeric_input(self, input_card):
        """Convert numeric inputs to card values."""
        # Convert numeric face card representations
        conversion_map = {
            '1': 'A',   # Ace
            '11': 'J',  # Jack
            '12': 'Q',  # Queen
            '13': 'K'   # King
        }
        return conversion_map.get(input_card, input_card)
    
    def on_card_enter(self, event):
        """Handle Enter key press in card input."""
        self.deal_card_from_input()
    
    def on_key_release(self, event):
        """Handle key release in card input for auto-formatting."""
        current_text = self.card_input_var.get().upper()
        
        # Valid inputs include regular cards, numeric face cards, and placeholder system
        valid_inputs = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', 'J', 'Q', 'K', 'A', '+']
        
        # Valid replacement patterns like "5+", "A+", "10+", etc.
        replacement_patterns = [f"{card}+" for card in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', 'J', 'Q', 'K', 'A']]
        
        # Auto-format common inputs
        if current_text in valid_inputs or current_text in replacement_patterns:
            # Valid input - change background to indicate success
            self.card_input.config(bg='#e8f5e8')  # Light green
        elif current_text == '':
            # Empty input
            self.card_input.config(bg='#ffffff')  # White
        elif current_text in ['1'] and len(current_text) == 1:
            # Partial input - could be '1' (Ace), '10', '11', '12', or '13'
            self.card_input.config(bg='#fff8e1')  # Light yellow
        elif len(current_text) > 1 and current_text.endswith('+'):
            # Partial replacement input like "5" before adding "+"
            partial_card = current_text[:-1]
            if partial_card in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', 'J', 'Q', 'K', 'A']:
                self.card_input.config(bg='#e8f5e8')  # Light green for valid replacement
            else:
                self.card_input.config(bg='#ffe8e8')  # Light red for invalid
        else:
            # Invalid input
            self.card_input.config(bg='#ffe8e8')  # Light red
    
    def update_last_card_display(self, card):
        """Update the last 8 cards dealt display with color-coded cards."""
        # Handle placeholder card
        if card == '+':
            color = '#808080'  # Gray for placeholder
        else:
            # Get the Hi-Lo value for the card to determine color
            hi_lo_value = self.counter.counting_values.get(card, 0)
            
            # Determine color based on Hi-Lo value
            if hi_lo_value == 1:  # Low cards
                color = '#00ff00'  # Bright green
            elif hi_lo_value == 0:  # Neutral cards
                color = '#ffff00'  # Bright yellow
            else:  # hi_lo_value == -1, High cards
                color = '#ff6b6b'  # Red
        
        # Add the new card to the beginning of the list
        self.last_cards_list.insert(0, {'card': card, 'color': color})
        
        # Keep only the last 10 cards
        if len(self.last_cards_list) > 10:
            self.last_cards_list = self.last_cards_list[:10]
        
        # Update the visual display
        self.update_cards_display()
    
    def update_cards_display(self):
        """Update the visual display of the last 10 cards with proper colors in one line."""
        # Clear existing card labels and frames
        for label in self.card_labels:
            label.destroy()
        self.card_labels = []
        
        # Clear any existing frames in the display area
        for widget in self.cards_display_frame.winfo_children():
            if widget != self.no_cards_label:
                widget.destroy()
        
        # Hide "None dealt yet" label if cards exist
        if self.last_cards_list:
            self.no_cards_label.pack_forget()
            
            # Create a single horizontal frame for all cards
            cards_frame = tk.Frame(self.cards_display_frame, bg='#0a4d3a')
            cards_frame.pack()
            
            # Create colored labels for each card in one line
            for i, card_info in enumerate(self.last_cards_list):
                card_label = tk.Label(cards_frame, 
                                     text=card_info['card'],
                                     bg='#0a4d3a', 
                                     fg=card_info['color'],
                                     font=('Arial', 12, 'bold'),
                                     width=2)  # Smaller width to fit 10 cards
                card_label.pack(side='left', padx=2)
                self.card_labels.append(card_label)
        else:
            # Show "None dealt yet" if no cards
            self.no_cards_label.pack()
    
    def flash_button_feedback(self, card):
        """Provide visual feedback when a card button is clicked."""
        # This is a simple implementation - in a more complex UI you might
        # highlight the specific button that was clicked
        self.root.configure(bg='#0f5f4a')
        self.root.after(100, lambda: self.root.configure(bg='#0a4d3a'))
    
    def update_display(self):
        """Update all display elements with current counter status."""
        status = self.counter.get_current_status()
        
        # Update count displays
        self.running_count_var.set(str(status['running_count']))
        self.true_count_var.set(f"{status['true_count']:.2f}")
        self.remaining_decks_var.set(f"{status['remaining_decks']:.2f}")
        
        # Calculate and update Hi-Lo group totals
        card_counts = status['card_counts']
        low_total = sum(card_counts[card] for card in ['2', '3', '4', '5', '6'])
        neutral_total = sum(card_counts[card] for card in ['7', '8', '9'])
        high_total = sum(card_counts[card] for card in ['10', 'J', 'Q', 'K', 'A'])
        
        self.low_total_var.set(str(low_total))
        self.neutral_total_var.set(str(neutral_total))
        self.high_total_var.set(str(high_total))
        
        # Update recommendations
        betting_rec = self.counter.get_betting_recommendation()
        self.betting_rec_var.set(betting_rec)
        
        # Update card composition display
        if hasattr(self, 'card_composition_frame'):
            self.update_card_composition()
        
        # Update true count color based on value
        self.update_count_colors(status['true_count'])
    
    def update_count_colors(self, true_count):
        """Update count display colors based on true count value."""
        if true_count >= 2:
            color = '#00ff00'  # Bright green for positive
        elif true_count >= 1:
            color = '#90ee90'  # Light green for slightly positive
        elif true_count >= -1:
            color = '#ffff00'  # Yellow for neutral
        else:
            color = '#ff6b6b'  # Red for negative
        
        # Update the true count label color
        style = ttk.Style()
        style.configure('Value.TLabel', foreground=color)
    
    def reset_shoe(self):
        """Reset the counter to start a new shoe."""
        # Check if we have an active recording to save
        save_message = ""
        if self.flow_recording and self.card_flow:
            save_message = f"\n• Current shoe ({self.current_shoe_id}) will be auto-saved"
        
        result = messagebox.askyesno("Reset Shoe", 
                                   f"Are you sure you want to start a new shoe?\n\nThis will reset:\n• Running count to 0\n• True count to 0\n• All 8 decks (416 cards)\n• Start new card flow recording{save_message}")
        if result:
            # Auto-save current recording if active
            if self.flow_recording and self.card_flow:
                self.stop_shoe_recording()
                messagebox.showinfo("Auto-Saved", f"Previous shoe {self.current_shoe_id} has been automatically saved!")
            
            self.counter.reset_shoe()
            self.update_display()
            
            # Reset flow recording and start new
            self.card_flow = []
            self.current_shoe_id = None
            self.flow_recording = False
            self.max_running_count = 0
            self.min_running_count = 0
            self.max_true_count = 0.0
            self.min_true_count = 0.0
            
            # Update UI states - both Card Counter and Flow tab buttons
            if hasattr(self, 'start_record_btn'):
                self.start_record_btn.config(state='normal')
            if hasattr(self, 'stop_record_btn'):
                self.stop_record_btn.config(state='disabled')
            if hasattr(self, 'flow_start_btn'):
                self.flow_start_btn.config(state='normal')
            if hasattr(self, 'flow_stop_btn'):
                self.flow_stop_btn.config(state='disabled')
            
            # Update flow display
            if hasattr(self, 'update_flow_display'):
                self.update_flow_display()
                self.update_flow_stats()
            
            # Also update hand analysis if it exists
            if hasattr(self, 'analysis_true_count_var'):
                self.analysis_true_count_var.set("0.00")
            
            # Reset last cards display
            if hasattr(self, 'last_cards_list'):
                self.last_cards_list = []
                self.update_cards_display()
            
            # Flash confirmation
            self.root.configure(bg='#0f5f4a')
            self.root.after(200, lambda: self.root.configure(bg='#0a4d3a'))
            
            messagebox.showinfo("✅ Reset Complete", 
                              "New shoe started!\n\n🃏 8 fresh decks (416 cards)\n📊 All counts reset to 0\n🎯 Ready for new recording")
    
    def show_help(self):
        """Show help dialog with instructions."""
        help_text = """🃏 Blackjack Card Counter Help 🃏

HOW TO USE:
1. Enter cards as they're dealt: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
2. Watch the Running Count and True Count update in real-time
3. Follow the betting recommendations based on the count
4. Use "New Shoe" to reset when the shoe is finished

🎭 DEALER HIDDEN CARD SYSTEM:
• Type '+' for dealer's hidden card (doesn't affect count)
• When revealed, type 'CARD+' to replace (e.g., '5+', 'A+', '10+')
• Maintains perfect chronological order for ML analysis
• Example: Deal sequence: 8 J K Q A 6 7 4 5 + 6 5 K Q...
• When dealer shows 5: type '5+' → replaces '+' with '5'

HI-LO COUNTING SYSTEM:
• Low cards (2-6): +1 each
• Neutral cards (7-9): 0 each  
• High cards (10-A): -1 each
• Placeholder '+': 0 (no count effect)

TRUE COUNT:
• True Count = Running Count ÷ Remaining Decks
• More accurate than running count alone
• Higher positive counts favor the player

BETTING STRATEGY:
• True Count +3 or higher: Increase bet size
• True Count +1 to +2: Normal betting
• True Count 0 to -1: Minimum bet
• True Count -2 or lower: Minimum bet or skip

REMEMBER: Card counting is for entertainment and educational purposes only!"""
        
        messagebox.showinfo("Help", help_text)
    
    def start_shoe_recording(self):
        """Start recording the current shoe."""
        if self.flow_recording:
            messagebox.showwarning("Already Recording", "Recording is already active.")
            return
        
        # Generate random shoe ID
        import random
        self.current_shoe_id = f"SHOE_{random.randint(10000, 99999)}"
        
        # Start recording
        self.flow_recording = True
        self.card_flow = []
        self.max_running_count = 0
        self.min_running_count = 0
        self.max_true_count = 0.0
        self.min_true_count = 0.0
        
        # Update UI - both Card Counter and Flow tab buttons
        self.start_record_btn.config(state='disabled')
        self.stop_record_btn.config(state='normal')
        if hasattr(self, 'flow_start_btn'):
            self.flow_start_btn.config(state='disabled')
        if hasattr(self, 'flow_stop_btn'):
            self.flow_stop_btn.config(state='normal')
        
        # Update flow display if available
        if hasattr(self, 'update_flow_display'):
            self.update_flow_display()
            self.update_flow_stats()
        
        messagebox.showinfo("Recording Started", f"Started recording shoe: {self.current_shoe_id}\n\nCards will be automatically recorded as you deal them.")
    
    def stop_shoe_recording(self):
        """Stop recording and save the shoe."""
        if not self.flow_recording:
            return
        
        if not self.card_flow:
            messagebox.showwarning("No Data", "No cards recorded yet.")
            self.flow_recording = False
            self.start_record_btn.config(state='normal')
            self.stop_record_btn.config(state='disabled')
            return
        
        # Create filename with proper directory structure
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure recorded_shoes directory exists
        recordings_dir = "recorded_shoes"
        if not os.path.exists(recordings_dir):
            os.makedirs(recordings_dir)
        
        filename = os.path.join(recordings_dir, f"shoe_{self.current_shoe_id}_{timestamp}.json")
        
        # Save flow data
        flow_data = {
            'shoe_id': self.current_shoe_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'card_flow': self.card_flow,
            'final_stats': {
                'total_cards': len(self.card_flow),
                'penetration': round((len(self.card_flow) / (8 * 52)) * 100, 2),
                'max_running_count': self.max_running_count,
                'min_running_count': self.min_running_count,
                'max_true_count': round(self.max_true_count, 2),
                'min_true_count': round(self.min_true_count, 2),
                'final_true_count': round(self.counter.true_count, 2)
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(flow_data, f, indent=2)
            
            # Update UI - both Card Counter and Flow tab buttons
            self.flow_recording = False
            self.start_record_btn.config(state='normal')
            self.stop_record_btn.config(state='disabled')
            if hasattr(self, 'flow_start_btn'):
                self.flow_start_btn.config(state='normal')
            if hasattr(self, 'flow_stop_btn'):
                self.flow_stop_btn.config(state='disabled')
            
            messagebox.showinfo("Recording Saved", f"Shoe {self.current_shoe_id} saved to: {filename}\n\nCards recorded: {len(self.card_flow)}\nMax RC: {self.max_running_count}, Min RC: {self.min_running_count}\nMax TC: {self.max_true_count:.2f}, Min TC: {self.min_true_count:.2f}\nFinal TC: {self.counter.true_count:.2f}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save recording: {e}")
    
    def setup_card_flow_tab(self, parent):
        """Setup the card flow display tab."""
        container = tk.Frame(parent, bg='#0a4d3a')
        container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title
        title_frame = tk.Frame(container, bg='#0a4d3a')
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                               text="🃏 Card Flow Display", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Shows cards from Card Counter tab when recording", 
                                  style='Recommendation.TLabel')
        subtitle_label.pack()
        
        # Main display area
        self.create_flow_display_section(container)
    
    def create_flow_display_section(self, parent):
        """Create the simplified card flow display section."""
        display_frame = tk.LabelFrame(parent, 
                                     text="Current Shoe Recording", 
                                     bg='#0a4d3a', 
                                     fg='#ffd700',
                                     font=('Arial', 14, 'bold'))
        display_frame.pack(fill='both', expand=True)
        
        # Status info
        status_frame = tk.Frame(display_frame, bg='#0a4d3a')
        status_frame.pack(fill='x', padx=15, pady=10)
        
        # Current shoe ID
        ttk.Label(status_frame, text="Shoe ID:", style='Input.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.flow_shoe_id_var = tk.StringVar(value="No recording")
        ttk.Label(status_frame, textvariable=self.flow_shoe_id_var, style='Value.TLabel').grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        # Recording status
        ttk.Label(status_frame, text="Status:", style='Input.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.flow_status_var = tk.StringVar(value="Not recording")
        ttk.Label(status_frame, textvariable=self.flow_status_var, style='Result.TLabel').grid(row=0, column=3, sticky='w')
        
        # Flow display text
        text_frame = tk.Frame(display_frame, bg='#0a4d3a')
        text_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.flow_display = tk.Text(text_frame,
                                   bg='#1a5a47',
                                   fg='#ffffff',
                                   font=('Courier', 12, 'bold'),
                                   wrap='word',
                                   state='disabled')
        
        flow_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.flow_display.yview)
        self.flow_display.configure(yscrollcommand=flow_scrollbar.set)
        
        self.flow_display.pack(side='left', fill='both', expand=True)
        flow_scrollbar.pack(side='right', fill='y')
        
        # Stats
        stats_frame = tk.Frame(display_frame, bg='#0a4d3a')
        stats_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        stats_grid = tk.Frame(stats_frame, bg='#0a4d3a')
        stats_grid.pack()
        
        ttk.Label(stats_grid, text="Cards:", style='Input.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.flow_cards_count_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.flow_cards_count_var, style='Value.TLabel').grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        ttk.Label(stats_grid, text="Penetration:", style='Input.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.flow_penetration_var = tk.StringVar(value="0.0%")
        ttk.Label(stats_grid, textvariable=self.flow_penetration_var, style='Value.TLabel').grid(row=0, column=3, sticky='w')
        
        # Control buttons for Card Flow tab
        controls_frame = tk.Frame(stats_frame, bg='#0a4d3a')
        controls_frame.pack(pady=15)
        
        # Start recording button (same functionality as Card Counter tab)
        self.flow_start_btn = ttk.Button(controls_frame, 
                                        text="📹 Start Recording", 
                                        style='Action.TButton',
                                        command=self.start_shoe_recording)
        self.flow_start_btn.pack(side='left', padx=(0, 10))
        ToolTip(self.flow_start_btn, "Start recording card flow (same as Card Counter tab)")
        
        # Stop recording button
        self.flow_stop_btn = ttk.Button(controls_frame, 
                                       text="⏹️ Stop Recording", 
                                       style='Action.TButton',
                                       command=self.stop_shoe_recording,
                                       state='disabled')
        self.flow_stop_btn.pack(side='left', padx=(0, 10))
        ToolTip(self.flow_stop_btn, "Stop recording and save current shoe")
        
        # Upload/Load previous shoes button
        upload_btn = ttk.Button(controls_frame, 
                               text="📂 Load Previous Shoe", 
                               style='Action.TButton',
                               command=self.load_previous_shoe)
        upload_btn.pack(side='left', padx=(0, 10))
        ToolTip(upload_btn, "Load a previously saved shoe file")
        
        # Clear current display button
        clear_btn = ttk.Button(controls_frame, 
                              text="🗑️ Clear Display", 
                              style='Action.TButton',
                              command=self.clear_flow_display)
        clear_btn.pack(side='left')
        ToolTip(clear_btn, "Clear current flow display without saving")
    
    def update_flow_display(self):
        """Update the flow display with current cards."""
        if not hasattr(self, 'flow_display'):
            return
            
        self.flow_display.config(state='normal')
        self.flow_display.delete('1.0', 'end')
        
        if self.current_shoe_id:
            self.flow_shoe_id_var.set(self.current_shoe_id)
        else:
            self.flow_shoe_id_var.set("No recording")
        
        if self.flow_recording:
            self.flow_status_var.set("🔴 Recording")
        else:
            self.flow_status_var.set("Not recording")
        
        if not self.card_flow:
            self.flow_display.insert('1.0', "No cards recorded yet.\n\nStart recording in Card Counter tab to see cards here!")
        else:
            content = f"Card Flow for {self.current_shoe_id or 'Unknown'}:\n" + "="*50 + "\n\n"
            
            for i in range(0, len(self.card_flow), 10):
                chunk = self.card_flow[i:i+10]
                line_num = i // 10 + 1
                content += f"Line {line_num:2d}: {' '.join(chunk)}\n"
            
            self.flow_display.insert('1.0', content)
        
        self.flow_display.config(state='disabled')
        self.flow_display.see('end')
    
    def update_flow_stats(self):
        """Update flow statistics display."""
        if not hasattr(self, 'flow_cards_count_var'):
            return
            
        card_count = len(self.card_flow)
        self.flow_cards_count_var.set(str(card_count))
        
        if card_count > 0:
            penetration = (card_count / (8 * 52)) * 100
            self.flow_penetration_var.set(f"{penetration:.1f}%")
        else:
            self.flow_penetration_var.set("0.0%")
    
    def load_previous_shoe(self):
        """Load a previously saved shoe file."""
        # Set initial directory to recorded_shoes if it exists
        initial_dir = "recorded_shoes" if os.path.exists("recorded_shoes") else "."
        
        filename = filedialog.askopenfilename(
            title="Load Previous Shoe File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r') as f:
                flow_data = json.load(f)
            
            # Load flow data
            self.card_flow = flow_data.get('card_flow', [])
            self.current_shoe_id = flow_data.get('shoe_id', 'Loaded')
            
            # Stop any current recording
            self.flow_recording = False
            
            # Update button states
            if hasattr(self, 'start_record_btn'):
                self.start_record_btn.config(state='normal')
            if hasattr(self, 'stop_record_btn'):
                self.stop_record_btn.config(state='disabled')
            if hasattr(self, 'flow_start_btn'):
                self.flow_start_btn.config(state='normal')
            if hasattr(self, 'flow_stop_btn'):
                self.flow_stop_btn.config(state='disabled')
            
            # Replay flow through counter and track max/min
            self.counter.reset_shoe()
            self.max_running_count = 0
            self.min_running_count = 0
            self.max_true_count = 0.0
            self.min_true_count = 0.0
            
            for card in self.card_flow:
                try:
                    self.counter.deal_card(card)
                    # Track max and min running and true counts during replay
                    current_rc = self.counter.running_count
                    current_tc = self.counter.true_count
                    self.max_running_count = max(self.max_running_count, current_rc)
                    self.min_running_count = min(self.min_running_count, current_rc)
                    self.max_true_count = max(self.max_true_count, current_tc)
                    self.min_true_count = min(self.min_true_count, current_tc)
                except ValueError:
                    pass  # Continue even if card depleted
            
            # Update all displays
            self.update_display()
            self.update_flow_display()
            self.update_flow_stats()
            
            messagebox.showinfo("Shoe Loaded", f"Loaded shoe: {self.current_shoe_id}\nCards: {len(self.card_flow)}\nMax RC: {self.max_running_count}, Min RC: {self.min_running_count}\nMax TC: {self.max_true_count:.2f}, Min TC: {self.min_true_count:.2f}\nFinal TC: {self.counter.true_count:.2f}")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load shoe: {e}")
    
    def clear_flow_display(self):
        """Clear the current flow display without saving."""
        if self.flow_recording and self.card_flow:
            result = messagebox.askyesno("Clear Recording", 
                                       f"You have an active recording ({self.current_shoe_id}) with {len(self.card_flow)} cards.\n\nClear without saving?")
            if not result:
                return
        
        # Clear flow data
        self.card_flow = []
        self.current_shoe_id = None
        self.flow_recording = False
        self.max_running_count = 0
        self.min_running_count = 0
        self.max_true_count = 0.0
        self.min_true_count = 0.0
        
        # Update button states
        if hasattr(self, 'start_record_btn'):
            self.start_record_btn.config(state='normal')
        if hasattr(self, 'stop_record_btn'):
            self.stop_record_btn.config(state='disabled')
        if hasattr(self, 'flow_start_btn'):
            self.flow_start_btn.config(state='normal')
        if hasattr(self, 'flow_stop_btn'):
            self.flow_stop_btn.config(state='disabled')
        
        # Reset counter
        self.counter.reset_shoe()
        
        # Update displays
        self.update_display()
        self.update_flow_display()
        self.update_flow_stats()
        
        messagebox.showinfo("Cleared", "Flow display cleared successfully!")

def main():
    """Create and run the GUI application."""
    root = tk.Tk()
    app = BlackjackCounterGUI(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (800 // 2)
    root.geometry(f"1200x800+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()


