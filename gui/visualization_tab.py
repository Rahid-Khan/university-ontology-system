"""
Interactive visualization tab with responsive graphs - FIXED VERSION
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import networkx as nx

from config.settings import Colors, Settings
from visualization.hierarchy_visualizer import HierarchyVisualizer
from visualization.network_visualizer import NetworkVisualizer
from visualization.department_visualizer import DepartmentVisualizer
from visualization.course_visualizer import CourseVisualizer
from visualization.student_enrollment_visualizer import StudentEnrollmentVisualizer
from visualization.research_network_visualizer import ResearchNetworkVisualizer
from visualization.temporal_visualizer import TemporalVisualizer
from visualization.interactive_plot import InteractivePlot

class VisualizationTab(ttk.Frame):
    """Interactive visualization tab"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_visualization = None
        self.zoom_level = 1.0
        self._current_animation = None  # Store current animation
        self.create_widgets()
        
    def create_widgets(self):
        """Create visualization widgets"""
        # Control panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Visualization type selection
        ttk.Label(control_frame, text="Visualization Type:").pack(side=tk.LEFT, padx=5)
        
        self.viz_type = ttk.Combobox(control_frame, 
                                    values=[
                                        "Class Hierarchy", 
                                        "Instance Network",
                                        "Department Structure", 
                                        "Course Dependencies",
                                        "Student Enrollment",
                                        "Research Network",
                                        "Temporal Analysis"
                                    ],
                                    width=20,
                                    state='readonly')
        self.viz_type.pack(side=tk.LEFT, padx=5)
        self.viz_type.set("Class Hierarchy")
        self.viz_type.bind('<<ComboboxSelected>>', self.on_viz_type_changed)
        
        # Filters
        ttk.Label(control_frame, text="Filter:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_entry = ttk.Entry(control_frame, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        self.filter_entry.bind('<KeyRelease>', self.on_filter_changed)
        
        # Layout algorithm
        ttk.Label(control_frame, text="Layout:").pack(side=tk.LEFT, padx=(20, 5))
        self.layout_var = tk.StringVar(value="spring")
        layout_combo = ttk.Combobox(control_frame, 
                                   textvariable=self.layout_var,
                                   values=["spring", "circular", "kamada_kawai", 
                                           "spectral", "shell", "random"],
                                   width=15,
                                   state='readonly')
        layout_combo.pack(side=tk.LEFT, padx=5)
        layout_combo.bind('<<ComboboxSelected>>', self.on_layout_changed)
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(button_frame, text="Generate",
                  command=self.generate_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Refresh",
                  command=self.refresh_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Save",
                  command=self.save_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Zoom In",
                  command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Zoom Out",
                  command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset View",
                  command=self.reset_view).pack(side=tk.LEFT, padx=2)
        
        # Create main visualization area
        viz_container = ttk.Frame(self)
        viz_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create matplotlib figure with subplots
        self.fig = Figure(figsize=(10, 8), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('white')
        
        # Create side panel for details (this creates the paned window and viz_frame)
        self.create_side_panel(viz_container)
        
        # Create canvas AFTER viz_frame is created, with viz_frame as parent
        self.canvas = FigureCanvasTkAgg(self.fig, self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.viz_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Ensure canvas is visible and draw initial empty figure
        self.canvas.get_tk_widget().update_idletasks()
        self.canvas.draw()
        
        # Initialize visualizers
        self.visualizers = {
            'Class Hierarchy': HierarchyVisualizer(self.app.ontology),
            'Instance Network': NetworkVisualizer(self.app.ontology),
            'Department Structure': DepartmentVisualizer(self.app.ontology),
            'Course Dependencies': CourseVisualizer(self.app.ontology),
            'Student Enrollment': StudentEnrollmentVisualizer(self.app.ontology),
            'Research Network': ResearchNetworkVisualizer(self.app.ontology),
            'Temporal Analysis': TemporalVisualizer(self.app.ontology)
        }
        
        # Interactive plot handler
        self.interactive_plot = None
        
        # Generate initial visualization
        self.after(100, self.generate_visualization)  # Delay to ensure GUI is ready
        
    def create_side_panel(self, parent):
        """Create side panel for details and controls"""
        # Create paned window for resizable side panel
        self.paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Add visualization frame to paned window (canvas will be added later)
        self.viz_frame = ttk.Frame(self.paned)
        self.paned.add(self.viz_frame, weight=3)
        
        # Create side panel frame
        side_frame = ttk.Frame(self.paned, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.paned.add(side_frame, weight=1)
        
        # Details section
        details_frame = ttk.LabelFrame(side_frame, text="Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Details text
        self.details_text = tk.Text(details_frame, height=20, wrap=tk.WORD,
                                   font=('Arial', 9))
        scrollbar = ttk.Scrollbar(details_frame, command=self.details_text.yview)
        self.details_text.config(yscrollcommand=scrollbar.set)
        
        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Controls section
        controls_frame = ttk.LabelFrame(side_frame, text="Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Node size control
        ttk.Label(controls_frame, text="Node Size:").pack(anchor=tk.W)
        self.node_size = tk.IntVar(value=Settings.NODE_SIZE)
        size_scale = ttk.Scale(controls_frame, from_=100, to=2000,
                              variable=self.node_size, orient=tk.HORIZONTAL,
                              command=lambda v: self.refresh_visualization())
        size_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Edge width control
        ttk.Label(controls_frame, text="Edge Width:").pack(anchor=tk.W)
        self.edge_width = tk.IntVar(value=Settings.EDGE_WIDTH)
        edge_scale = ttk.Scale(controls_frame, from_=1, to=10,
                              variable=self.edge_width, orient=tk.HORIZONTAL,
                              command=lambda v: self.refresh_visualization())
        edge_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Font size control
        ttk.Label(controls_frame, text="Font Size:").pack(anchor=tk.W)
        self.font_size = tk.IntVar(value=Settings.FONT_SIZE)
        font_scale = ttk.Scale(controls_frame, from_=6, to=20,
                              variable=self.font_size, orient=tk.HORIZONTAL,
                              command=lambda v: self.refresh_visualization())
        font_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Color scheme
        ttk.Label(controls_frame, text="Color Scheme:").pack(anchor=tk.W)
        self.color_scheme = tk.StringVar(value="viridis")
        color_combo = ttk.Combobox(controls_frame,
                                  textvariable=self.color_scheme,
                                  values=["viridis", "plasma", "coolwarm", 
                                         "Set2", "Set3", "tab20c"],
                                  state='readonly')
        color_combo.pack(fill=tk.X, pady=(0, 10))
        color_combo.bind('<<ComboboxSelected>>', self.on_color_scheme_changed)
        
        # Animation toggle
        self.animate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls_frame, text="Animate",
                       variable=self.animate_var,
                       command=self.on_animate_changed).pack(anchor=tk.W)
        
        # Interactive dragging toggle
        self.interactive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(controls_frame, text="Interactive Dragging",
                       variable=self.interactive_var,
                       command=self.on_interactive_changed).pack(anchor=tk.W)
        
        # Auto movement toggle
        self.auto_movement_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(controls_frame, text="Auto Movement",
                       variable=self.auto_movement_var,
                       command=self.on_auto_movement_changed).pack(anchor=tk.W)
        
    def on_viz_type_changed(self, event=None):
        """Handle visualization type change"""
        self.after(200, self.generate_visualization)
        
    def on_filter_changed(self, event=None):
        """Handle filter change"""
        # Debounce: only refresh after user stops typing
        if hasattr(self, '_filter_timer'):
            self.after_cancel(self._filter_timer)
        self._filter_timer = self.after(500, self.refresh_visualization)
        
    def on_layout_changed(self, event=None):
        """Handle layout algorithm change"""
        self.refresh_visualization()
        
    # def on_node_size_changed(self, event=None):
    #     """Handle node size change"""
    #     pass  # Now handled by scale command
        
    # def on_edge_width_changed(self, event=None):
    #     """Handle edge width change"""
    #     pass  # Now handled by scale command
        
    # def on_font_size_changed(self, event=None):
    #     """Handle font size change"""
    #     pass  # Now handled by scale command
        
    def on_color_scheme_changed(self, event=None):
        """Handle color scheme change"""
        self.refresh_visualization()
    
    def on_animate_changed(self):
        """Handle animation checkbox change"""
        # Stop any running animations
        if hasattr(self, '_current_animation') and self._current_animation:
            try:
                self._current_animation.event_source.stop()
            except:
                pass
            self._current_animation = None
        
        # Refresh visualization
        self.refresh_visualization()
    
    def on_interactive_changed(self):
        """Handle interactive dragging checkbox change"""
        # Disconnect existing dragger
        if hasattr(self, '_current_dragger') and self._current_dragger:
            try:
                self._current_dragger.disconnect()
            except:
                pass
            self._current_dragger = None
        
        # Refresh to enable/disable dragging
        if self.current_visualization:
            self.refresh_visualization()
    
    def on_auto_movement_changed(self):
        """Handle auto movement checkbox change"""
        if hasattr(self, '_current_dragger') and self._current_dragger:
            if self.auto_movement_var.get():
                # Start auto movement
                self._current_dragger.start_auto_movement()
            else:
                # Stop auto movement
                self._current_dragger.stop_auto_movement()
        
    def generate_visualization(self):
        """Generate visualization based on selected type"""
        viz_type = self.viz_type.get()
        print(f"[DEBUG] Generating visualization: {viz_type}")
        print(f"[DEBUG] Ontology has {len(self.app.ontology.graph)} triples")
        # Clear previous visualization
        self.ax.clear()
        
        try:
            if viz_type in self.visualizers:
                print(f"[DEBUG] Using visualizer for {viz_type}")
                visualizer = self.visualizers[viz_type]
                # Get animation state
                animate = self.animate_var.get() if hasattr(self, 'animate_var') else False
                
                # Stop any existing animation
                if hasattr(self, '_current_animation') and self._current_animation:
                    try:
                        self._current_animation.event_source.stop()
                    except:
                        pass
                    self._current_animation = None
                
                # Get interactive state
                interactive = self.interactive_var.get() if hasattr(self, 'interactive_var') else True
                
                visualizer.visualize(
                    ax=self.ax,
                    filter_text=self.filter_entry.get(),
                    layout=self.layout_var.get(),
                    node_size=self.node_size.get(),
                    edge_width=self.edge_width.get(),
                    font_size=self.font_size.get(),
                    color_scheme=self.color_scheme.get(),
                    animate=animate,
                    interactive=interactive and not animate  # Disable dragging during animation
                )
                
                # Store dragger reference if created
                if hasattr(visualizer, '_dragger') and visualizer._dragger:
                    self._current_dragger = visualizer._dragger
                    # Start auto movement if enabled
                    if hasattr(self, 'auto_movement_var') and self.auto_movement_var.get():
                        def auto_move_callback():
                            """Callback for auto movement"""
                            if (hasattr(self, '_current_dragger') and 
                                self._current_dragger and 
                                self._current_dragger.auto_movement):
                                self.after(50, lambda: self._current_dragger._auto_move_step(auto_move_callback))
                        self._current_dragger.start_auto_movement(callback=auto_move_callback)
                
                # Start animation if enabled
                if animate and hasattr(visualizer, '_animation_data'):
                    try:
                        from visualization.animated_visualizer import AnimatedGraphVisualizer
                        anim_data = visualizer._animation_data
                        
                        # Create progressive animation
                        self._current_animation = AnimatedGraphVisualizer.create_progressive_animation(
                            fig=anim_data['fig'],
                            ax=anim_data['ax'],
                            graph=anim_data['graph'],
                            pos=anim_data['pos'],
                            node_colors=anim_data['node_colors'],
                            node_sizes=anim_data['node_sizes'],
                            edge_width=self.edge_width.get(),
                            labels=anim_data.get('labels'),
                            interval=80,  # Fast animation
                            repeat=False  # Play once
                        )
                        
                        if self._current_animation:
                            # After progressive animation, switch to pulsing
                            def switch_to_pulse():
                                """Switch to pulsing animation after progressive is done"""
                                if hasattr(self, '_current_animation') and self._current_animation:
                                    try:
                                        self._current_animation.event_source.stop()
                                    except:
                                        pass
                                
                                # Create pulsing animation
                                self._current_animation = AnimatedGraphVisualizer.create_pulsing_animation(
                                    fig=anim_data['fig'],
                                    ax=anim_data['ax'],
                                    graph=anim_data['graph'],
                                    pos=anim_data['pos'],
                                    node_colors=anim_data['node_colors'],
                                    node_sizes=anim_data['node_sizes'],
                                    base_sizes=anim_data['node_sizes'],
                                    pulse_factor=1.15,  # Subtle pulse
                                    interval=150,
                                    labels=anim_data.get('labels'),
                                    edge_width=self.edge_width.get(),
                                    title=f"{viz_type} (Animated)"
                                )
                            
                            # Schedule switch to pulsing after progressive animation completes
                            total_frames = len(anim_data['graph'].nodes()) + len(anim_data['graph'].edges())
                            animation_duration = total_frames * 0.08  # 80ms per frame
                            self.after(int(animation_duration * 1000), switch_to_pulse)
                    except Exception as e:
                        print(f"Animation error: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Store current visualization
                self.current_visualization = {
                    'type': viz_type,
                    'visualizer': visualizer,
                    'params': {
                        'filter': self.filter_entry.get(),
                        'layout': self.layout_var.get(),
                        'node_size': self.node_size.get(),
                        'edge_width': self.edge_width.get(),
                        'font_size': self.font_size.get(),
                        'color_scheme': self.color_scheme.get()
                    }
                }
                
                # Update details
                self.update_details(visualizer.get_details())
                
                # Setup interactive plot if enabled (optional feature)
                # Note: Interactive plot requires additional setup and may not work
                # with all visualization types, so we'll skip it for now
                # Uncomment below to enable interactive features
                # if hasattr(visualizer, 'graph') and visualizer.graph and len(visualizer.graph.nodes()) > 0:
                #     try:
                #         # Disconnect previous interactive plot
                #         if self.interactive_plot:
                #             self.interactive_plot.disconnect()
                #         # Interactive plot setup would go here
                #     except Exception as e:
                #         print(f"Could not create interactive plot: {e}")
                
            else:
                # Default visualization
                self.ax.text(0.5, 0.5, f"Visualization: {viz_type}\nComing Soon!",
                           ha='center', va='center', fontsize=16)
                self.ax.set_axis_off()
                
            print(f"[DEBUG] Visualization completed, redrawing canvas")
            # CRITICAL: Force the canvas to redraw
            self._redraw_canvas()
            print(f"[DEBUG] Canvas redrawn successfully")
            
        except Exception as e:
            import traceback
            print(f"Visualization error: {e}")
            print(traceback.format_exc())
            
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Error: {str(e)}",
                       ha='center', va='center', fontsize=12, color='red')
            self.ax.set_axis_off()
            self._redraw_canvas()
            
    def refresh_visualization(self):
        """Refresh current visualization"""
        # Stop any running animation
        if hasattr(self, '_current_animation') and self._current_animation:
            try:
                self._current_animation.event_source.stop()
            except:
                pass
            self._current_animation = None
        
        # Stop any running dragger
        if hasattr(self, '_current_dragger') and self._current_dragger:
            try:
                self._current_dragger.disconnect()
            except:
                pass
            self._current_dragger = None
        
        # Always regenerate, even if no current visualization
        self.after(200, self.generate_visualization)
            
    def update_details(self, details):
        """Update details panel"""
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        
    def save_visualization(self):
        """Save current visualization to file"""
        from tkinter import filedialog, messagebox
        import os
        
        filetypes = [
            ("PNG files", "*.png"),
            ("PDF files", "*.pdf"),
            ("SVG files", "*.svg"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            initialfile=f"visualization_{self.viz_type.get().replace(' ', '_')}.png"
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight',
                               facecolor=self.fig.get_facecolor())
                if hasattr(self.app, 'status_label'):
                    self.app.status_label.config(text=f"Saved: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Visualization saved to {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save: {str(e)}")
                
    def zoom_in(self):
        """Zoom in visualization"""
        self.zoom_level *= 1.2
        self.apply_zoom()
        
    def zoom_out(self):
        """Zoom out visualization"""
        self.zoom_level /= 1.2
        self.apply_zoom()
        
    def reset_view(self):
        """Reset zoom and view"""
        self.zoom_level = 1.0
        if self.current_visualization:
            self.after(200, self.generate_visualization)
        else:
            self.toolbar.home()  # Use matplotlib's home button
            
    def apply_zoom(self):
        """Apply zoom level to current visualization"""
        if self.current_visualization:
            self.ax.clear()
            visualizer = self.current_visualization['visualizer']
            params = self.current_visualization['params'].copy()
            
            # Adjust sizes based on zoom
            params['node_size'] = int(params['node_size'] * self.zoom_level)
            params['font_size'] = int(params['font_size'] * self.zoom_level)
            
            visualizer.visualize(ax=self.ax, **params)
            self._redraw_canvas()
            
    def show_hierarchy(self):
        """Show class hierarchy"""
        self.viz_type.set("Class Hierarchy")
        self.after(200, self.generate_visualization)
        
    def show_instance_network(self):
        """Show instance network"""
        self.viz_type.set("Instance Network")
        self.after(200, self.generate_visualization)
        
    def show_department_structure(self):
        """Show department structure"""
        self.viz_type.set("Department Structure")
        self.after(200, self.generate_visualization)
        
    def show_course_dependencies(self):
        """Show course dependencies"""
        self.viz_type.set("Course Dependencies")
        self.after(200, self.generate_visualization)
        
    def on_tab_selected(self):
        """Called when tab is selected"""
         # Only refresh if we have data
        if len(self.app.ontology.graph) > 0:
            self.refresh_visualization()
        else:
            # Show message if no data
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data loaded\n\nUse File → Import Sample Data",
                   ha='center', va='center', fontsize=14, color='gray')
            self.ax.set_axis_off()
            self._redraw_canvas()
        
    def refresh(self):
        """Refresh visualization"""
        self.refresh_visualization()
    
    def _redraw_canvas(self):
        """Force a reliable redraw of the Tk canvas - CRITICAL FIX"""
        try:
            # Step 1: Tight layout (if graph has content)
            if len(self.ax.get_children()) > 0:
                try:
                    self.fig.tight_layout(pad=1.0)
                except Exception:
                    pass
            
            # Step 2: Force canvas draw
            self.canvas.draw()
            
            # Step 3: Update Tk widget
            self.canvas.get_tk_widget().update_idletasks()
            
            # Step 4: Flush events
            self.canvas.get_tk_widget().update()
            # try:
            #     self.canvas.flush_events()
            # except Exception:
            #     pass
                
            # Step 5: Force another update after a brief moment
            # self.after(10, lambda: self.canvas.get_tk_widget().update())
             # Step 5: Flush any pending events
            try:
                self.canvas.flush_events()
            except (AttributeError, Exception):
                pass
            
        except Exception as e:
            print(f"Canvas redraw error: {e}")
            # Last resort
            try:
                self.canvas.draw()
                self.canvas.get_tk_widget().update()
            except Exception:
                pass