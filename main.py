#!/usr/bin/env python3
"""
University Management Ontology System
Main application entry point
"""

import tkinter as tk
from gui.main_window import UniversityManagementApp
import sys

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = UniversityManagementApp(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Handle window closing
    def on_closing():
        if app.confirm_exit():
            root.destroy()
            sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()