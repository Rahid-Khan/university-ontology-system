"""
Instances tab implementation
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from config.settings import Colors, Fonts
from gui.widgets import ToolTip

class InstancesTab(ttk.Frame):
    """Instances tab showing ontology instances"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_filter = "All"
        self.create_widgets()
        
    def create_widgets(self):
        """Create instances tab widgets"""
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Class filter
        ttk.Label(control_frame, text="Filter by Class:").pack(side=tk.LEFT, padx=5)
        
        self.class_filter_var = tk.StringVar(value="All")
        self.class_filter_combo = ttk.Combobox(control_frame,
                                              textvariable=self.class_filter_var,
                                              width=25, state='readonly')
        self.class_filter_combo.pack(side=tk.LEFT, padx=5)
        self.class_filter_combo.bind('<<ComboboxSelected>>', self.on_class_filter)
        
        # Search
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var,
                                width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="Add Instance",
                  command=self.add_instance).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Delete Instance",
                  command=self.delete_instance).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Refresh",
                  command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Export",
                  command=self.export_instances).pack(side=tk.LEFT, padx=2)
        
        # Main content
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Class', 'Name', 'ID', 'Description')
        self.tree = ttk.Treeview(tree_frame, columns=columns,
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
        self.tree.column('#0', width=150, minwidth=100, stretch=tk.NO)
        self.tree.column('Class', width=150, minwidth=100, stretch=tk.NO)
        self.tree.column('Name', width=200, minwidth=150, stretch=tk.YES)
        self.tree.column('ID', width=100, minwidth=80, stretch=tk.NO)
        self.tree.column('Description', width=300, minwidth=200, stretch=tk.YES)
        
        # Configure headings
        self.tree.heading('#0', text='Instance', anchor=tk.W)
        self.tree.heading('Class', text='Class', anchor=tk.W)
        self.tree.heading('Name', text='Name', anchor=tk.W)
        self.tree.heading('ID', text='ID', anchor=tk.W)
        self.tree.heading('Description', text='Description', anchor=tk.W)
        
        # Bind events
        self.tree.bind('<Double-Button-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Details panel
        self.create_details_panel(main_frame)
        
        # Load class filter and instances
        self.load_class_filter()
        self.refresh()
        
    def create_details_panel(self, parent):
        """Create details panel"""
        details_frame = ttk.LabelFrame(parent, text="Instance Details", padding=10)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Details text
        self.details_text = tk.Text(details_frame, height=8, wrap=tk.WORD,
                                   font=('Arial', 9))
        scrollbar = ttk.Scrollbar(details_frame, command=self.details_text.yview)
        self.details_text.config(yscrollcommand=scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Make read-only
        self.details_text.config(state=tk.DISABLED)
        
    def load_class_filter(self):
        """Load classes into filter combobox"""
        query = """
        SELECT ?class
        WHERE {
            ?class rdf:type owl:Class .
        }
        ORDER BY ?class
        """
        
        try:
            results = self.app.ontology.query(query)
            classes = ["All"]
            
            for row in results:
                class_uri = str(row['class'])
                class_name = class_uri.split('#')[-1]
                classes.append(class_name)
                
            self.class_filter_combo['values'] = classes
            self.class_filter_var.set("All")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load classes: {str(e)}")
            
    def on_class_filter(self, event=None):
        """Handle class filter change"""
        self.current_filter = self.class_filter_var.get()
        self.refresh()
        
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
            instance_name = self.tree.item(item, 'text').lower()
            class_name = self.tree.item(item, 'values')[0].lower() if self.tree.item(item, 'values') else ""
            
            if (search_term in instance_name or 
                search_term in class_name):
                self.tree.item(item, tags=('match',))
            else:
                self.tree.item(item, tags=('no_match',))
                self.tree.detach(item)
                
    def on_item_double_click(self, event):
        """Handle double click on item"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            instance_id = self.tree.item(item, 'text')
            self.show_instance_details(instance_id)
            
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            instance_id = self.tree.item(item, 'text')
            self.update_details(instance_id)
            
    def show_instance_details(self, instance_id):
        """Show detailed information about an instance"""
        # Get instance details
        query = f"""
        SELECT ?property ?value
        WHERE {{
            univ:{instance_id} ?property ?value .
            FILTER (isLiteral(?value))
        }}
        """
        
        try:
            results = self.app.ontology.query(query)
            
            details = f"Instance: {instance_id}\n\n"
            details += "Properties:\n"
            details += "-" * 40 + "\n"
            
            for row in results:
                prop_name = str(row['property']).split('#')[-1]
                value = str(row['value'])
                details += f"{prop_name}: {value}\n"
                
            # Get relationships
            rel_query = f"""
            SELECT ?property ?object
            WHERE {{
                univ:{instance_id} ?property ?object .
                FILTER (isURI(?object))
            }}
            """
            
            rel_results = self.app.ontology.query(rel_query)
            
            if rel_results:
                details += "\nRelationships:\n"
                details += "-" * 40 + "\n"
                
                for row in rel_results:
                    prop_name = str(row['property']).split('#')[-1]
                    object_ = str(row['object']).split('#')[-1]
                    details += f"{prop_name}: {object_}\n"
                    
            messagebox.showinfo("Instance Details", details)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load details: {str(e)}")
            
    def update_details(self, instance_id):
        """Update details panel with instance information"""
        # Get instance details
        query = f"""
        SELECT ?class ?property ?value
        WHERE {{
            univ:{instance_id} rdf:type ?class .
            FILTER (?class != owl:NamedIndividual)
            OPTIONAL {{
                univ:{instance_id} ?property ?value .
                FILTER (isLiteral(?value))
            }}
        }}
        """
        
        try:
            results = list(self.app.ontology.query(query))
            
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            
            if results:
                class_uri = str(results[0]['class'])
                class_name = class_uri.split('#')[-1]
                
                details = f"Instance: {instance_id}\n"
                details += f"Class: {class_name}\n\n"
                details += "Properties:\n"
                
                properties_shown = set()
                for row in results:
                    if 'property' in row and 'value' in row:
                        prop_name = str(row['property']).split('#')[-1]
                        if prop_name not in properties_shown:
                            value = str(row['value'])
                            details += f"  {prop_name}: {value}\n"
                            properties_shown.add(prop_name)
                            
                # Get relationships count
                rel_query = f"""
                SELECT (COUNT(?property) as ?count)
                WHERE {{
                    univ:{instance_id} ?property ?object .
                    FILTER (isURI(?object))
                }}
                """
                
                rel_results = list(self.app.ontology.query(rel_query))
                rel_count = int(rel_results[0]['count']) if rel_results else 0
                
                details += f"\nRelationships: {rel_count}"
                
                self.details_text.insert(1.0, details)
            else:
                self.details_text.insert(1.0, f"Instance not found: {instance_id}")
                
            self.details_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, f"Error loading details: {str(e)}")
            self.details_text.config(state=tk.DISABLED)
            
    def refresh(self):
        """Refresh instances tree"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Build query based on filter
        if self.current_filter == "All":
            query = """
            SELECT ?instance ?class ?name
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                ?instance rdf:type ?class .
                FILTER (?class != owl:NamedIndividual)
                OPTIONAL { ?instance univ:name ?name }
            }
            ORDER BY ?class ?instance
            """
        else:
            class_uri = self.app.ontology.univ_ns[self.current_filter]
            query = f"""
            SELECT ?instance ?name
            WHERE {{
                ?instance rdf:type owl:NamedIndividual .
                ?instance rdf:type <{class_uri}> .
                OPTIONAL {{ ?instance univ:name ?name }}
            }}
            ORDER BY ?instance
            """
            
        try:
            results = self.app.ontology.query(query, limit=500)
            
            for row in results:
                instance_uri = str(row['instance'])
                instance_id = instance_uri.split('#')[-1]
                
                if self.current_filter == "All":
                    class_uri = str(row['class'])
                    class_name = class_uri.split('#')[-1]
                else:
                    class_name = self.current_filter
                    
                name = str(row['name']) if row.get('name') else ""
                
                # Get ID property
                id_query = f"""
                SELECT ?id
                WHERE {{
                    <{instance_uri}> univ:id ?id .
                }}
                LIMIT 1
                """
                
                id_results = list(self.app.ontology.query(id_query))
                instance_id_display = str(id_results[0]['id']) if id_results else instance_id
                
                # Get description
                desc_query = f"""
                SELECT ?description
                WHERE {{
                    <{instance_uri}> univ:description ?description .
                }}
                LIMIT 1
                """
                
                desc_results = list(self.app.ontology.query(desc_query))
                description = str(desc_results[0]['description']) if desc_results else ""
                
                # Insert into tree
                self.tree.insert('', tk.END, text=instance_id,
                               values=(class_name, name, instance_id_display, description))
                               
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load instances: {str(e)}")
            
    def add_instance(self):
        """Add new instance"""
        self.app.open_add_instance()
        
    def delete_instance(self):
        """Delete selected instance(s)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select instance(s) to delete")
            return
            
        instances = []
        for item in selection:
            instance_id = self.tree.item(item, 'text')
            instances.append(instance_id)
            
        if len(instances) == 1:
            message = f"Delete instance '{instances[0]}'?"
        else:
            message = f"Delete {len(instances)} instances?"
            
        confirm = messagebox.askyesno("Confirm Delete", message)
        
        if confirm:
            try:
                deleted_count = 0
                for instance_id in instances:
                    count = self.app.ontology.remove_instance(instance_id)
                    deleted_count += count
                    
                self.refresh()
                messagebox.showinfo("Success", 
                                  f"Deleted {deleted_count} triples for {len(instances)} instance(s)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete instance(s): {str(e)}")
                
    def export_instances(self):
        """Export instances to file"""
        from tkinter import filedialog
        import csv
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            title="Export Instances"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(['Instance', 'Class', 'Name', 'ID', 'Description'])
                    
                    # Write data
                    for item in self.tree.get_children():
                        instance = self.tree.item(item, 'text')
                        values = self.tree.item(item, 'values')
                        writer.writerow([instance] + list(values))
                        
                messagebox.showinfo("Success", f"Instances exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
                
    def on_tab_selected(self):
        """Called when tab is selected"""
        self.refresh()
        
    def delete_selected(self):
        """Delete selected items"""
        self.delete_instance()