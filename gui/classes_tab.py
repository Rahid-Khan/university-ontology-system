"""
Classes tab implementation
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from config.settings import Colors, Fonts
from gui.widgets import ToolTip

class ClassesTab(ttk.Frame):
    """Classes tab showing ontology classes"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """Create classes tab widgets"""
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var,
                                width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # Show instances checkbox
        self.show_instances_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Show Instance Count",
                       variable=self.show_instances_var,
                       command=self.refresh).pack(side=tk.LEFT, padx=20)
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh",
                  command=self.refresh).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="Add Class",
                  command=self.add_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Delete Class",
                  command=self.delete_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="View Hierarchy",
                  command=self.view_hierarchy).pack(side=tk.LEFT, padx=2)
        
        # Main content
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=('Description', 'Instances', 'Subclasses'),
                                selectmode='extended')
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configure grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure columns
        self.tree.column('#0', width=200, minwidth=150, stretch=tk.YES)
        self.tree.column('Description', width=300, minwidth=200, stretch=tk.YES)
        self.tree.column('Instances', width=100, minwidth=80, stretch=tk.NO)
        self.tree.column('Subclasses', width=100, minwidth=80, stretch=tk.NO)
        
        # Configure headings
        self.tree.heading('#0', text='Class Name', anchor=tk.W)
        self.tree.heading('Description', text='Description', anchor=tk.W)
        self.tree.heading('Instances', text='Instances', anchor=tk.W)
        self.tree.heading('Subclasses', text='Subclasses', anchor=tk.W)
        
        # Bind events
        self.tree.bind('<Double-Button-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Details panel
        self.create_details_panel(main_frame)
        
        # Populate tree
        self.refresh()
        
    def create_details_panel(self, parent):
        """Create details panel"""
        details_frame = ttk.LabelFrame(parent, text="Class Details", padding=10)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Details text
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD,
                                   font=('Arial', 9))
        scrollbar = ttk.Scrollbar(details_frame, command=self.details_text.yview)
        self.details_text.config(yscrollcommand=scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Make read-only
        self.details_text.config(state=tk.DISABLED)
        
    def on_search(self, event=None):
        """Handle search"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Show all items
            for item in self.tree.get_children():
                self.tree.item(item, tags=())
            return
            
        # Hide non-matching items
        for item in self.tree.get_children():
            text = self.tree.item(item, 'text').lower()
            if search_term in text:
                self.tree.item(item, tags=('match',))
            else:
                self.tree.item(item, tags=('no_match',))
                self.tree.detach(item)
                
    def on_item_double_click(self, event):
        """Handle double click on item"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            class_name = self.tree.item(item, 'text')
            self.show_class_details(class_name)
            
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            class_name = self.tree.item(item, 'text')
            self.update_details(class_name)
            
    def show_class_details(self, class_name):
        """Show detailed information about a class"""
        # This could open a separate dialog with more details
        messagebox.showinfo("Class Details", 
                           f"Showing details for class: {class_name}\n\n"
                           "Detailed information would appear here.")
                           
    def update_details(self, class_name):
        """Update details panel with class information"""
        # Get class details from ontology
        query = f"""
        SELECT ?comment
        WHERE {{
            univ:{class_name} rdfs:comment ?comment .
        }}
        """
        
        try:
            results = list(self.app.ontology.query(query))
            comment = str(results[0]['comment']) if results else "No description available"
            
            # Get instance count
            instance_query = f"""
            SELECT (COUNT(?instance) as ?count)
            WHERE {{
                ?instance rdf:type univ:{class_name} .
                ?instance rdf:type owl:NamedIndividual .
            }}
            """
            
            instance_results = list(self.app.ontology.query(instance_query))
            instance_count = int(instance_results[0]['count']) if instance_results else 0
            
            # Get subclass count
            subclass_query = f"""
            SELECT (COUNT(?subclass) as ?count)
            WHERE {{
                ?subclass rdfs:subClassOf univ:{class_name} .
            }}
            """
            
            subclass_results = list(self.app.ontology.query(subclass_query))
            subclass_count = int(subclass_results[0]['count']) if subclass_results else 0
            
            # Update details text
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            
            details = f"Class: {class_name}\n"
            details += f"Instances: {instance_count}\n"
            details += f"Subclasses: {subclass_count}\n"
            details += f"\nDescription:\n{comment}"
            
            self.details_text.insert(1.0, details)
            self.details_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, f"Error loading details: {str(e)}")
            self.details_text.config(state=tk.DISABLED)
            
    def refresh(self):
        """Refresh classes tree"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get classes from ontology
        query = """
        SELECT ?class ?comment
        WHERE {
            ?class rdf:type owl:Class .
            OPTIONAL { ?class rdfs:comment ?comment }
        }
        ORDER BY ?class
        """
        
        try:
            results = self.app.ontology.query(query)
            
            for row in results:
                class_uri = str(row['class'])
                class_name = class_uri.split('#')[-1]
                comment = str(row['comment']) if row['comment'] else ""
                
                # Get instance count if requested
                instance_count = 0
                if self.show_instances_var.get():
                    instance_query = f"""
                    SELECT (COUNT(?instance) as ?count)
                    WHERE {{
                        ?instance rdf:type <{class_uri}> .
                        ?instance rdf:type owl:NamedIndividual .
                    }}
                    """
                    
                    instance_results = list(self.app.ontology.query(instance_query))
                    if instance_results:
                        instance_count = int(instance_results[0]['count'])
                        
                # Get subclass count
                subclass_query = f"""
                SELECT (COUNT(?subclass) as ?count)
                WHERE {{
                    ?subclass rdfs:subClassOf <{class_uri}> .
                }}
                """
                
                subclass_results = list(self.app.ontology.query(subclass_query))
                subclass_count = int(subclass_results[0]['count']) if subclass_results else 0
                
                # Insert into tree
                self.tree.insert('', tk.END, text=class_name,
                               values=(comment, instance_count, subclass_count))
                               
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load classes: {str(e)}")
            
    def add_class(self):
        """Add new class"""
        from gui.dialogs import BaseDialog
        import tkinter.simpledialog as sd
        
        class_name = sd.askstring("Add Class", "Enter class name:")
        if class_name:
            description = sd.askstring("Add Class", "Enter description (optional):")
            
            try:
                # In a real implementation, you would add the class to the ontology
                # For now, just show a message
                messagebox.showinfo("Info", 
                                  f"Class '{class_name}' would be added to ontology.\n"
                                  "Implementation pending.")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add class: {str(e)}")
                
    def delete_class(self):
        """Delete selected class"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a class to delete")
            return
            
        item = selection[0]
        class_name = self.tree.item(item, 'text')
        
        confirm = messagebox.askyesno("Confirm Delete",
                                     f"Delete class '{class_name}'?\n\n"
                                     "Warning: This will also delete all instances of this class!")
        
        if confirm:
            try:
                # In a real implementation, you would delete the class from ontology
                # For now, just show a message
                messagebox.showinfo("Info",
                                  f"Class '{class_name}' would be deleted.\n"
                                  "Implementation pending.")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete class: {str(e)}")
                
    def view_hierarchy(self):
        """View class hierarchy"""
        self.app.show_hierarchy()
        
    def on_tab_selected(self):
        """Called when tab is selected"""
        self.refresh()
        
    def delete_selected(self):
        """Delete selected items"""
        self.delete_class()