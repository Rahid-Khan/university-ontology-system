"""
Interactive plot with zoom, pan, and click events
"""

import matplotlib.pyplot as plt
from matplotlib.backend_bases import PickEvent
import networkx as nx

class InteractivePlot:
    """Interactive plot with event handling"""
    
    def __init__(self, fig, ax, graph, node_positions, node_details=None):
        self.fig = fig
        self.ax = ax
        self.graph = graph
        self.pos = node_positions
        self.node_details = node_details or {}
        self.selected_node = None
        
        # Connect events
        self.cid_pick = self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
    def on_pick(self, event):
        """Handle node pick event"""
        if isinstance(event, PickEvent) and hasattr(event.artist, 'get_label'):
            node = event.artist.get_label()
            if node and node in self.graph:
                self.highlight_node(node)
                return True
        return False
        
    def on_click(self, event):
        """Handle mouse click event"""
        if event.inaxes != self.ax:
            return
            
        # Find closest node
        closest_node = None
        min_distance = float('inf')
        
        for node, (x, y) in self.pos.items():
            distance = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_node = node
                
        # If click is close to a node, select it
        if closest_node and min_distance < 0.05:  # Threshold
            self.highlight_node(closest_node)
            
    def highlight_node(self, node):
        """Highlight a node and show details"""
        # Clear previous highlights
        self.clear_highlights()
        
        # Store selected node
        self.selected_node = node
        
        # Highlight node
        if node in self.pos:
            x, y = self.pos[node]
            
            # Draw circle around node
            circle = plt.Circle((x, y), 0.1, color='red', fill=False, 
                              linewidth=2, alpha=0.7)
            self.ax.add_patch(circle)
            
            # Highlight connected edges
            self.highlight_edges(node)
            
            # Show details in annotation
            self.show_details_annotation(node, x, y)
            
        self.fig.canvas.draw_idle()
        
    def highlight_edges(self, node):
        """Highlight edges connected to node"""
        if node not in self.graph:
            return
            
        # Get edges
        edges = list(self.graph.edges(node))
        
        # Draw highlighted edges
        for u, v in edges:
            if u in self.pos and v in self.pos:
                x1, y1 = self.pos[u]
                x2, y2 = self.pos[v]
                
                # Draw thicker edge
                self.ax.plot([x1, x2], [y1, y2], 'r-', linewidth=3, alpha=0.7)
                
    def show_details_annotation(self, node, x, y):
        """Show details annotation for node"""
        # Remove previous annotation
        if hasattr(self, 'annotation'):
            self.annotation.remove()
            
        # Get node details
        details = self.get_node_details(node)
        
        # Create annotation
        self.annotation = self.ax.annotate(
            details,
            xy=(x, y),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.9),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2")
        )
        
    def get_node_details(self, node):
        """Get details for a node"""
        if node in self.node_details:
            return self.node_details[node]
        elif hasattr(self, 'get_node_info'):
            return self.get_node_info(node)
        else:
            return f"Node: {node}"
            
    def clear_highlights(self):
        """Clear all highlights"""
        # Remove annotations
        if hasattr(self, 'annotation'):
            self.annotation.remove()
            delattr(self, 'annotation')
            
        # Clear patches (circles)
        for patch in self.ax.patches[:]:
            patch.remove()
            
        # Clear highlighted edges (remove red lines)
        for line in self.ax.lines[:]:
            if line.get_color() == 'red':
                line.remove()
                
        self.selected_node = None
        
    def disconnect(self):
        """Disconnect event handlers"""
        if hasattr(self, 'cid_pick'):
            self.fig.canvas.mpl_disconnect(self.cid_pick)
        if hasattr(self, 'cid_click'):
            self.fig.canvas.mpl_disconnect(self.cid_click)