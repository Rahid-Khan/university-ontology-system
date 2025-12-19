"""
Additional dialog windows
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json

class QueryBuilderDialog:
    """Visual SPARQL query builder dialog"""
    
    def __init__(self, parent, ontology):
        self.parent = parent
        self.ontology = ontology
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("SPARQL Query Builder")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create query builder widgets"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Visual builder tab
        visual_frame = ttk.Frame(notebook)
        notebook.add(visual_frame, text="Visual Builder")
        self.create_visual_builder(visual_frame)
        
        # Template tab
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="Templates")
        self.create_template_tab(template_frame)
        
        # Preview tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="Preview")
        self.create_preview_tab(preview_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=self.dialog.destroy).pack(pady=(10, 0))
                  
    def create_visual_builder(self, parent):
        """Create visual query builder"""
        # This would be a complex visual query builder
        # For now, just show a placeholder
        label = ttk.Label(parent, text="Visual Query Builder (Coming Soon)",
                         font=('Arial', 12))
        label.pack(expand=True)
        
    def create_template_tab(self, parent):
        """Create template selection tab"""
        from core.query_engine import QueryEngine
        
        text = tk.Text(parent, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get common queries
        query_engine = QueryEngine(self.ontology)
        templates = query_engine.get_common_queries()
        
        content = "SPARQL QUERY TEMPLATES\n"
        content += "=" * 40 + "\n\n"
        
        for name, query in templates.items():
            display_name = ' '.join(word.capitalize() for word in name.split('_'))
            content += f"{display_name}:\n"
            content += "-" * 30 + "\n"
            content += query + "\n\n"
            
        text.insert(1.0, content)
        text.config(state=tk.DISABLED)
        
    def create_preview_tab(self, parent):
        """Create query preview tab"""
        # Query preview text
        self.preview_text = tk.Text(parent, wrap=tk.NONE, font=('Courier', 10),
                                   height=20)
        scrollbar_y = ttk.Scrollbar(parent, command=self.preview_text.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL,
                                   command=self.preview_text.xview)
        
        self.preview_text.config(yscrollcommand=scrollbar_y.set,
                                xscrollcommand=scrollbar_x.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set default query
        default_query = """
        # Example SPARQL Query
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object .
            FILTER (isURI(?object))
        }
        LIMIT 10
        """
        self.preview_text.insert(1.0, default_query)

class ExamplesDialog:
    """Examples and tutorials dialog"""
    
    def __init__(self, parent, query_engine):
        self.parent = parent
        self.query_engine = query_engine
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Examples and Tutorials")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create examples dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic examples tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Examples")
        self.create_basic_examples(basic_frame)
        
        # Advanced examples tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Advanced Examples")
        self.create_advanced_examples(advanced_frame)
        
        # Tutorial tab
        tutorial_frame = ttk.Frame(notebook)
        notebook.add(tutorial_frame, text="Tutorial")
        self.create_tutorial(tutorial_frame)
        
        # Close button
        ttk.Button(main_frame, text="Close",
                  command=self.dialog.destroy).pack(pady=(10, 0))
                  
    def create_basic_examples(self, parent):
        """Create basic examples tab"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        examples = """
        BASIC SPARQL EXAMPLES
        =====================
        
        1. Find All Students:
        SELECT ?student ?name ?gpa
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:name ?name .
            OPTIONAL { ?student univ:gpa ?gpa }
        }
        ORDER BY ?name
        LIMIT 20
        
        2. Find Courses by Professor:
        SELECT ?course ?courseName
        WHERE {
            ?prof univ:name "John Smith" .
            ?prof univ:teaches ?course .
            ?course univ:name ?courseName .
        }
        
        3. Count Students by Program:
        SELECT ?program (COUNT(?student) as ?count)
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:enrolledIn ?program .
        }
        GROUP BY ?program
        ORDER BY DESC(?count)
        
        4. Find Courses with Prerequisites:
        SELECT ?course ?prereq
        WHERE {
            ?course univ:hasPrerequisite ?prereq .
            ?course univ:name ?courseName .
            ?prereq univ:name ?prereqName .
        }
        """
        
        text.insert(1.0, examples)
        text.config(state=tk.DISABLED)
        
    def create_advanced_examples(self, parent):
        """Create advanced examples tab"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        examples = """
        ADVANCED SPARQL EXAMPLES
        ========================
        
        1. Find Students Taking Specific Course:
        SELECT ?student ?name ?gpa
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:name ?name .
            ?student univ:gpa ?gpa .
            ?student univ:takesCourse univ:CS101 .
        }
        ORDER BY DESC(?gpa)
        
        2. Find Research Collaboration Network:
        SELECT ?researcher1 ?researcher2
        WHERE {
            ?researcher1 univ:partOfResearch ?research .
            ?researcher2 univ:partOfResearch ?research .
            FILTER (?researcher1 != ?researcher2)
        }
        GROUP BY ?researcher1 ?researcher2
        
        3. Find Department Structure:
        SELECT ?dept ?program ?course
        WHERE {
            ?dept univ:offersProgram ?program .
            ?program univ:hasCourse ?course .
        }
        ORDER BY ?dept ?program ?course
        
        4. Find Students and Their Advisors:
        SELECT ?student ?studentName ?advisor ?advisorName
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:name ?studentName .
            ?student univ:hasAdvisor ?advisor .
            ?advisor univ:name ?advisorName .
        }
        ORDER BY ?advisorName ?studentName
        """
        
        text.insert(1.0, examples)
        text.config(state=tk.DISABLED)
        
    def create_tutorial(self, parent):
        """Create tutorial tab"""
        text = tk.Text(parent, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tutorial = """
        SPARQL QUERY TUTORIAL
        =====================
        
        1. UNDERSTANDING SPARQL
        -----------------------
        SPARQL (SPARQL Protocol and RDF Query Language) is a query language 
        for RDF data. It's similar to SQL but designed for graph data.
        
        Key components:
        - SELECT: Specifies what to return
        - WHERE: Specifies patterns to match
        - FILTER: Adds conditions
        - OPTIONAL: Optional patterns
        - ORDER BY: Sorting results
        - LIMIT: Limits number of results
        
        2. BASIC PATTERNS
        -----------------
        Triple patterns in SPARQL look like:
        ?subject ?predicate ?object .
        
        Example:
        ?student univ:name ?name .
        
        This matches all triples where:
        - Subject is any student
        - Predicate is 'name'
        - Object is bound to ?name variable
        
        3. FILTERING RESULTS
        --------------------
        Use FILTER to add conditions:
        FILTER (?gpa > 3.5)
        FILTER (CONTAINS(?name, "John"))
        FILTER (REGEX(?email, "@university.edu$"))
        
        4. OPTIONAL PATTERNS
        --------------------
        OPTIONAL allows missing data:
        OPTIONAL { ?student univ:gpa ?gpa }
        
        Students without GPA will still appear in results.
        
        5. AGGREGATION
        --------------
        Use aggregation functions:
        COUNT(?student) - Count students
        AVG(?gpa) - Average GPA
        MAX(?gpa) - Maximum GPA
        MIN(?gpa) - Minimum GPA
        SUM(?credits) - Sum of credits
        
        6. GROUPING
        -----------
        GROUP BY groups results:
        GROUP BY ?program
        Use with aggregation functions.
        
        7. ORDERING
        -----------
        ORDER BY sorts results:
        ORDER BY ?name - Ascending by name
        ORDER BY DESC(?gpa) - Descending by GPA
        
        8. LIMITING RESULTS
        -------------------
        LIMIT restricts number of results:
        LIMIT 100 - First 100 results
        
        9. BEST PRACTICES
        -----------------
        - Always use LIMIT for large queries
        - Use OPTIONAL for optional data
        - Filter early to improve performance
        - Use meaningful variable names
        - Comment complex queries
        """
        
        text.insert(1.0, tutorial)
        text.config(state=tk.DISABLED)

class PreferencesDialog:
    """Preferences dialog"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Preferences")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create preferences widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # General tab
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text="General")
        self.create_general_tab(general_frame)
        
        # Visualization tab
        viz_frame = ttk.Frame(notebook, padding=10)
        notebook.add(viz_frame, text="Visualization")
        self.create_visualization_tab(viz_frame)
        
        # Query tab
        query_frame = ttk.Frame(notebook, padding=10)
        notebook.add(query_frame, text="Query")
        self.create_query_tab(query_frame)
        
        # Save/Cancel buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))
        
        ttk.Button(button_frame, text="Save",
                  command=self.save_preferences).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults",
                  command=self.reset_preferences).pack(side=tk.LEFT, padx=5)
                  
    def create_general_tab(self, parent):
        """Create general preferences tab"""
        # Auto-save
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Auto-save changes",
                       variable=self.auto_save_var).pack(anchor=tk.W, pady=5)
        
        # Auto-save interval
        ttk.Label(parent, text="Auto-save interval (minutes):").pack(anchor=tk.W, pady=(10, 0))
        self.auto_save_interval = tk.IntVar(value=5)
        ttk.Spinbox(parent, from_=1, to=60, textvariable=self.auto_save_interval,
                   width=10).pack(anchor=tk.W, pady=5)
        
        # Show warnings
        self.show_warnings_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Show warning dialogs",
                       variable=self.show_warnings_var).pack(anchor=tk.W, pady=5)
        
        # Confirm deletions
        self.confirm_deletions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Confirm before deleting",
                       variable=self.confirm_deletions_var).pack(anchor=tk.W, pady=5)
        
    def create_visualization_tab(self, parent):
        """Create visualization preferences tab"""
        # Default layout
        ttk.Label(parent, text="Default layout:").pack(anchor=tk.W, pady=(0, 5))
        self.default_layout = tk.StringVar(value="spring")
        layout_combo = ttk.Combobox(parent, textvariable=self.default_layout,
                                   values=["spring", "circular", "kamada_kawai", 
                                           "spectral", "shell"],
                                   width=15)
        layout_combo.pack(anchor=tk.W, pady=5)
        
        # Default node size
        ttk.Label(parent, text="Default node size:").pack(anchor=tk.W, pady=(10, 0))
        self.default_node_size = tk.IntVar(value=500)
        ttk.Scale(parent, from_=100, to=2000, variable=self.default_node_size,
                 orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Default edge width
        ttk.Label(parent, text="Default edge width:").pack(anchor=tk.W, pady=(10, 0))
        self.default_edge_width = tk.IntVar(value=2)
        ttk.Scale(parent, from_=1, to=10, variable=self.default_edge_width,
                 orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Default color scheme
        ttk.Label(parent, text="Default color scheme:").pack(anchor=tk.W, pady=(10, 0))
        self.default_color_scheme = tk.StringVar(value="viridis")
        color_combo = ttk.Combobox(parent, textvariable=self.default_color_scheme,
                                  values=["viridis", "plasma", "coolwarm", 
                                         "Set2", "Set3", "tab20c"],
                                  width=15)
        color_combo.pack(anchor=tk.W, pady=5)
        
    def create_query_tab(self, parent):
        """Create query preferences tab"""
        # Query timeout
        ttk.Label(parent, text="Query timeout (seconds):").pack(anchor=tk.W, pady=(0, 5))
        self.query_timeout = tk.IntVar(value=30)
        ttk.Spinbox(parent, from_=5, to=300, textvariable=self.query_timeout,
                   width=10).pack(anchor=tk.W, pady=5)
        
        # Default limit
        ttk.Label(parent, text="Default result limit:").pack(anchor=tk.W, pady=(10, 0))
        self.default_limit = tk.IntVar(value=100)
        ttk.Spinbox(parent, from_=10, to=1000, textvariable=self.default_limit,
                   width=10).pack(anchor=tk.W, pady=5)
        
        # Enable query cache
        self.enable_cache_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Enable query caching",
                       variable=self.enable_cache_var).pack(anchor=tk.W, pady=5)
        
        # Cache size
        ttk.Label(parent, text="Cache size (queries):").pack(anchor=tk.W, pady=(10, 0))
        self.cache_size = tk.IntVar(value=50)
        ttk.Spinbox(parent, from_=10, to=500, textvariable=self.cache_size,
                   width=10).pack(anchor=tk.W, pady=5)
        
    def save_preferences(self):
        """Save preferences"""
        # In a real implementation, save to config file
        messagebox.showinfo("Preferences", "Preferences saved successfully")
        self.dialog.destroy()
        
    def reset_preferences(self):
        """Reset preferences to defaults"""
        self.auto_save_var.set(True)
        self.auto_save_interval.set(5)
        self.show_warnings_var.set(True)
        self.confirm_deletions_var.set(True)
        self.default_layout.set("spring")
        self.default_node_size.set(500)
        self.default_edge_width.set(2)
        self.default_color_scheme.set("viridis")
        self.query_timeout.set(30)
        self.default_limit.set(100)
        self.enable_cache_var.set(True)
        self.cache_size.set(50)
        
        messagebox.showinfo("Preferences", "Preferences reset to defaults")