"""
Custom GUI widgets
"""

import tkinter as tk
from tkinter import ttk
from config.settings import Colors, Fonts

class ToolTip:
    """Create a tooltip for a given widget"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
        
    def show_tooltip(self, event=None):
        """Show tooltip"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.text, 
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=('TkDefaultFont', 8))
        label.pack()
        
    def hide_tooltip(self, event=None):
        """Hide tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class CardWidget(ttk.Frame):
    """Card widget for displaying information"""
    
    def __init__(self, parent, title, content, color=Colors.PRIMARY):
        super().__init__(parent, style='Card.TFrame')
        self.title = title
        self.content = content
        self.color = color
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create card widgets"""
        # Title
        title_label = ttk.Label(self, text=self.title,
                               font=Fonts.HEADING,
                               foreground=self.color)
        title_label.pack(pady=(10, 5))
        
        # Separator
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=10)
        
        # Content
        content_label = ttk.Label(self, text=self.content,
                                 font=Fonts.BODY,
                                 wraplength=200)
        content_label.pack(pady=10, padx=10)
        
class StatWidget(ttk.Frame):
    """Statistics widget"""
    
    def __init__(self, parent, title, value, color, description=""):
        # Use tk.Frame instead of ttk.Frame to support background color
        super().__init__(parent, relief=tk.RAISED, borderwidth=2)
        self.title = title
        self.value = value
        self.color = color
        self.description = description
        
        # Convert to tk.Frame for background color support
        self.tk_frame = tk.Frame(self, bg=self.color, relief=tk.RAISED, borderwidth=2)
        self.tk_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create stat widget"""
        # Value
        value_label = tk.Label(self.tk_frame, text=str(self.value),
                              font=('Helvetica', 24, 'bold'),
                              background=self.color,
                              foreground='white')
        value_label.pack(pady=(10, 5))
        
        # Title
        title_label = tk.Label(self.tk_frame, text=self.title,
                              font=('Helvetica', 10),
                              background=self.color,
                              foreground='white')
        title_label.pack(pady=(0, 10))
        
        # Description tooltip
        if self.description:
            ToolTip(self.tk_frame, self.description)

class RecentActivityWidget(ttk.Frame):
    """Recent activity widget"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.activities = []
        self.create_widgets()
        
    def create_widgets(self):
        """Create activity widget"""
        # Treeview for activities
        self.tree = ttk.Treeview(self, columns=('Time', 'Details'), 
                                show='tree headings', height=6)
        
        self.tree.heading('#0', text='Activity')
        self.tree.heading('Time', text='Time')
        self.tree.heading('Details', text='Details')
        
        self.tree.column('#0', width=150)
        self.tree.column('Time', width=100)
        self.tree.column('Details', width=200)
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def add_activity(self, activity, details, time):
        """Add activity to list"""
        item_id = self.tree.insert('', 'end', text=activity,
                                  values=(time, details))
        self.activities.append((activity, details, time))
        
        # Keep only last 10 activities
        if len(self.activities) > 10:
            oldest = self.tree.get_children()[0]
            self.tree.delete(oldest)
            self.activities.pop(0)
            
    def clear(self):
        """Clear all activities"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.activities.clear()