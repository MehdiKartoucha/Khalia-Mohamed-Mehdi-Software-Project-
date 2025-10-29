"""
Graphical User Interface for BitPacking Compression.

This module provides a user-friendly GUI using tkinter for compressing
integer arrays and visualizing results.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from src.factory import CompressionFactory
from typing import List


class CompressionGUI:
    """Graphical User Interface for compression operations."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Bit Packing Compression Tool")
        self.root.geometry("1000x700")
        
        # Data storage
        self.original_data = []
        self.compressor = None
        self.compressed_data = []
        
        # Configure style
        self.setup_styles()
        
        # Create main layout
        self.create_widgets()
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='#27ae60')
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🗜️ Bit Packing Compression Tool", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Input Section
        self.create_input_section(main_frame)
        
        # Compression Method Section
        self.create_method_section(main_frame)
        
        # Action Buttons
        self.create_action_buttons(main_frame)
        
        # Results Section (Notebook with tabs)
        self.create_results_section(main_frame)
        
        # Status Bar
        self.create_status_bar(main_frame)
    
    def create_input_section(self, parent):
        """Create data input section."""
        input_frame = ttk.LabelFrame(parent, text="📊 Input Data", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        # Label
        ttk.Label(input_frame, text="Enter integers (space or comma separated):").grid(
            row=0, column=0, sticky=tk.W, pady=5)
        
        # Entry field
        self.data_entry = ttk.Entry(input_frame, font=('Arial', 10))
        self.data_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.data_entry.insert(0, "1 2 3 4 5 6 7 8 9 10")
        
        # Example buttons
        example_frame = ttk.Frame(input_frame)
        example_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(example_frame, text="Small Values", 
                  command=lambda: self.load_example("small")).pack(side=tk.LEFT, padx=2)
        ttk.Button(example_frame, text="With Outliers", 
                  command=lambda: self.load_example("outliers")).pack(side=tk.LEFT, padx=2)
        ttk.Button(example_frame, text="Negative Numbers", 
                  command=lambda: self.load_example("negative")).pack(side=tk.LEFT, padx=2)
        ttk.Button(example_frame, text="Random 100", 
                  command=lambda: self.load_example("random")).pack(side=tk.LEFT, padx=2)
    
    def create_method_section(self, parent):
        """Create compression method selection section."""
        method_frame = ttk.LabelFrame(parent, text="⚙️ Compression Method", padding="10")
        method_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.method_var = tk.StringVar(value="with_overflow")
        
        methods = [
            ("with_overflow", "With Overflow", "Maximum compression (values can span words)"),
            ("no_overflow", "Without Overflow", "Faster random access (values within word boundaries)"),
            ("overflow_area", "With Overflow Area", "Optimal for outliers (separate storage)")
        ]
        
        for i, (value, label, desc) in enumerate(methods):
            rb = ttk.Radiobutton(method_frame, text=label, variable=self.method_var, value=value)
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Label(method_frame, text=desc, style='Info.TLabel').grid(
                row=i, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_action_buttons(self, parent):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(button_frame, text="🗜️ Compress", command=self.compress_data,
                  style='Primary.TButton', width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Compare Methods", command=self.compare_methods,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧪 Test Random Access", command=self.test_random_access,
                  width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Clear", command=self.clear_all,
                  width=10).pack(side=tk.LEFT, padx=5)
    
    def create_results_section(self, parent):
        """Create results display section with tabs."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Tab 1: Text Results
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="📝 Results")
        
        self.results_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                      font=('Courier', 10), height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: Visualization
        vis_frame = ttk.Frame(self.notebook)
        self.notebook.add(vis_frame, text="📊 Visualization")
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=vis_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Tab 3: Comparison
        compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(compare_frame, text="⚖️ Comparison")
        
        self.compare_text = scrolledtext.ScrolledText(compare_frame, wrap=tk.WORD,
                                                      font=('Courier', 10), height=15)
        self.compare_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_bar(self, parent):
        """Create status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E))
    
    def load_example(self, example_type):
        """Load example data."""
        import random
        random.seed(42)
        
        if example_type == "small":
            data = [random.randint(0, 10) for element in range(20)]
        elif example_type == "outliers":
            data = [random.randint(0, 10) for element in range(20)]
            data[5] = 1000
            data[15] = 5000
        elif example_type == "negative":
            data = [random.randint(-50, 50) for element in range(20)]
        elif example_type == "random":
            data = [random.randint(0, 1000) for element in range(100)]
        
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, " ".join(map(str, data)))
        self.status_var.set(f"Loaded {example_type} example with {len(data)} elements")
    
    def parse_input_data(self) -> List[int]:
        """Parse input data from entry field."""
        try:
            text = self.data_entry.get().strip()
            # Handle both space and comma separated
            text = text.replace(',', ' ')
            data = [int(x) for x in text.split()]
            
            if not data:
                raise ValueError("No data entered")
            
            return data
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}\n\nPlease enter integers separated by spaces or commas.")
            return None
    
    def compress_data(self):
        """Perform compression and display results."""
        # Parse input
        data = self.parse_input_data()
        if data is None:
            return
        
        self.original_data = data
        method = self.method_var.get()
        
        try:
            # Create compressor
            self.compressor = CompressionFactory.create(method)
            self.status_var.set(f"Compressing {len(data)} integers using {method}...")
            self.root.update()
            
            # Compress
            self.compressed_data = self.compressor.compress(data)
            info = self.compressor.get_info()
            
            # Display results
            self.display_results(info)
            self.visualize_compression(info)
            
            self.status_var.set(f"✓ Compression complete! Ratio: {info['compression_ratio']:.2f}x")
            self.notebook.select(0)  # Show results tab
            
        except Exception as e:
            messagebox.showerror("Compression Error", f"Error during compression:\n{e}")
            self.status_var.set("❌ Compression failed")
    
    def display_results(self, info):
        """Display compression results in text format."""
        self.results_text.delete('1.0', tk.END)
        
        # Header
        self.results_text.insert(tk.END, "=" * 60 + "\n")
        self.results_text.insert(tk.END, "COMPRESSION RESULTS\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # Original data (truncated if too long)
        data_str = str(self.original_data[:20])
        if len(self.original_data) > 20:
            data_str = data_str[:-1] + ", ...]"
        self.results_text.insert(tk.END, f"Original Data: {data_str}\n\n")
        
        # Statistics
        self.results_text.insert(tk.END, "Statistics:\n")
        self.results_text.insert(tk.END, "-" * 60 + "\n")
        self.results_text.insert(tk.END, f"  Original Length:    {info['original_length']} integers\n")
        self.results_text.insert(tk.END, f"  Compressed Length:  {info['compressed_length']} integers\n")
        self.results_text.insert(tk.END, f"  Bits per Value:     {info['bits_per_value']} bits\n")
        self.results_text.insert(tk.END, f"  Original Size:      {info['original_bits']} bits\n")
        self.results_text.insert(tk.END, f"  Compressed Size:    {info['compressed_bits']} bits\n")
        self.results_text.insert(tk.END, f"  Compression Ratio:  {info['compression_ratio']:.2f}x\n")
        self.results_text.insert(tk.END, f"  Space Saved:        {(1 - 1/info['compression_ratio'])*100:.1f}%\n\n")
        
        # Additional info for specific methods
        if 'values_per_int' in info:
            self.results_text.insert(tk.END, f"  Values per Integer: {info['values_per_int']}\n")
            self.results_text.insert(tk.END, f"  Wasted Bits/Int:    {info['wasted_bits_per_int']}\n\n")
        
        if info.get('has_overflow_area'):
            self.results_text.insert(tk.END, f"  Overflow Area:      YES\n")
            self.results_text.insert(tk.END, f"  Overflow Items:     {info['overflow_area_size']}\n\n")
        
        # Compressed data (truncated if too long)
        comp_str = str(self.compressed_data[:10])
        if len(self.compressed_data) > 10:
            comp_str = comp_str[:-1] + ", ...]"
        self.results_text.insert(tk.END, f"Compressed Data: {comp_str}\n\n")
        
        # Verification
        decompressed = self.compressor.decompress(self.compressed_data)
        match = decompressed == self.original_data
        self.results_text.insert(tk.END, f"Decompression Check: {'✓ PASSED' if match else '✗ FAILED'}\n")
    
    def visualize_compression(self, info):
        """Visualize compression results."""
        self.fig.clear()
        
        # Create subplots
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        ax1 = self.fig.add_subplot(gs[0, 0])
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax3 = self.fig.add_subplot(gs[1, :])
        
        # 1. Size comparison bar chart
        sizes = [info['original_bits'], info['compressed_bits']]
        labels = ['Original', 'Compressed']
        colors = ['#3498db', '#2ecc71']
        
        ax1.bar(labels, sizes, color=colors)
        ax1.set_ylabel('Size (bits)')
        ax1.set_title('Size Comparison')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar_index, bar_value in enumerate(sizes):
            ax1.text(bar_index, bar_value + max(sizes)*0.02, str(bar_value), ha='center', va='bottom')
        
        # 2. Compression ratio pie chart
        saved = info['original_bits'] - info['compressed_bits']
        sizes_pie = [info['compressed_bits'], saved]
        labels_pie = [f'Compressed\n({info["compressed_bits"]} bits)', 
                     f'Saved\n({saved} bits)']
        colors_pie = ['#2ecc71', '#e74c3c']
        
        ax2.pie(sizes_pie, labels=labels_pie, colors=colors_pie, autopct='%1.1f%%',
               startangle=90)
        ax2.set_title(f'Space Savings: {info["compression_ratio"]:.2f}x')
        
        # 3. Data distribution
        if len(self.original_data) <= 100:
            ax3.plot(self.original_data, marker='o', linestyle='-', markersize=4, 
                    linewidth=1, color='#3498db')
            ax3.set_xlabel('Index')
            ax3.set_ylabel('Value')
            ax3.set_title('Original Data Distribution')
            ax3.grid(True, alpha=0.3)
        else:
            # Histogram for large datasets
            ax3.hist(self.original_data, bins=30, color='#3498db', edgecolor='black', alpha=0.7)
            ax3.set_xlabel('Value')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Value Distribution')
            ax3.grid(axis='y', alpha=0.3)
        
        self.canvas.draw()
    
    def compare_methods(self):
        """Compare all compression methods."""
        data = self.parse_input_data()
        if data is None:
            return
        
        self.status_var.set("Comparing compression methods...")
        self.root.update()
        
        methods = ["with_overflow", "no_overflow", "overflow_area"]
        results = {}
        
        try:
            for method_name in methods:
                compressor = CompressionFactory.create(method_name)
                compressed = compressor.compress(data)
                info = compressor.get_info()
                results[method_name] = info
            
            # Display comparison
            self.display_comparison(results)
            self.notebook.select(2)  # Show comparison tab
            self.status_var.set("✓ Comparison complete!")
            
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Error during comparison:\n{e}")
            self.status_var.set("❌ Comparison failed")
    
    def display_comparison(self, results):
        """Display comparison results."""
        self.compare_text.delete('1.0', tk.END)
        
        # Header
        self.compare_text.insert(tk.END, "=" * 70 + "\n")
        self.compare_text.insert(tk.END, "COMPRESSION METHOD COMPARISON\n")
        self.compare_text.insert(tk.END, "=" * 70 + "\n\n")
        
        self.compare_text.insert(tk.END, f"Data Size: {results['with_overflow']['original_length']} integers\n")
        self.compare_text.insert(tk.END, f"Original Size: {results['with_overflow']['original_bits']} bits\n\n")
        
        # Table header
        self.compare_text.insert(tk.END, f"{'Method':<25} {'Comp.Size':<12} {'Bits/Val':<10} {'Ratio':<10} {'Saved':<10}\n")
        self.compare_text.insert(tk.END, "-" * 70 + "\n")
        
        # Table rows
        for method_name, method_info in results.items():
            saved_pct = (1 - 1/method_info['compression_ratio']) * 100
            self.compare_text.insert(tk.END, 
                f"{method_name:<25} {method_info['compressed_length']:<12} {method_info['bits_per_value']:<10} "
                f"{method_info['compression_ratio']:<10.2f} {saved_pct:<10.1f}%\n")
        
        self.compare_text.insert(tk.END, "\n")
        
        # Winner analysis
        best_ratio = max(results.items(), key=lambda x: x[1]['compression_ratio'])
        self.compare_text.insert(tk.END, f"🏆 Best Compression: {best_ratio[0]} ({best_ratio[1]['compression_ratio']:.2f}x)\n\n")
        
        # Detailed info
        self.compare_text.insert(tk.END, "Detailed Information:\n")
        self.compare_text.insert(tk.END, "-" * 70 + "\n")
        
        for method_name, method_info in results.items():
            self.compare_text.insert(tk.END, f"\n{method_name.upper()}:\n")
            self.compare_text.insert(tk.END, f"  Compressed: {method_info['compressed_length']} integers ({method_info['compressed_bits']} bits)\n")
            self.compare_text.insert(tk.END, f"  Bits per value: {method_info['bits_per_value']}\n")
            
            if 'has_overflow_area' in method_info and method_info['has_overflow_area']:
                self.compare_text.insert(tk.END, f"  Uses overflow area: {method_info['overflow_area_size']} items\n")
    
    def test_random_access(self):
        """Test random access functionality."""
        if not self.compressor or not self.original_data:
            messagebox.showwarning("No Data", "Please compress data first!")
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Random Access Test")
        popup.geometry("500x400")
        
        # Frame
        frame = ttk.Frame(popup, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(frame, text="Enter an index to retrieve (0-based):", 
                 style='Subtitle.TLabel').pack(pady=10)
        
        # Index entry
        index_frame = ttk.Frame(frame)
        index_frame.pack(pady=10)
        
        ttk.Label(index_frame, text="Index:").pack(side=tk.LEFT, padx=5)
        index_entry = ttk.Entry(index_frame, width=10)
        index_entry.pack(side=tk.LEFT, padx=5)
        index_entry.insert(0, "0")
        
        # Results text
        result_text = scrolledtext.ScrolledText(frame, height=10, width=50, font=('Courier', 10))
        result_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        def retrieve_value():
            try:
                idx = int(index_entry.get())
                if idx < 0 or idx >= len(self.original_data):
                    messagebox.showerror("Index Error", 
                                       f"Index must be between 0 and {len(self.original_data)-1}")
                    return
                
                value = self.compressor.get(idx)
                expected = self.original_data[idx]
                
                result_text.insert(tk.END, f"\n{'='*40}\n")
                result_text.insert(tk.END, f"Index: {idx}\n")
                result_text.insert(tk.END, f"Retrieved Value: {value}\n")
                result_text.insert(tk.END, f"Expected Value:  {expected}\n")
                result_text.insert(tk.END, f"Match: {'✓ YES' if value == expected else '✗ NO'}\n")
                result_text.see(tk.END)
                
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid integer index")
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Retrieve", command=retrieve_value).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=popup.destroy).pack(side=tk.LEFT, padx=5)
        
        # Info
        info_text = f"Data range: 0 to {len(self.original_data)-1} ({len(self.original_data)} elements)"
        ttk.Label(frame, text=info_text, style='Info.TLabel').pack()
    
    def clear_all(self):
        """Clear all data and results."""
        self.original_data = []
        self.compressor = None
        self.compressed_data = []
        self.results_text.delete('1.0', tk.END)
        self.compare_text.delete('1.0', tk.END)
        self.fig.clear()
        self.canvas.draw()
        self.status_var.set("Cleared")


def launch_gui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = CompressionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
