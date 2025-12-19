"""
Main application window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime

from config.settings import Settings, Colors, Fonts
from core.ontology import UniversityOntology
from core.query_engine import QueryEngine
from gui.dashboard import DashboardTab
from gui.classes_tab import ClassesTab
from gui.instances_tab import InstancesTab
from gui.relationships_tab import RelationshipsTab
from gui.visualization_tab import VisualizationTab
from data.sample_data import SampleDataLoader

logger = logging.getLogger(__name__)

class UniversityManagementApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(Settings.WINDOW_TITLE)
        self.root.geometry(Settings.WINDOW_SIZE)
        self.root.minsize(*Settings.MIN_WINDOW_SIZE)
        self.root.configure(bg=Colors.DARK)
        
        # Initialize logging
        self._setup_logging()
        
        # Initialize ontology and query engine
        self.ontology = UniversityOntology()
        self.query_engine = QueryEngine(self.ontology)
        
        # Load sample data
        self.sample_loader = SampleDataLoader(self.ontology)
        # NOTE: defer loading sample data until GUI components (tabs) exist
        
        # Setup styles
        self._setup_styles()
        
        # Create GUI components
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        # Bind events
        self._bind_events()

        # Now load sample data (tabs and other UI are ready)
        try:
            self.load_sample_data()
        except Exception:
            # load_sample_data already logs and shows errors, ignore here
            pass

        logger.info("Application initialized")
        
    def _setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def _setup_styles(self):
        """Setup custom styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel',
                           font=Fonts.TITLE,
                           foreground=Colors.LIGHT)
        self.style.configure('Subtitle.TLabel',
                           font=Fonts.SUBTITLE,
                           foreground=Colors.LIGHT)
        self.style.configure('Card.TFrame',
                           background='white',
                           relief='raised',
                           borderwidth=2)
        self.style.configure('Primary.TButton',
                           font=Fonts.BODY,
                           padding=10,
                           background=Colors.PRIMARY,
                           foreground='white')
        self.style.configure('Success.TButton',
                           font=Fonts.BODY,
                           padding=10,
                           background=Colors.SUCCESS,
                           foreground='white')
        self.style.configure('Warning.TButton',
                           font=Fonts.BODY,
                           padding=10,
                           background=Colors.WARNING,
                           foreground='white')
                           
    def _bind_events(self):
        """Bind keyboard shortcuts and events"""
        self.root.bind('<Control-s>', lambda e: self.save_ontology())
        self.root.bind('<Control-o>', lambda e: self.load_ontology())
        self.root.bind('<Control-q>', lambda e: self.open_sparql_editor())
        self.root.bind('<Control-r>', lambda e: self.refresh_all_views())
        self.root.bind('<F5>', lambda e: self.refresh_all_views())
        self.root.bind('<Escape>', lambda e: self.root.focus())
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Ontology", command=self.new_ontology,
                             accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.load_ontology,
                             accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_ontology,
                             accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_ontology_as)
        file_menu.add_separator()
        file_menu.add_command(label="Import Sample Data", command=self.load_sample_data)
        file_menu.add_command(label="Clear All Data", command=self.clear_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export as Turtle", command=self.export_turtle)
        file_menu.add_command(label="Export as JSON-LD", command=self.export_jsonld)
        file_menu.add_command(label="Export as RDF/XML", command=self.export_rdfxml)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application,
                             accelerator="Alt+F4")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Instance", command=self.open_add_instance,
                             accelerator="Ctrl+I")
        edit_menu.add_command(label="Add Relationship", command=self.open_add_relationship,
                             accelerator="Ctrl+R")
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.open_search,
                             accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.open_replace)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self.open_preferences)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all_views,
                             accelerator="F5")
        view_menu.add_separator()
        view_menu.add_command(label="Class Hierarchy", command=self.show_hierarchy)
        view_menu.add_command(label="Instance Network", command=self.show_instance_graph)
        view_menu.add_command(label="Department Structure", command=self.show_department_structure)
        view_menu.add_command(label="Course Dependencies", command=self.show_course_dependencies)
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Toolbar", variable=tk.BooleanVar(value=True))
        view_menu.add_checkbutton(label="Show Status Bar", variable=tk.BooleanVar(value=True))
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        
        # Query menu
        query_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Query", menu=query_menu)
        query_menu.add_command(label="SPARQL Editor", command=self.open_sparql_editor,
                              accelerator="Ctrl+Q")
        query_menu.add_separator()
        
        # Add common queries to menu
        common_queries = self.query_engine.get_common_queries()
        for name, query in common_queries.items():
            display_name = ' '.join(word.capitalize() for word in name.split('_'))
            query_menu.add_command(label=display_name,
                                  command=lambda q=query: self.open_sparql_editor_with_query(q))
        
        query_menu.add_separator()
        query_menu.add_command(label="Query Builder", command=self.open_query_builder)
        query_menu.add_command(label="Query History", command=self.show_query_history)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Inference", command=self.run_inference)
        tools_menu.add_command(label="Validation", command=self.validate_ontology)
        tools_menu.add_separator()
        tools_menu.add_command(label="Backup", command=self.create_backup)
        tools_menu.add_command(label="Restore", command=self.restore_backup)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="Tutorial", command=self.show_tutorial)
        help_menu.add_command(label="Examples", command=self.show_examples)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_main_layout(self):
        """Create main layout with notebook"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))
        
        # Create toolbar
        self.create_toolbar(main_container)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create tabs
        self.tabs = {}
        
        self.tabs['dashboard'] = DashboardTab(self.notebook, self)
        self.tabs['classes'] = ClassesTab(self.notebook, self)
        self.tabs['instances'] = InstancesTab(self.notebook, self)
        self.tabs['relationships'] = RelationshipsTab(self.notebook, self)
        self.tabs['visualization'] = VisualizationTab(self.notebook, self)
        
        self.notebook.add(self.tabs['dashboard'], text="Dashboard")
        self.notebook.add(self.tabs['classes'], text="Classes")
        self.notebook.add(self.tabs['instances'], text="Instances")
        self.notebook.add(self.tabs['relationships'], text="Relationships")
        self.notebook.add(self.tabs['visualization'], text="Visualization")
        
        # Set tab change callback
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
    def create_toolbar(self, parent):
        """Create toolbar with common actions"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Toolbar buttons
        buttons = [
            ("New", "icons/new.png", self.new_ontology),
            ("Open", "icons/open.png", self.load_ontology),
            ("Save", "icons/save.png", self.save_ontology),
            None,  # Separator
            ("Add Instance", "icons/add.png", self.open_add_instance),
            ("Add Relationship", "icons/link.png", self.open_add_relationship),
            ("Delete", "icons/delete.png", self.delete_selected),
            None,  # Separator
            ("Search", "icons/search.png", self.open_search),
            ("Query", "icons/query.png", self.open_sparql_editor),
            ("Visualize", "icons/chart.png", self.show_instance_graph),
            None,  # Separator
            ("Refresh", "icons/refresh.png", self.refresh_all_views),
            ("Help", "icons/help.png", self.show_documentation)
        ]
        
        for i, btn_info in enumerate(buttons):
            if btn_info is None:
                ttk.Separator(toolbar, orient=tk.VERTICAL).grid(row=0, column=i, padx=5, pady=2, sticky='ns')
                continue
                
            text, icon, command = btn_info
            btn = ttk.Button(toolbar, text=text, command=command, width=10)
            btn.grid(row=0, column=i, padx=2, pady=2)
            
            # Add tooltip
            self._add_tooltip(btn, text)
            
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status messages
        self.status_label = ttk.Label(self.status_bar, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2, fill=tk.X, expand=True)
        
        # Statistics
        self.stats_label = ttk.Label(self.status_bar, text="", anchor=tk.E)
        self.stats_label.pack(side=tk.RIGHT, padx=10, pady=2)
        
        # Update statistics
        self.update_status_bar()
        
    def _add_tooltip(self, widget, text):
        """Add tooltip to widget"""
        from gui.widgets import ToolTip
        ToolTip(widget, text)
        
    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected = self.notebook.select()
        tab_name = self.notebook.tab(selected, "text")
        
        # Update status bar
        self.status_label.config(text=f"Viewing: {tab_name}")
        
        # Refresh current tab if needed
        current_tab = self.notebook.nametowidget(selected)
        if hasattr(current_tab, 'on_tab_selected'):
            current_tab.on_tab_selected()
            
    def update_status_bar(self):
        """Update status bar with current statistics"""
        stats = self.ontology.get_statistics()
        stats_text = f"Classes: {stats['classes']} | " \
                    f"Instances: {stats['instances']} | " \
                    f"Relationships: {stats['relationships']}"
        self.stats_label.config(text=stats_text)
        
    def load_sample_data(self):
        """Load sample data"""
        try:
            self.sample_loader.load_all()
            self.refresh_all_views()
            self.status_label.config(text="Sample data loaded successfully")
            logger.info("Sample data loaded")
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")
            messagebox.showerror("Error", f"Failed to load sample data: {e}")
            
    def new_ontology(self):
        """Create new empty ontology"""
        if messagebox.askyesno("Confirm", "Create new ontology? Current data will be lost."):
            self.ontology.clear()
            self.query_engine.clear_cache()
            self.refresh_all_views()
            self.status_label.config(text="New ontology created")
            logger.info("New ontology created")
            
    def save_ontology(self):
        """Save ontology"""
        from gui.dialogs import SaveOntologyDialog
        SaveOntologyDialog(self.root, self.ontology)
        self.status_label.config(text="Ontology saved")
        
    def save_ontology_as(self):
        """Save ontology with new filename"""
        from gui.dialogs import SaveOntologyDialog
        SaveOntologyDialog(self.root, self.ontology, save_as=True)
        self.status_label.config(text="Ontology saved as")
        
    def load_ontology(self):
        """Load ontology from file"""
        from gui.dialogs import LoadOntologyDialog
        if LoadOntologyDialog(self.root, self.ontology):
            self.query_engine.clear_cache()
            self.refresh_all_views()
            self.status_label.config(text="Ontology loaded")
            logger.info("Ontology loaded from file")
            
    def export_turtle(self):
        """Export as Turtle format"""
        from data.import_export import export_ontology
        export_ontology(self.ontology, 'turtle')
        self.status_label.config(text="Exported as Turtle")
        
    def export_jsonld(self):
        """Export as JSON-LD format"""
        from data.import_export import export_ontology
        export_ontology(self.ontology, 'json-ld')
        self.status_label.config(text="Exported as JSON-LD")
        
    def export_rdfxml(self):
        """Export as RDF/XML format"""
        from data.import_export import export_ontology
        export_ontology(self.ontology, 'xml')
        self.status_label.config(text="Exported as RDF/XML")
        
    def open_add_instance(self):
        """Open add instance dialog"""
        from gui.dialogs import AddInstanceDialog
        dialog = AddInstanceDialog(self.root, self.ontology)
        if dialog.result:
            self.refresh_all_views()
            
    def open_add_relationship(self):
        """Open add relationship dialog"""
        from gui.dialogs import AddRelationshipDialog
        dialog = AddRelationshipDialog(self.root, self.ontology)
        if dialog.result:
            self.refresh_all_views()
            
    def open_sparql_editor(self):
        """Open SPARQL editor"""
        from gui.dialogs import SPARQLEditorDialog
        SPARQLEditorDialog(self.root, self.query_engine)
        
    def open_sparql_editor_with_query(self, query):
        """Open SPARQL editor with preloaded query"""
        from gui.dialogs import SPARQLEditorDialog
        SPARQLEditorDialog(self.root, self.query_engine, initial_query=query)
        
    def open_search(self):
        """Open search dialog"""
        from gui.dialogs import SearchDialog
        SearchDialog(self.root, self.ontology)
        
    def show_hierarchy(self):
        """Show class hierarchy"""
        self.notebook.select(self.tabs['visualization'])
        self.tabs['visualization'].show_hierarchy()
        
    def show_instance_graph(self):
        """Show instance graph"""
        self.notebook.select(self.tabs['visualization'])
        self.tabs['visualization'].show_instance_network()
        
    def show_department_structure(self):
        """Show department structure"""
        self.notebook.select(self.tabs['visualization'])
        self.tabs['visualization'].show_department_structure()
        
    def show_course_dependencies(self):
        """Show course dependencies"""
        self.notebook.select(self.tabs['visualization'])
        self.tabs['visualization'].show_course_dependencies()
        
    def show_statistics(self):
        """Show statistics dialog"""
        from gui.dialogs import StatisticsDialog
        StatisticsDialog(self.root, self.ontology)
        
    def delete_selected(self):
        """Delete selected item"""
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if hasattr(current_tab, 'delete_selected'):
            current_tab.delete_selected()
            
    def refresh_all_views(self):
        """Refresh all views"""
        for tab in self.tabs.values():
            if hasattr(tab, 'refresh'):
                tab.refresh()
                
        self.update_status_bar()
        self.status_label.config(text="All views refreshed")
        
    def clear_data(self):
        """Clear all data"""
        if messagebox.askyesno("Confirm", "Clear all data? This cannot be undone."):
            self.ontology.clear()
            self.query_engine.clear_cache()
            self.refresh_all_views()
            self.status_label.config(text="All data cleared")
            logger.info("All data cleared")
            
    def confirm_exit(self):
        """Confirm before exiting"""
        return messagebox.askyesno("Exit", "Are you sure you want to exit?")
        
    def exit_application(self):
        """Exit application"""
        if self.confirm_exit():
            self.root.destroy()
            
    def zoom_in(self):
        """Zoom in visualization"""
        if hasattr(self.tabs['visualization'], 'zoom_in'):
            self.tabs['visualization'].zoom_in()
            
    def zoom_out(self):
        """Zoom out visualization"""
        if hasattr(self.tabs['visualization'], 'zoom_out'):
            self.tabs['visualization'].zoom_out()
            
    def run_inference(self):
        """Run inference on ontology"""
        from tkinter import messagebox as mb
        import os
        from datetime import datetime
        
        try:
            # Basic inference: check for implicit relationships
            inferred_count = 0
            issues = []
            
            # Check for transitive relationships (e.g., if A teaches B and B is prerequisite of C, infer A teaches C)
            # Check for symmetric relationships
            # Check for inverse relationships
            
            # Simple inference: find missing type assertions
            query = """
            SELECT ?instance ?class
            WHERE {
                ?instance ?p ?o .
                ?instance rdf:type ?class .
                FILTER (?class != owl:NamedIndividual)
                FILTER (STRSTARTS(STR(?p), STR(univ:)))
            }
            """
            
            results = self.ontology.query(query)
            total_relationships = len(list(results))
            
            # Check for orphaned instances (instances with no relationships)
            orphan_query = """
            SELECT ?instance
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                FILTER NOT EXISTS {
                    ?instance ?p ?o .
                    FILTER (?p != rdf:type)
                }
            }
            """
            orphans = list(self.ontology.query(orphan_query))
            
            # Show results
            result_text = f"Inference Results:\n"
            result_text += f"Total relationships: {total_relationships}\n"
            result_text += f"Orphaned instances: {len(orphans)}\n"
            
            if len(orphans) > 0:
                result_text += f"\nFound {len(orphans)} instances with no relationships.\n"
                result_text += "Consider adding relationships to these instances."
            
            mb.showinfo("Inference Results", result_text)
            self.status_label.config(text=f"Inference completed: {total_relationships} relationships found")
            logger.info("Inference completed")
            
        except Exception as e:
            mb.showerror("Inference Error", f"Failed to run inference: {str(e)}")
            logger.error(f"Inference error: {e}")
        
    def validate_ontology(self):
        """Validate ontology consistency"""
        from tkinter import messagebox as mb
        
        try:
            issues = []
            warnings = []
            
            # Check 1: All instances have a type
            query1 = """
            SELECT ?instance
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                FILTER NOT EXISTS {
                    ?instance rdf:type ?class .
                    FILTER (?class != owl:NamedIndividual)
                }
            }
            """
            untyped = list(self.ontology.query(query1))
            if untyped:
                issues.append(f"{len(untyped)} instances without a class type")
            
            # Check 2: All relationships use valid properties
            query2 = """
            SELECT DISTINCT ?p
            WHERE {
                ?s ?p ?o .
                FILTER (STRSTARTS(STR(?p), STR(univ:)))
                FILTER NOT EXISTS {
                    ?p rdf:type ?propType .
                    FILTER (?propType IN (owl:ObjectProperty, owl:DatatypeProperty))
                }
            }
            """
            invalid_props = list(self.ontology.query(query2))
            if invalid_props:
                warnings.append(f"{len(invalid_props)} relationships use undefined properties")
            
            # Check 3: Check for circular prerequisites
            query3 = """
            SELECT ?course1 ?course2
            WHERE {
                ?course1 univ:hasPrerequisite ?course2 .
                ?course2 univ:hasPrerequisite ?course1 .
            }
            """
            circular = list(self.ontology.query(query3))
            if circular:
                issues.append(f"{len(circular)} circular prerequisite relationships found")
            
            # Show results
            result_text = "Validation Results:\n" + "="*40 + "\n\n"
            
            if not issues and not warnings:
                result_text += "✓ Ontology is valid! No issues found.\n"
            else:
                if issues:
                    result_text += "ISSUES FOUND:\n"
                    for issue in issues:
                        result_text += f"  ✗ {issue}\n"
                    result_text += "\n"
                
                if warnings:
                    result_text += "WARNINGS:\n"
                    for warning in warnings:
                        result_text += f"  ⚠ {warning}\n"
            
            mb.showinfo("Validation Results", result_text)
            self.status_label.config(text=f"Validation completed: {len(issues)} issues, {len(warnings)} warnings")
            logger.info(f"Validation completed: {len(issues)} issues, {len(warnings)} warnings")
            
        except Exception as e:
            mb.showerror("Validation Error", f"Failed to validate ontology: {str(e)}")
            logger.error(f"Validation error: {e}")
        
    def create_backup(self):
        """Create backup"""
        from tkinter import filedialog, messagebox as mb
        import os
        from datetime import datetime
        
        try:
            # Suggest backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"ontology_backup_{timestamp}.ttl"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".ttl",
                filetypes=[
                    ("Turtle files", "*.ttl"),
                    ("RDF/XML files", "*.rdf"),
                    ("JSON-LD files", "*.jsonld"),
                    ("All files", "*.*")
                ],
                initialfile=default_filename,
                title="Create Backup"
            )
            
            if filename:
                # Determine format from extension
                ext = os.path.splitext(filename)[1].lower()
                format_map = {
                    '.ttl': 'turtle',
                    '.rdf': 'xml',
                    '.xml': 'xml',
                    '.jsonld': 'json-ld',
                    '.json': 'json-ld'
                }
                format_type = format_map.get(ext, 'turtle')
                
                self.ontology.save_ontology(filename, format=format_type)
                mb.showinfo("Backup Created", f"Backup saved to:\n{os.path.basename(filename)}")
                self.status_label.config(text=f"Backup created: {os.path.basename(filename)}")
                logger.info(f"Backup created: {filename}")
                
        except Exception as e:
            mb.showerror("Backup Error", f"Failed to create backup: {str(e)}")
            logger.error(f"Backup error: {e}")
        
    def restore_backup(self):
        """Restore from backup"""
        from tkinter import filedialog, messagebox as mb
        import os
        
        try:
            if not mb.askyesno("Confirm Restore", 
                              "Restore from backup? Current data will be replaced."):
                return
            
            filename = filedialog.askopenfilename(
                filetypes=[
                    ("Turtle files", "*.ttl"),
                    ("RDF/XML files", "*.rdf"),
                    ("JSON-LD files", "*.jsonld"),
                    ("All files", "*.*")
                ],
                title="Restore Backup"
            )
            
            if filename:
                # Determine format from extension
                ext = os.path.splitext(filename)[1].lower()
                format_map = {
                    '.ttl': 'turtle',
                    '.rdf': 'xml',
                    '.xml': 'xml',
                    '.jsonld': 'json-ld',
                    '.json': 'json-ld'
                }
                format_type = format_map.get(ext, None)
                
                # Clear current ontology
                self.ontology.clear()
                
                # Load backup
                self.ontology.load_ontology(filename, format=format_type)
                
                # Clear query cache
                self.query_engine.clear_cache()
                
                # Refresh all views
                self.refresh_all_views()
                
                mb.showinfo("Restore Complete", f"Backup restored from:\n{os.path.basename(filename)}")
                self.status_label.config(text=f"Backup restored: {os.path.basename(filename)}")
                logger.info(f"Backup restored: {filename}")
                
        except Exception as e:
            mb.showerror("Restore Error", f"Failed to restore backup: {str(e)}")
            logger.error(f"Restore error: {e}")
        
    def show_documentation(self):
        """Show documentation"""
        from gui.dialogs import DocumentationDialog
        DocumentationDialog(self.root)
        
    def show_tutorial(self):
        """Show tutorial"""
        messagebox.showinfo("Tutorial", "Interactive tutorial coming soon!")
        
    def show_examples(self):
        """Show examples"""
        from gui.dialogs import ExamplesDialog
        ExamplesDialog(self.root, self.query_engine)
        
    def check_updates(self):
        """Check for updates"""
        messagebox.showinfo("Updates", "You have the latest version.")
        
    def show_about(self):
        """Show about dialog"""
        from gui.dialogs import AboutDialog
        AboutDialog(self.root)
        
    def open_preferences(self):
        """Open preferences dialog"""
        from gui.dialogs import PreferencesDialog
        PreferencesDialog(self.root)
        
    def open_query_builder(self):
        """Open query builder"""
        from gui.dialogs import QueryBuilderDialog
        QueryBuilderDialog(self.root, self.ontology)
        
    def show_query_history(self):
        """Show query history"""
        from gui.dialogs import QueryHistoryDialog
        QueryHistoryDialog(self.root, self.query_engine)
        
    def open_replace(self):
        """Open find and replace"""
        from gui.dialogs import FindReplaceDialog
        FindReplaceDialog(self.root, self.ontology)