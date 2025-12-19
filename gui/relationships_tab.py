"""
Relationships tab implementation
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from config.settings import Colors, Fonts
from gui.widgets import ToolTip

class RelationshipsTab(ttk.Frame):
    """Relationships tab showing ontology relationships"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.create_widgets()
        
    def create_widgets(self):
        """Create relationships tab widgets"""
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Filter by relationship type
        ttk.Label(control_frame, text="Relationship Type:").pack(side=tk.LEFT, padx=5)
        
        self.rel_type_var = tk.StringVar(value="All")
        self.rel_type_combo = ttk.Combobox(control_frame,
                                          textvariable=self.rel_type_var,
                                          width=20, state='readonly')
        self.rel_type_combo.pack(side=tk.LEFT, padx=5)
        self.rel_type_combo.bind('<<ComboboxSelected>>', self.on_rel_type_filter)
        
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
        
        ttk.Button(action_frame, text="Add Relationship",
                  command=self.add_relationship).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Delete Relationship",
                  command=self.delete_relationship).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Refresh",
                  command=self.refresh).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Visualize",
                  command=self.visualize_relationships).pack(side=tk.LEFT, padx=2)
        
        # Main content
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame, columns=('Subject', 'Predicate', 'Object'),
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
        self.tree.column('#0', width=50, minwidth=40, stretch=tk.NO)
        self.tree.column('Subject', width=200, minwidth=150, stretch=tk.YES)
        self.tree.column('Predicate', width=150, minwidth=120, stretch=tk.YES)
        self.tree.column('Object', width=200, minwidth=150, stretch=tk.YES)
        
        # Configure headings
        self.tree.heading('#0', text='#', anchor=tk.W)
        self.tree.heading('Subject', text='Subject', anchor=tk.W)
        self.tree.heading('Predicate', text='Relationship', anchor=tk.W)
        self.tree.heading('Object', text='Object', anchor=tk.W)
        
        # Bind events
        self.tree.bind('<Double-Button-1>', self.on_item_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        
        # Statistics panel
        self.create_statistics_panel(main_frame)
        
        # Load relationship types and data
        self.load_relationship_types()
        self.refresh()
        
    def create_statistics_panel(self, parent):
        """Create statistics panel"""
        stats_frame = ttk.LabelFrame(parent, text="Relationship Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create grid for statistics
        self.stats_labels = {}
        
        for i, (label, key) in enumerate([
            ("Total Relationships:", "total"),
            ("Most Common Type:", "most_common"),
            ("Average per Subject:", "avg_per_subject"),
            ("Maximum per Subject:", "max_per_subject")
        ]):
            ttk.Label(stats_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.stats_labels[key] = ttk.Label(stats_frame, text="", font=Fonts.BODY)
            self.stats_labels[key].grid(row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0))
            
    def load_relationship_types(self):
        """Load relationship types into combobox"""
        query = """
        SELECT ?predicate
        WHERE {
            ?predicate rdf:type owl:ObjectProperty .
        }
        ORDER BY ?predicate
        """
        
        try:
            results = self.app.ontology.query(query)
            rel_types = ["All"]
            
            for row in results:
                predicate_uri = str(row['predicate'])
                predicate_name = predicate_uri.split('#')[-1]
                rel_types.append(predicate_name)
                
            self.rel_type_combo['values'] = rel_types
            self.rel_type_var.set("All")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load relationship types: {str(e)}")
            
    def on_rel_type_filter(self, event=None):
        """Handle relationship type filter change"""
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
            values = self.tree.item(item, 'values')
            if values and len(values) >= 3:
                subject = values[0].lower()
                predicate = values[1].lower()
                object_ = values[2].lower()
                
                if (search_term in subject or 
                    search_term in predicate or 
                    search_term in object_):
                    self.tree.item(item, tags=('match',))
                else:
                    self.tree.item(item, tags=('no_match',))
                    self.tree.detach(item)
                    
    def on_item_double_click(self, event):
        """Handle double click on item"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values and len(values) >= 3:
                subject, predicate, object_ = values[:3]
                self.show_relationship_details(subject, predicate, object_)
                
    def on_item_select(self, event):
        """Handle item selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values and len(values) >= 3:
                subject, predicate, object_ = values[:3]
                self.update_statistics()
                
    def show_relationship_details(self, subject, predicate, object_):
        """Show detailed information about a relationship"""
        details = f"Relationship Details\n"
        details += "=" * 40 + "\n\n"
        details += f"Subject: {subject}\n"
        details += f"Predicate: {predicate}\n"
        details += f"Object: {object_}\n\n"
        
        # Get additional information
        try:
            # Get subject type
            subj_query = f"""
            SELECT ?class
            WHERE {{
                univ:{subject} rdf:type ?class .
                FILTER (?class != owl:NamedIndividual)
            }}
            LIMIT 1
            """
            
            subj_results = list(self.app.ontology.query(subj_query))
            if subj_results:
                subj_class = str(subj_results[0]['class']).split('#')[-1]
                details += f"Subject Type: {subj_class}\n"
                
            # Get object type
            obj_query = f"""
            SELECT ?class
            WHERE {{
                univ:{object_} rdf:type ?class .
                FILTER (?class != owl:NamedIndividual)
            }}
            LIMIT 1
            """
            
            obj_results = list(self.app.ontology.query(obj_query))
            if obj_results:
                obj_class = str(obj_results[0]['class']).split('#')[-1]
                details += f"Object Type: {obj_class}\n"
                
            # Get predicate details
            pred_query = f"""
            SELECT ?comment
            WHERE {{
                univ:{predicate} rdfs:comment ?comment .
            }}
            LIMIT 1
            """
            
            pred_results = list(self.app.ontology.query(pred_query))
            if pred_results:
                comment = str(pred_results[0]['comment'])
                details += f"\nDescription: {comment}\n"
                
        except:
            pass
            
        messagebox.showinfo("Relationship Details", details)
        
    def update_statistics(self):
        """Update statistics panel"""
        try:
            # Get all relationships
            query = """
            SELECT ?subject ?predicate ?object
            WHERE {
                ?subject ?predicate ?object .
                FILTER (isURI(?object))
                FILTER (STRSTARTS(STR(?predicate), STR(univ:)))
            }
            """
            
            results = list(self.app.ontology.query(query))
            
            if not results:
                return
                
            # Calculate statistics
            total = len(results)
            
            # Count by predicate
            predicate_counts = {}
            subject_counts = {}
            
            for row in results:
                predicate = str(row['predicate']).split('#')[-1]
                subject = str(row['subject']).split('#')[-1]
                
                predicate_counts[predicate] = predicate_counts.get(predicate, 0) + 1
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
                
            # Find most common predicate
            most_common = max(predicate_counts.items(), key=lambda x: x[1]) if predicate_counts else ("None", 0)
            
            # Calculate averages
            avg_per_subject = total / len(subject_counts) if subject_counts else 0
            max_per_subject = max(subject_counts.values()) if subject_counts else 0
            
            # Update labels
            self.stats_labels['total'].config(text=str(total))
            self.stats_labels['most_common'].config(
                text=f"{most_common[0]} ({most_common[1]})")
            self.stats_labels['avg_per_subject'].config(
                text=f"{avg_per_subject:.2f}")
            self.stats_labels['max_per_subject'].config(
                text=str(max_per_subject))
                
        except Exception as e:
            print(f"Error updating statistics: {e}")
            
    def refresh(self):
        """Refresh relationships tree"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Build query based on filter
        rel_type = self.rel_type_var.get()
        
        if rel_type == "All":
            query = """
            SELECT ?subject ?predicate ?object
            WHERE {
                ?subject ?predicate ?object .
                FILTER (isURI(?object))
                FILTER (STRSTARTS(STR(?predicate), STR(univ:)))
            }
            ORDER BY ?predicate ?subject
            LIMIT 500
            """
        else:
            predicate_uri = self.app.ontology.univ_ns[rel_type]
            query = f"""
            SELECT ?subject ?object
            WHERE {{
                ?subject <{predicate_uri}> ?object .
                FILTER (isURI(?object))
            }}
            ORDER BY ?subject
            LIMIT 500
            """
            
        try:
            results = list(self.app.ontology.query(query))
            
            for i, row in enumerate(results, 1):
                subject_uri = str(row['subject'])
                subject = subject_uri.split('#')[-1]
                
                object_uri = str(row['object'])
                object_ = object_uri.split('#')[-1]
                
                if rel_type == "All":
                    predicate_uri = str(row['predicate'])
                    predicate = predicate_uri.split('#')[-1]
                else:
                    predicate = rel_type
                    
                # Insert into tree
                self.tree.insert('', tk.END, text=str(i),
                               values=(subject, predicate, object_))
                               
            # Update statistics
            self.update_statistics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load relationships: {str(e)}")
            
    def add_relationship(self):
        """Add new relationship"""
        self.app.open_add_relationship()
        
    def delete_relationship(self):
        """Delete selected relationship(s)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select relationship(s) to delete")
            return
            
        relationships = []
        for item in selection:
            values = self.tree.item(item, 'values')
            if values and len(values) >= 3:
                subject, predicate, object_ = values[:3]
                relationships.append((subject, predicate, object_))
                
        if not relationships:
            return
            
        if len(relationships) == 1:
            subject, predicate, object_ = relationships[0]
            message = f"Delete relationship:\n{subject} {predicate} {object_}?"
        else:
            message = f"Delete {len(relationships)} relationships?"
            
        confirm = messagebox.askyesno("Confirm Delete", message)
        
        if confirm:
            try:
                deleted_count = 0
                for subject, predicate, object_ in relationships:
                    # Remove the relationship
                    subj_uri = self.app.ontology.univ_ns[subject]
                    pred_uri = self.app.ontology.univ_ns[predicate]
                    obj_uri = self.app.ontology.univ_ns[object_]
                    
                    self.app.ontology.graph.remove((subj_uri, pred_uri, obj_uri))
                    deleted_count += 1
                    
                self.refresh()
                messagebox.showinfo("Success", 
                                  f"Deleted {deleted_count} relationship(s)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete relationship(s): {str(e)}")
                
    def visualize_relationships(self):
        """Visualize relationships"""
        self.app.show_instance_graph()
        
    def on_tab_selected(self):
        """Called when tab is selected"""
        self.refresh()
        
    def delete_selected(self):
        """Delete selected items"""
        self.delete_relationship()