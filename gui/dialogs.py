"""
Dialog windows for the application
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from datetime import datetime
import json

from config.settings import Colors, Fonts
from core.ontology import UniversityOntology
from core.query_engine import QueryEngine
from utils.helpers import format_date, generate_id
# Re-export additional dialogs implemented in dialogs_extra for convenience
try:
    from gui.dialogs_extra import QueryBuilderDialog, ExamplesDialog, PreferencesDialog
except Exception:
    # Fallback: ignore if dialogs_extra not available at import time
    QueryBuilderDialog = None
    ExamplesDialog = None
    PreferencesDialog = None

class BaseDialog:
    """Base class for dialog windows"""
    
    def __init__(self, parent, title="Dialog", width=400, height=300):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        self.result = None
        # Note: do not call create_widgets() here because subclasses may need
        # to set attributes (e.g. ontology, query_engine) before widgets are
        # created. Subclasses should call self.create_widgets() after their
        # own initialization.
        
    def create_widgets(self):
        """Create dialog widgets (to be overridden)"""
        pass
        
    def show(self):
        """Show dialog and wait for result"""
        self.dialog.wait_window()
        return self.result

class AddInstanceDialog(BaseDialog):
    """Dialog for adding new instances"""
    
    def __init__(self, parent, ontology):
        # store required attributes before creating widgets
        self.ontology = ontology
        self.class_var = tk.StringVar()
        self.instance_id_var = tk.StringVar()
        self.properties = {}
        super().__init__(parent, "Add New Instance", 500, 400)
        # create widgets now that attributes are set
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Class selection
        ttk.Label(main_frame, text="Class:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        classes = self.get_classes()
        class_combo = ttk.Combobox(main_frame, textvariable=self.class_var,
                                  values=classes, width=30)
        class_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        class_combo.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        if classes:
            class_combo.set(classes[0])
            
        # Instance ID
        ttk.Label(main_frame, text="Instance ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        id_entry = ttk.Entry(main_frame, textvariable=self.instance_id_var, width=30)
        id_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Auto-generate ID button
        ttk.Button(main_frame, text="Generate ID",
                  command=self.generate_id).grid(row=1, column=2, padx=5)
                  
        # Properties frame
        self.props_frame = ttk.LabelFrame(main_frame, text="Properties", padding=10)
        self.props_frame.grid(row=2, column=0, columnspan=3, sticky=tk.NSEW, pady=10)
        
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Initial properties
        self.on_class_selected()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Add", command=self.on_add,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def get_classes(self):
        """Get list of available classes"""
        query = """
        SELECT ?class
        WHERE {
            ?class rdf:type owl:Class .
        }
        ORDER BY ?class
        """
        
        results = self.ontology.query(query)
        classes = []
        
        for row in results:
            class_uri = str(row['class'])
            class_name = class_uri.split('#')[-1]
            classes.append(class_name)
            
        return sorted(classes)
        
    def on_class_selected(self, event=None):
        """Update properties when class is selected"""
        # Clear existing properties
        for widget in self.props_frame.winfo_children():
            widget.destroy()
            
        class_name = self.class_var.get()
        if not class_name:
            return
            
        # Get properties for this class
        properties = self.get_class_properties(class_name)
        
        self.property_entries = {}
        
        # Create property fields
        for i, (prop_name, prop_info) in enumerate(properties):
            ttk.Label(self.props_frame, text=f"{prop_name}:").grid(
                row=i, column=0, sticky=tk.W, pady=2, padx=5)
                
            if prop_info.get('datatype', '').endswith('string'):
                entry = ttk.Entry(self.props_frame, width=30)
            elif prop_info.get('datatype', '').endswith('integer'):
                entry = ttk.Spinbox(self.props_frame, from_=0, to=10000, width=28)
            elif prop_info.get('datatype', '').endswith('float'):
                entry = ttk.Spinbox(self.props_frame, from_=0.0, to=10000.0, 
                                   increment=0.1, width=28)
            elif prop_info.get('datatype', '').endswith('date'):
                entry = ttk.Entry(self.props_frame, width=30)
                # In real implementation, add date picker
            else:
                entry = ttk.Entry(self.props_frame, width=30)
                
            entry.grid(row=i, column=1, sticky=tk.W, pady=2, padx=5)
            
            # Add tooltip with description
            if prop_info.get('comment'):
                from gui.widgets import ToolTip
                ToolTip(entry, prop_info['comment'])
                
            self.property_entries[prop_name] = entry
            
    def get_class_properties(self, class_name):
        """Get properties for a class"""
        # Common properties for all classes
        common_props = [
            ("name", {"datatype": "string", "comment": "Name of the instance"}),
            ("description", {"datatype": "string", "comment": "Description"}),
            ("id", {"datatype": "string", "comment": "Unique identifier"})
        ]
        
        # Get specific properties for this class
        query = f"""
        SELECT ?prop ?datatype ?comment
        WHERE {{
            ?prop rdf:type owl:DatatypeProperty .
            ?prop rdfs:domain univ:{class_name} .
            ?prop rdfs:range ?datatype .
            OPTIONAL {{ ?prop rdfs:comment ?comment }}
        }}
        """
        
        specific_props = []
        try:
            results = self.ontology.query(query)
            for row in results:
                prop_name = str(row['prop']).split('#')[-1]
                datatype = str(row['datatype']).split('#')[-1] if row['datatype'] else "string"
                comment = str(row['comment']) if row['comment'] else ""
                
                specific_props.append((prop_name, {
                    "datatype": datatype,
                    "comment": comment
                }))
        except:
            pass
            
        # Combine and remove duplicates
        all_props = {}
        for prop_name, prop_info in common_props + specific_props:
            if prop_name not in all_props:
                all_props[prop_name] = prop_info
                
        return list(all_props.items())
        
    def generate_id(self):
        """Generate a unique ID"""
        class_name = self.class_var.get()
        if class_name:
            prefix = class_name[:3].upper()
            self.instance_id_var.set(f"{prefix}_{generate_id(length=6)}")
            
    def on_add(self):
        """Handle add button click"""
        class_name = self.class_var.get()
        instance_id = self.instance_id_var.get()
        
        if not class_name:
            messagebox.showerror("Error", "Please select a class")
            return
            
        if not instance_id:
            messagebox.showerror("Error", "Please enter an instance ID")
            return
            
        # Collect properties
        properties = {}
        for prop_name, entry in self.property_entries.items():
            value = entry.get()
            if value:
                properties[prop_name] = value
                
        try:
            # Add the instance
            self.ontology.add_instance(class_name, instance_id, properties)
            self.result = (class_name, instance_id, properties)
            self.dialog.destroy()
            messagebox.showinfo("Success", f"Instance '{instance_id}' added successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add instance: {str(e)}")

class AddRelationshipDialog(BaseDialog):
    """Dialog for adding new relationships"""
    
    def __init__(self, parent, ontology):
        # set attributes first
        self.ontology = ontology
        super().__init__(parent, "Add New Relationship", 450, 300)
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Subject
        ttk.Label(main_frame, text="Subject:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(main_frame, textvariable=self.subject_var,
                                         width=30)
        self.subject_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Predicate
        ttk.Label(main_frame, text="Relationship:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.predicate_var = tk.StringVar()
        self.predicate_combo = ttk.Combobox(main_frame, textvariable=self.predicate_var,
                                           width=30)
        self.predicate_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.predicate_combo.bind('<<ComboboxSelected>>', self.on_predicate_selected)
        
        # Object
        ttk.Label(main_frame, text="Object:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.object_var = tk.StringVar()
        self.object_combo = ttk.Combobox(main_frame, textvariable=self.object_var,
                                        width=30)
        self.object_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Load data
        self.load_instances()
        self.load_predicates()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add", command=self.on_add,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def load_instances(self):
        """Load instances into comboboxes"""
        query = """
        SELECT ?instance
        WHERE {
            ?instance rdf:type owl:NamedIndividual .
        }
        ORDER BY ?instance
        """
        
        results = self.ontology.query(query)
        instances = []
        
        for row in results:
            instance_uri = str(row['instance'])
            instance_id = instance_uri.split('#')[-1]
            instances.append(instance_id)
            
        self.subject_combo['values'] = sorted(instances)
        self.object_combo['values'] = sorted(instances)
        
    def load_predicates(self):
        """Load predicates into combobox"""
        query = """
        SELECT ?predicate
        WHERE {
            ?predicate rdf:type owl:ObjectProperty .
        }
        ORDER BY ?predicate
        """
        
        results = self.ontology.query(query)
        predicates = []
        
        for row in results:
            predicate_uri = str(row['predicate'])
            predicate_name = predicate_uri.split('#')[-1]
            predicates.append(predicate_name)
            
        self.predicate_combo['values'] = sorted(predicates)
        
    def on_predicate_selected(self, event=None):
        """Update object suggestions based on predicate"""
        predicate = self.predicate_var.get()
        if not predicate:
            return
            
        # Get range of predicate
        query = f"""
        SELECT ?range
        WHERE {{
            univ:{predicate} rdfs:range ?range .
        }}
        """
        
        try:
            results = self.ontology.query(query)
            if results:
                range_class = str(list(results)[0]['range']).split('#')[-1]
                
                # Filter objects by class
                query2 = f"""
                SELECT ?instance
                WHERE {{
                    ?instance rdf:type univ:{range_class} .
                    ?instance rdf:type owl:NamedIndividual .
                }}
                """
                
                results2 = self.ontology.query(query2)
                objects = []
                
                for row in results2:
                    instance_uri = str(row['instance'])
                    instance_id = instance_uri.split('#')[-1]
                    objects.append(instance_id)
                    
                self.object_combo['values'] = sorted(objects)
        except:
            pass
            
    def on_add(self):
        """Handle add button click"""
        subject = self.subject_var.get()
        predicate = self.predicate_var.get()
        object_ = self.object_var.get()
        
        if not all([subject, predicate, object_]):
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        try:
            # Add the relationship
            success = self.ontology.add_relationship(subject, predicate, object_)
            if success:
                self.result = (subject, predicate, object_)
                self.dialog.destroy()
                messagebox.showinfo("Success", "Relationship added successfully")
            else:
                messagebox.showwarning("Warning", "Relationship already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add relationship: {str(e)}")

class SPARQLEditorDialog(BaseDialog):
    """Dialog for SPARQL query editing and execution"""
    
    def __init__(self, parent, query_engine, initial_query=""):
        # set attributes before creating widgets
        self.query_engine = query_engine
        self.initial_query = initial_query
        self.history = []
        super().__init__(parent, "SPARQL Query Editor", 800, 600)
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Query input frame
        input_frame = ttk.LabelFrame(main_frame, text="SPARQL Query", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # Query text with line numbers
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(text_frame, width=4, padx=5, pady=5,
                                   state='disabled', font=('Courier', 10))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Query text
        self.query_text = tk.Text(text_frame, wrap=tk.NONE, font=('Courier', 10),
                                 padx=5, pady=5)
        query_scroll_y = ttk.Scrollbar(text_frame, command=self.on_text_scroll)
        query_scroll_x = ttk.Scrollbar(input_frame, orient=tk.HORIZONTAL,
                                      command=self.query_text.xview)
        
        self.query_text.config(yscrollcommand=self.on_text_scroll,
                              xscrollcommand=query_scroll_x.set)
        
        self.query_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        query_scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        query_scroll_x.pack(fill=tk.X)
        
        # Set initial query
        if self.initial_query:
            self.query_text.insert(1.0, self.initial_query)
            self.update_line_numbers()
            
        # Bind events
        self.query_text.bind('<KeyRelease>', self.on_query_change)
        
        # Result frame
        result_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Result text
        self.result_text = tk.Text(result_frame, wrap=tk.NONE, font=('Courier', 9),
                                  padx=5, pady=5)
        result_scroll_y = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        result_scroll_x = ttk.Scrollbar(result_frame, orient=tk.HORIZONTAL,
                                       command=self.result_text.xview)
        
        self.result_text.config(yscrollcommand=result_scroll_y.set,
                               xscrollcommand=result_scroll_x.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scroll_y.pack(side=tk.LEFT, fill=tk.Y)
        result_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Query templates
        ttk.Button(control_frame, text="Templates",
                  command=self.show_templates).pack(side=tk.LEFT, padx=2)
        
        # Limit
        ttk.Label(control_frame, text="Limit:").pack(side=tk.LEFT, padx=(10, 2))
        self.limit_var = tk.StringVar(value="100")
        limit_spin = ttk.Spinbox(control_frame, from_=1, to=1000,
                                textvariable=self.limit_var, width=8)
        limit_spin.pack(side=tk.LEFT, padx=2)
        
        # Format
        ttk.Label(control_frame, text="Format:").pack(side=tk.LEFT, padx=(10, 2))
        self.format_var = tk.StringVar(value="Table")
        format_combo = ttk.Combobox(control_frame, textvariable=self.format_var,
                                   values=["Table", "JSON", "CSV", "Turtle"],
                                   width=10, state='readonly')
        format_combo.pack(side=tk.LEFT, padx=2)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Execute (Ctrl+Enter)",
                  command=self.execute_query,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Clear",
                  command=self.clear_results).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save Results",
                  command=self.save_results).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Close",
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=2)
                  
        # Bind Ctrl+Enter
        self.query_text.bind('<Control-Return>', lambda e: self.execute_query())
        
    def on_text_scroll(self, *args):
        """Sync scroll between text and line numbers"""
        self.line_numbers.yview_moveto(args[0])
        self.query_text.yview_moveto(args[0])
        
    def on_query_change(self, event=None):
        """Update line numbers when query changes"""
        self.update_line_numbers()
        
    def update_line_numbers(self):
        """Update line numbers in the side panel"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        
        lines = self.query_text.get(1.0, tk.END).count('\n')
        for i in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
            
        self.line_numbers.config(state='disabled')
        
    def execute_query(self):
        """Execute SPARQL query"""
        query = self.query_text.get(1.0, tk.END).strip()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a SPARQL query")
            return
            
        try:
            # Add to history
            self.history.append(query)
            
            # Execute query
            limit = int(self.limit_var.get())
            result = self.query_engine.execute_query(query, limit=limit)
            
            # Display results
            self.display_results(result)
            
        except Exception as e:
            messagebox.showerror("Query Error", f"Error executing query: {str(e)}")
            
    def display_results(self, result):
        """Display query results"""
        self.result_text.delete(1.0, tk.END)
        
        if result.type == 'SELECT':
            # Get headers
            headers = result.vars
            
            # Create table
            table_data = []
            
            # Add headers
            table_data.append([str(h) for h in headers])
            table_data.append(['-' * 20 for _ in headers])
            
            # Add rows
            for row in result:
                row_data = []
                for var in headers:
                    value = row[var]
                    if value:
                        # Simplify URIs
                        value_str = str(value)
                        if '#' in value_str:
                            value_str = value_str.split('#')[-1]
                        elif '/' in value_str:
                            value_str = value_str.split('/')[-1]
                        row_data.append(value_str)
                    else:
                        row_data.append("")
                table_data.append(row_data)
                
            # Format as table
            if self.format_var.get() == "Table":
                # Calculate column widths
                col_widths = [max(len(str(row[i])) for row in table_data) 
                            for i in range(len(headers))]
                
                # Format rows
                for row in table_data:
                    formatted_row = []
                    for i, cell in enumerate(row):
                        formatted_row.append(str(cell).ljust(col_widths[i] + 2))
                    self.result_text.insert(tk.END, ' '.join(formatted_row) + '\n')
                    
            elif self.format_var.get() == "JSON":
                import json
                data = []
                for row in result:
                    row_dict = {}
                    for var in headers:
                        value = row[var]
                        if value:
                            row_dict[str(var)] = str(value)
                    data.append(row_dict)
                self.result_text.insert(tk.END, json.dumps(data, indent=2))
                
            elif self.format_var.get() == "CSV":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write headers
                writer.writerow([str(h) for h in headers])
                
                # Write rows
                for row in result:
                    row_data = []
                    for var in headers:
                        value = row[var]
                        row_data.append(str(value) if value else "")
                    writer.writerow(row_data)
                    
                self.result_text.insert(tk.END, output.getvalue())
                
        elif result.type == 'ASK':
            self.result_text.insert(tk.END, f"Result: {result.askAnswer}\n")
            
        elif result.type == 'CONSTRUCT' or result.type == 'DESCRIBE':
            self.result_text.insert(tk.END, "Graph result:\n")
            for triple in result:
                self.result_text.insert(tk.END, f"{triple}\n")
                
    def clear_results(self):
        """Clear results text"""
        self.result_text.delete(1.0, tk.END)
        
    def save_results(self):
        """Save results to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Results saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
                
    def show_templates(self):
        """Show query templates"""
        templates = self.query_engine.get_common_queries()
        
        template_window = tk.Toplevel(self.dialog)
        template_window.title("Query Templates")
        template_window.geometry("500x400")
        
        # Center window
        template_window.transient(self.dialog)
        template_window.grab_set()
        
        x = self.dialog.winfo_x() + 50
        y = self.dialog.winfo_y() + 50
        template_window.geometry(f"+{x}+{y}")
        
        # Listbox for templates
        listbox = tk.Listbox(template_window, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(template_window, command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        
        for name in templates.keys():
            display_name = ' '.join(word.capitalize() for word in name.split('_'))
            listbox.insert(tk.END, display_name)
            
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def on_template_select(event):
            selection = listbox.curselection()
            if selection:
                template_name = list(templates.keys())[selection[0]]
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(1.0, templates[template_name])
                self.update_line_numbers()
                template_window.destroy()
                
        listbox.bind('<Double-Button-1>', on_template_select)
        
        ttk.Button(template_window, text="Close",
                  command=template_window.destroy).pack(pady=10)

class SearchDialog(BaseDialog):
    """Simple search dialog for instances"""
    def __init__(self, parent, ontology):
        self.ontology = ontology
        super().__init__(parent, "Search", 600, 400)
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Search for instances:").pack(anchor=tk.W)
        self.query_var = tk.StringVar()
        entry = ttk.Entry(main_frame, textvariable=self.query_var, width=60)
        entry.pack(fill=tk.X, pady=(5,10))
        entry.bind('<Return>', lambda e: self.perform_search())

        self.results_lb = tk.Listbox(main_frame, height=12)
        self.results_lb.pack(fill=tk.BOTH, expand=True)
        self.results_lb.bind('<Double-Button-1>', lambda e: self.select_result())

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10,0))
        ttk.Button(btn_frame, text="Search", command=self.perform_search).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def perform_search(self):
        q = self.query_var.get().strip().lower()
        if not q:
            return

        # Search by instance URI or name literal
        sparql = f"""
        SELECT ?instance ?name WHERE {{
            ?instance rdf:type owl:NamedIndividual .
            OPTIONAL {{ ?instance univ:name ?name }} .
            FILTER (CONTAINS(LCASE(STR(?instance)), "{q}") || (BOUND(?name) && CONTAINS(LCASE(STR(?name)), "{q}")))
        }} ORDER BY ?instance LIMIT 200
        """

        try:
            results = list(self.ontology.query(sparql))
            self.results_lb.delete(0, tk.END)
            for row in results:
                inst = str(row['instance']).split('#')[-1]
                name = str(row['name']) if row.get('name') else ''
                display = f"{inst} - {name}" if name else inst
                self.results_lb.insert(tk.END, display)
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search: {e}")

    def select_result(self):
        sel = self.results_lb.curselection()
        if not sel:
            return
        value = self.results_lb.get(sel[0])
        inst_id = value.split(' - ')[0]
        self.result = inst_id
        self.dialog.destroy()

class SaveOntologyDialog:
    """Dialog for saving ontology"""
    
    def __init__(self, parent, ontology, save_as=False):
        self.parent = parent
        self.ontology = ontology
        
        if save_as or not hasattr(self, 'last_filename'):
            self.save_as()
        else:
            self.save()
            
    def save(self):
        """Save ontology to last used filename"""
        try:
            if hasattr(self, 'last_filename') and self.last_filename:
                self.ontology.save_ontology(self.last_filename)
                messagebox.showinfo("Success", f"Ontology saved to {self.last_filename}")
            else:
                self.save_as()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            
    def save_as(self):
        """Save ontology with new filename"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".ttl",
            filetypes=[
                ("Turtle files", "*.ttl"),
                ("RDF/XML", "*.rdf"),
                ("JSON-LD", "*.jsonld"),
                ("N-Triples", "*.nt"),
                ("All files", "*.*")
            ],
            title="Save Ontology As"
        )
        
        if filename:
            try:
                # Determine format from extension
                if filename.endswith('.ttl'):
                    format = 'turtle'
                elif filename.endswith('.rdf') or filename.endswith('.xml'):
                    format = 'xml'
                elif filename.endswith('.jsonld'):
                    format = 'json-ld'
                elif filename.endswith('.nt'):
                    format = 'nt'
                else:
                    format = 'turtle'
                    
                self.ontology.save_ontology(filename, format)
                self.last_filename = filename
                messagebox.showinfo("Success", f"Ontology saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")

class LoadOntologyDialog:
    """Dialog for loading ontology"""
    
    def __init__(self, parent, ontology):
        self.parent = parent
        self.ontology = ontology
        self.load()
        
    def load(self):
        """Load ontology from file"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Turtle files", "*.ttl"),
                ("RDF/XML", "*.rdf"),
                ("JSON-LD", "*.jsonld"),
                ("N-Triples", "*.nt"),
                ("All files", "*.*")
            ],
            title="Load Ontology"
        )
        
        if filename:
            try:
                self.ontology.load_ontology(filename)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
                return False
        return False

class StatisticsDialog(BaseDialog):
    """Dialog for displaying ontology statistics"""
    
    def __init__(self, parent, ontology):
        # set attributes before creating widgets
        self.ontology = ontology
        super().__init__(parent, "Ontology Statistics", 500, 400)
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Get statistics
        stats = self.ontology.get_statistics()
        hierarchy = self.ontology.get_class_hierarchy()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        
        self.create_overview_tab(overview_frame, stats)
        
        # Class distribution tab
        distribution_frame = ttk.Frame(notebook)
        notebook.add(distribution_frame, text="Class Distribution")
        
        self.create_distribution_tab(distribution_frame, hierarchy)
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Details")
        
        self.create_details_tab(details_frame, hierarchy)
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=self.dialog.destroy).pack(pady=(10, 0))
                  
    def create_overview_tab(self, parent, stats):
        """Create overview tab"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.insert(tk.END, "ONTOLOGY STATISTICS\n")
        text.insert(tk.END, "=" * 40 + "\n\n")
        
        text.insert(tk.END, f"Classes: {stats['classes']}\n")
        text.insert(tk.END, f"Instances: {stats['instances']}\n")
        text.insert(tk.END, f"Object Properties: {stats['object_properties']}\n")
        text.insert(tk.END, f"Data Properties: {stats['data_properties']}\n")
        text.insert(tk.END, f"Relationships: {stats['relationships']}\n\n")
        
        # Calculate density
        if stats['instances'] > 0:
            density = stats['relationships'] / stats['instances']
            text.insert(tk.END, f"Relationship Density: {density:.2f} relationships per instance\n")
            
        text.config(state=tk.DISABLED)
        
    def create_distribution_tab(self, parent, hierarchy):
        """Create class distribution tab"""
        # Calculate instance counts
        class_counts = {}
        for class_name, info in hierarchy.items():
            class_counts[class_name] = info['instance_count']
            
        # Sort by count
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create treeview
        tree = ttk.Treeview(parent, columns=('Count', 'Percentage'), show='headings')
        scrollbar = ttk.Scrollbar(parent, command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)
        
        tree.heading('#0', text='Class')
        tree.heading('Count', text='Instances')
        tree.heading('Percentage', text='% of Total')
        
        tree.column('#0', width=200)
        tree.column('Count', width=100)
        tree.column('Percentage', width=100)
        
        total_instances = sum(class_counts.values())
        
        for class_name, count in sorted_classes:
            if total_instances > 0:
                percentage = (count / total_instances) * 100
                percentage_str = f"{percentage:.1f}%"
            else:
                percentage_str = "0.0%"
                
            tree.insert('', tk.END, text=class_name,
                       values=(count, percentage_str))
                       
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_details_tab(self, parent, hierarchy):
        """Create details tab"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.insert(tk.END, "CLASS DETAILS\n")
        text.insert(tk.END, "=" * 40 + "\n\n")
        
        for class_name, info in sorted(hierarchy.items()):
            text.insert(tk.END, f"{info['label']}:\n")
            text.insert(tk.END, f"  Instances: {info['instance_count']}\n")
            
            if info['subclasses']:
                text.insert(tk.END, f"  Subclasses ({len(info['subclasses'])}):\n")
                for subclass in info['subclasses'][:5]:  # Show first 5
                    text.insert(tk.END, f"    • {subclass}\n")
                if len(info['subclasses']) > 5:
                    text.insert(tk.END, f"    ... and {len(info['subclasses']) - 5} more\n")
                    
            if info['comment']:
                text.insert(tk.END, f"  Description: {info['comment']}\n")
                
            text.insert(tk.END, "\n")
            
        text.config(state=tk.DISABLED)

class DocumentationDialog(BaseDialog):
    """Dialog for displaying documentation"""
    
    def __init__(self, parent):
        super().__init__(parent, "Documentation", 700, 500)
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for sections
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Quick Start tab
        quickstart_frame = ttk.Frame(notebook)
        notebook.add(quickstart_frame, text="Quick Start")
        self.create_quickstart_tab(quickstart_frame)
        
        # Ontology tab
        ontology_frame = ttk.Frame(notebook)
        notebook.add(ontology_frame, text="Ontology")
        self.create_ontology_tab(ontology_frame)
        
        # SPARQL tab
        sparql_frame = ttk.Frame(notebook)
        notebook.add(sparql_frame, text="SPARQL")
        self.create_sparql_tab(sparql_frame)
        
        # Visualization tab
        viz_frame = ttk.Frame(notebook)
        notebook.add(viz_frame, text="Visualization")
        self.create_visualization_tab(viz_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=self.dialog.destroy).pack(pady=(10, 0))
                  
    def create_quickstart_tab(self, parent):
        """Create quick start documentation"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        content = """
        QUICK START GUIDE
        =================
        
        1. GETTING STARTED
        ------------------
        - The application loads with sample data automatically
        - Use the Dashboard tab for an overview
        - Browse the Classes tab to see available entity types
        - View Instances to see concrete examples
        
        2. BASIC OPERATIONS
        -------------------
        Adding Data:
        - Use "Add Instance" to create new entities
        - Use "Add Relationship" to connect entities
        - Sample data can be reloaded from File menu
        
        Querying:
        - Use the SPARQL Editor for custom queries
        - Try pre-built templates from Query menu
        - Results can be saved in multiple formats
        
        Visualization:
        - Interactive graphs in Visualization tab
        - Filter and customize visualizations
        - Export visualizations as images
        
        3. KEYBOARD SHORTCUTS
        ---------------------
        Ctrl+N      New Ontology
        Ctrl+O      Open Ontology
        Ctrl+S      Save Ontology
        Ctrl+I      Add Instance
        Ctrl+R      Add Relationship
        Ctrl+Q      SPARQL Editor
        Ctrl+F      Find/Search
        F5          Refresh All
        
        4. NEXT STEPS
        -------------
        - Explore the sample university data
        - Try running different queries
        - Create your own instances and relationships
        - Experiment with different visualizations
        """
        
        text.insert(1.0, content)
        text.config(state=tk.DISABLED)
        
    def create_ontology_tab(self, parent):
        """Create ontology documentation"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        content = """
        ONTOLOGY STRUCTURE
        ===================
        
        1. CLASSES
        ----------
        The university ontology includes these main classes:
        
        Academic Structure:
        - University: Top-level institution
        - Faculty: Academic divisions
        - Department: Subject areas
        - Program: Degree programs
        - Course: Individual courses
        
        People:
        - Person: Base class for all people
        - Student: University students
        - Professor: Teaching faculty
        - Staff: Administrative personnel
        - Researcher: Research personnel
        
        Facilities:
        - Building: University buildings
        - Room: Individual rooms
        - Lab: Laboratory facilities
        - Library: Library resources
        
        Activities:
        - Research: Research projects
        - Publication: Academic publications
        - Event: University events
        - Thesis: Student theses
        
        2. PROPERTIES
        -------------
        Object Properties (relationships):
        - hasFaculty, hasDepartment, offersProgram
        - teaches, enrolledIn, takesCourse
        - worksIn, manages, hasAdvisor
        - published, partOfResearch, locatedIn
        
        Data Properties (attributes):
        - name, id, email, phone
        - startDate, endDate, credits
        - gpa, salary, budget, title
        - description, address, roomNumber
        
        3. BEST PRACTICES
        -----------------
        - Use meaningful instance IDs (e.g., CS101, ProfSmith)
        - Always provide names for instances
        - Use consistent naming conventions
        - Add descriptions where helpful
        - Validate relationships before adding
        """
        
        text.insert(1.0, content)
        text.config(state=tk.DISABLED)
        
    def create_sparql_tab(self, parent):
        """Create SPARQL documentation"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        content = """
        SPARQL QUERY GUIDE
        ===================
        
        1. BASIC QUERIES
        ----------------
        All Students:
        SELECT ?student ?name ?gpa
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:name ?name .
            OPTIONAL { ?student univ:gpa ?gpa }
        }
        ORDER BY ?name
        
        Courses by Professor:
        SELECT ?prof ?course
        WHERE {
            ?prof univ:teaches ?course .
            ?prof univ:name "John Smith" .
        }
        
        2. FILTERING
        ------------
        Students with High GPA:
        SELECT ?student ?name ?gpa
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:name ?name .
            ?student univ:gpa ?gpa .
            FILTER (?gpa > 3.5)
        }
        ORDER BY DESC(?gpa)
        
        3. AGGREGATION
        --------------
        Count by Department:
        SELECT ?dept (COUNT(?student) as ?count)
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:enrolledIn ?program .
            ?program ^univ:offersProgram ?dept .
        }
        GROUP BY ?dept
        
        4. PATHS
        --------
        Course Prerequisites:
        SELECT ?course ?prereq
        WHERE {
            ?course univ:hasPrerequisite+ ?prereq .
        }
        
        5. TIPS
        -------
        - Use LIMIT for large result sets
        - OPTIONAL for missing values
        - FILTER for conditions
        - ORDER BY for sorting
        - DISTINCT for unique results
        """
        
        text.insert(1.0, content)
        text.config(state=tk.DISABLED)
        
    def create_visualization_tab(self, parent):
        """Create visualization documentation"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        content = """
        VISUALIZATION GUIDE
        ===================
        
        1. VISUALIZATION TYPES
        ----------------------
        Class Hierarchy:
        - Shows class inheritance structure
        - Node color indicates instance count
        - Node size shows importance
        
        Instance Network:
        - Displays instances and relationships
        - Color indicates entity type
        - Size shows connection degree
        
        Department Structure:
        - Shows departmental hierarchy
        - Includes programs and courses
        - Useful for academic planning
        
        Course Dependencies:
        - Shows prerequisite relationships
        - Helps with curriculum design
        - Visualizes course sequences
        
        2. INTERACTIVE FEATURES
        -----------------------
        Navigation:
        - Zoom: Mouse wheel or buttons
        - Pan: Click and drag
        - Reset: Reset View button
        
        Selection:
        - Click nodes for details
        - Hover for quick info
        - Multiple selection possible
        
        Customization:
        - Adjust node size
        - Change edge width
        - Modify font size
        - Select color schemes
        
        3. FILTERING
        ------------
        Text Filter:
        - Filters nodes by name
        - Case-insensitive search
        - Updates in real-time
        
        Type Filter:
        - Filter by entity type
        - Multiple types can be selected
        - Combined with text filter
        
        4. EXPORT
        ---------
        Supported Formats:
        - PNG: High-quality images
        - PDF: Vector format
        - SVG: Scalable vector
        - JPEG: Compressed images
        
        Settings:
        - Adjust DPI for quality
        - Choose background color
        - Include legends
        """
        
        text.insert(1.0, content)
        text.config(state=tk.DISABLED)

class AboutDialog(BaseDialog):
    """About dialog"""
    
    def __init__(self, parent):
        super().__init__(parent, "About", 400, 300)
        self.create_widgets()
        
    def create_widgets(self):
        """Create about dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame,
                               text="University Management\nOntology System",
                               font=('Helvetica', 16, 'bold'),
                               justify=tk.CENTER)
        title_label.pack(pady=(0, 20))
        
        # Version
        version_label = ttk.Label(main_frame, text="Version 1.0.0",
                                 font=('Helvetica', 12))
        version_label.pack(pady=5)
        
        # Author
        author_label = ttk.Label(main_frame, text="Author: Rahid Khan",
                                font=('Helvetica', 10))
        author_label.pack(pady=5)
        
        # Description
        desc_label = ttk.Label(main_frame,
                              text="A comprehensive system for managing\n"
                                   "university knowledge graphs using\n"
                                   "semantic web technologies.",
                              font=('Helvetica', 10),
                              justify=tk.CENTER)
        desc_label.pack(pady=20)
        
        # Technologies
        tech_label = ttk.Label(main_frame,
                              text="Built with:\n"
                                   "• Python 3.x\n"
                                   "• RDFLib\n"
                                   "• NetworkX\n"
                                   "• Matplotlib\n"
                                   "• Tkinter",
                              font=('Helvetica', 9),
                              justify=tk.LEFT)
        tech_label.pack(pady=10)
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=self.dialog.destroy).pack(pady=(20, 0))

class QueryHistoryDialog(BaseDialog):
    """Query history dialog"""
    
    def __init__(self, parent, query_engine):
        super().__init__(parent, "Query History", 800, 600)
        self.query_engine = query_engine
        self.create_widgets()
        
    def create_widgets(self):
        """Create query history widgets"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="Clear History",
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Refresh",
                  command=self.refresh_history).pack(side=tk.LEFT, padx=5)
        
        # History list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for history
        columns = ('Timestamp', 'Query', 'Results', 'Time')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=20)
        
        self.tree.heading('#0', text='#')
        self.tree.heading('Timestamp', text='Timestamp')
        self.tree.heading('Query', text='Query')
        self.tree.heading('Results', text='Results')
        self.tree.heading('Time', text='Time (s)')
        
        self.tree.column('#0', width=50)
        self.tree.column('Timestamp', width=150)
        self.tree.column('Query', width=400)
        self.tree.column('Results', width=80)
        self.tree.column('Time', width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to open query in editor
        self.tree.bind('<Double-1>', self.on_query_selected)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Open in Editor",
                  command=self.open_in_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close",
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Load history
        self.refresh_history()
        
    def refresh_history(self):
        """Refresh query history"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get history
        history = self.query_engine.get_query_history()
        history.reverse()  # Show most recent first
        
        from datetime import datetime
        for i, entry in enumerate(history, 1):
            timestamp = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            query_preview = entry['query'][:80] + '...' if len(entry['query']) > 80 else entry['query']
            
            self.tree.insert('', tk.END, text=str(i),
                           values=(timestamp, query_preview, 
                                  entry['result_count'], 
                                  f"{entry['execution_time']:.3f}"))
    
    def clear_history(self):
        """Clear query history"""
        if messagebox.askyesno("Confirm", "Clear all query history?"):
            self.query_engine.clear_history()
            self.refresh_history()
    
    def on_query_selected(self, event):
        """Handle query selection"""
        self.open_in_editor()
    
    def open_in_editor(self):
        """Open selected query in SPARQL editor"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a query from history")
            return
        
        # Get full query from history
        item = self.tree.item(selection[0])
        index = int(item['text']) - 1
        history = self.query_engine.get_query_history()
        history.reverse()
        
        if 0 <= index < len(history):
            query = history[index]['query']
            # Open SPARQL editor with this query
            from gui.dialogs import SPARQLEditorDialog
            SPARQLEditorDialog(self.dialog, self.query_engine, initial_query=query)

class FindReplaceDialog(BaseDialog):
    """Find and replace dialog"""
    
    def __init__(self, parent, ontology):
        super().__init__(parent, "Find and Replace", 500, 400)
        self.ontology = ontology
        self.create_widgets()
        
    def create_widgets(self):
        """Create find/replace widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Find section
        find_frame = ttk.LabelFrame(main_frame, text="Find", padding=10)
        find_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(find_frame, text="Search for:").pack(anchor=tk.W)
        self.find_entry = ttk.Entry(find_frame, width=50)
        self.find_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Replace section
        replace_frame = ttk.LabelFrame(main_frame, text="Replace", padding=10)
        replace_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(replace_frame, text="Replace with:").pack(anchor=tk.W)
        self.replace_entry = ttk.Entry(replace_frame, width=50)
        self.replace_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.case_sensitive = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Case sensitive",
                       variable=self.case_sensitive).pack(anchor=tk.W)
        
        self.search_in = tk.StringVar(value="all")
        ttk.Radiobutton(options_frame, text="All instances",
                       variable=self.search_in, value="all").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Instance names only",
                       variable=self.search_in, value="names").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Property values only",
                       variable=self.search_in, value="values").pack(anchor=tk.W)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.results_text = tk.Text(results_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Find All",
                  command=self.find_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Replace All",
                  command=self.replace_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close",
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to find
        self.find_entry.bind('<Return>', lambda e: self.find_all())
        self.find_entry.focus()
    
    def find_all(self):
        """Find all occurrences"""
        search_text = self.find_entry.get()
        if not search_text:
            messagebox.showwarning("Empty Search", "Please enter text to search for")
            return
        
        case_sensitive = self.case_sensitive.get()
        search_type = self.search_in.get()
        
        # Build query based on search type
        if search_type == "names":
            query = """
            SELECT ?instance ?name
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                ?instance univ:name ?name .
            }
            """
        elif search_type == "values":
            query = """
            SELECT ?instance ?prop ?value
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                ?instance ?prop ?value .
                FILTER (isLiteral(?value))
            }
            """
        else:  # all
            query = """
            SELECT ?instance ?prop ?value
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                ?instance ?prop ?value .
            }
            """
        
        results = self.ontology.query(query)
        matches = []
        
        for row in results:
            for key, value in row.items():
                value_str = str(value)
                if not case_sensitive:
                    if search_text.lower() in value_str.lower():
                        matches.append((str(row.get('instance', '')), key, value_str))
                else:
                    if search_text in value_str:
                        matches.append((str(row.get('instance', '')), key, value_str))
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        if matches:
            self.results_text.insert(1.0, f"Found {len(matches)} matches:\n\n")
            for instance, prop, value in matches[:50]:  # Show first 50
                instance_name = instance.split('#')[-1] if '#' in instance else instance
                self.results_text.insert(tk.END, f"• {instance_name}: {prop} = {value}\n")
            if len(matches) > 50:
                self.results_text.insert(tk.END, f"\n... and {len(matches) - 50} more matches")
        else:
            self.results_text.insert(1.0, "No matches found.")
    
    def replace_all(self):
        """Replace all occurrences"""
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not find_text:
            messagebox.showwarning("Empty Search", "Please enter text to find")
            return
        
        if not messagebox.askyesno("Confirm Replace", 
                                  f"Replace all occurrences of '{find_text}' with '{replace_text}'?\n\n"
                                  "This operation cannot be undone."):
            return
        
        # Note: Actual replacement would require modifying the RDF graph
        # This is a simplified version that shows what would be replaced
        messagebox.showinfo("Replace", 
                          "Replace functionality requires direct graph modification.\n"
                          "This feature is available through the Edit menu options.")