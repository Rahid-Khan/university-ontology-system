"""
Dashboard tab implementation
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from config.settings import Colors, Fonts
from gui.widgets import CardWidget, StatWidget, RecentActivityWidget

class DashboardTab(ttk.Frame):
    """Dashboard tab showing overview and quick actions"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """Create dashboard widgets"""
        # Create scrollable canvas
        canvas = tk.Canvas(self, bg=Colors.DARK)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(header_frame,
                               text="University Management Ontology Dashboard",
                               style='Title.TLabel')
        title_label.pack(pady=10)
        
        subtitle_label = ttk.Label(header_frame,
                                  text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=5)
        
        # Statistics cards
        self.create_statistics_cards(scrollable_frame)
        
        # Quick actions
        self.create_quick_actions(scrollable_frame)
        
        # Recent activity
        self.create_recent_activity(scrollable_frame)
        
        # System status
        self.create_system_status(scrollable_frame)
        
    def create_statistics_cards(self, parent):
        """Create statistics cards"""
        stats_frame = ttk.LabelFrame(parent, text="Ontology Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Get statistics
        stats = self.app.ontology.get_statistics()
        
        # Create stat cards
        stats_data = [
            ("Classes", stats['classes'], Colors.PRIMARY, "Total classes in ontology"),
            ("Instances", stats['instances'], Colors.SUCCESS, "Total instances"),
            ("Relationships", stats['relationships'], Colors.WARNING, "Total relationships"),
            ("Properties", stats['object_properties'] + stats['data_properties'],
             Colors.ACCENT, "Object + Data properties")
        ]
        
        for i, (title, value, color, description) in enumerate(stats_data):
            card = StatWidget(stats_frame, title, value, color, description)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            stats_frame.columnconfigure(i, weight=1)
            
    def create_quick_actions(self, parent):
        """Create quick actions section"""
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        actions = [
            ("Add Student", self.app.open_add_instance, Colors.SUCCESS),
            ("Add Professor", self.app.open_add_instance, Colors.PRIMARY),
            ("Add Course", self.app.open_add_instance, Colors.WARNING),
            ("Run Query", self.app.open_sparql_editor, Colors.INFO),
            ("View Graph", self.app.show_instance_graph, Colors.ACCENT),
            ("Export Data", self.app.export_turtle, Colors.SECONDARY),
            ("Statistics", self.app.show_statistics, Colors.INFO),
            ("Refresh All", self.app.refresh_all_views, Colors.WARNING)
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = ttk.Button(actions_frame, text=text,
                           command=lambda c=command: c(),
                           style='Primary.TButton')
            btn.grid(row=i // 4, column=i % 4, padx=5, pady=5, sticky='ew')
            actions_frame.columnconfigure(i % 4, weight=1)
            
    def create_recent_activity(self, parent):
        """Create recent activity section"""
        activity_frame = ttk.LabelFrame(parent, text="Recent Activity", padding=10)
        activity_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create recent activity widget
        self.activity_widget = RecentActivityWidget(activity_frame)
        self.activity_widget.pack(fill=tk.X, expand=True)
        
        # Add sample activities
        sample_activities = [
            ("Added new course", "CS401 - Machine Learning", "2 minutes ago"),
            ("Updated student record", "Alice Johnson - GPA updated", "5 minutes ago"),
            ("Added relationship", "ProfSmith teaches CS301", "10 minutes ago"),
            ("Exported data", "Ontology exported as Turtle", "15 minutes ago")
        ]
        
        for activity, details, time in sample_activities:
            self.activity_widget.add_activity(activity, details, time)
            
    def create_system_status(self, parent):
        """Create system status section"""
        status_frame = ttk.LabelFrame(parent, text="System Status", padding=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_items = [
            ("Ontology Status", "Healthy", Colors.SUCCESS),
            ("Memory Usage", "45%", Colors.INFO),
            ("Query Cache", "Enabled", Colors.SUCCESS),
            ("Visualization Engine", "Ready", Colors.SUCCESS)
        ]
        
        for i, (label, value, color) in enumerate(status_items):
            frame = ttk.Frame(status_frame)
            frame.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky='ew')
            
            ttk.Label(frame, text=label, font=Fonts.BODY).pack(anchor=tk.W)
            ttk.Label(frame, text=value, font=Fonts.HEADING,
                     foreground=color).pack(anchor=tk.W)
                     
    def on_tab_selected(self):
        """Called when tab is selected"""
        self.refresh()
        
    def refresh(self):
        """Refresh dashboard data"""
        # Update statistics
        if hasattr(self, 'activity_widget'):
            self.activity_widget.clear()
            # Add new activities here if tracking was implemented
            
        # Update status bar via main app
        self.app.update_status_bar()