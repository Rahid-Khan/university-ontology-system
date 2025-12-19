"""
Interactive node dragging and automated movement system
"""

import networkx as nx
import numpy as np

class InteractiveNodeDragger:
    """Interactive node dragging with automated movement"""
    
    def __init__(self, fig, ax, graph, pos, node_colors, node_sizes, labels=None):
        self.fig = fig
        self.ax = ax
        self.graph = graph
        self.pos = pos.copy()  # Make a copy to modify
        self.node_colors = node_colors
        self.node_sizes = node_sizes
        self.labels = labels or {}
        
        # Dragging state
        self.dragging = False
        self.dragged_node = None
        self.drag_offset = (0, 0)
        
        # Automated movement state
        self.auto_movement = False
        self.auto_movement_timer = None
        
        # Connect events
        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
    def on_press(self, event):
        """Handle mouse press event"""
        if event.inaxes != self.ax:
            return
        
        # Find closest node
        closest_node = None
        min_distance = float('inf')
        
        for node, (x, y) in self.pos.items():
            # Calculate distance in data coordinates
            dx = event.xdata - x
            dy = event.ydata - y
            distance = np.sqrt(dx*dx + dy*dy)
            
            # Check if click is within node radius (approximate)
            node_idx = list(self.graph.nodes()).index(node)
            node_size = self.node_sizes[node_idx] if node_idx < len(self.node_sizes) else 500
            # Convert size to data coordinates (approximate)
            radius = np.sqrt(node_size / np.pi) * 0.01  # Approximate conversion
            
            if distance < radius and distance < min_distance:
                min_distance = distance
                closest_node = node
        
        if closest_node:
            self.dragging = True
            self.dragged_node = closest_node
            # Calculate offset
            node_x, node_y = self.pos[closest_node]
            self.drag_offset = (event.xdata - node_x, event.ydata - node_y)
            self.fig.canvas.draw_idle()
    
    def on_motion(self, event):
        """Handle mouse motion event"""
        if not self.dragging or self.dragged_node is None:
            return
        
        if event.inaxes != self.ax:
            return
        
        # Update node position
        if event.xdata is not None and event.ydata is not None:
            self.pos[self.dragged_node] = (event.xdata - self.drag_offset[0], 
                                          event.ydata - self.drag_offset[1])
            self.redraw()
    
    def on_release(self, event):
        """Handle mouse release event"""
        if self.dragging:
            self.dragging = False
            self.dragged_node = None
            self.drag_offset = (0, 0)
            self.fig.canvas.draw_idle()
    
    def redraw(self):
        """Redraw the graph with updated positions"""
        self.ax.clear()
        self.ax.set_axis_off()
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph, self.pos, ax=self.ax,
            edge_color='gray',
            width=2,
            alpha=0.6
        )
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, self.pos, ax=self.ax,
            node_color=self.node_colors,
            node_size=self.node_sizes,
            edgecolors='black',
            linewidths=1,
            alpha=0.85
        )
        
        # Draw labels
        if self.labels:
            nx.draw_networkx_labels(
                self.graph, self.pos, self.labels, ax=self.ax,
                font_size=9,
                font_weight='bold',
                alpha=0.8
            )
        
        # Set limits
        if len(self.pos) > 0:
            x_coords = [pos[0] for pos in self.pos.values()]
            y_coords = [pos[1] for pos in self.pos.values()]
            if x_coords and y_coords:
                x_margin = (max(x_coords) - min(x_coords)) * 0.1 if max(x_coords) != min(x_coords) else 0.5
                y_margin = (max(y_coords) - min(y_coords)) * 0.1 if max(y_coords) != min(y_coords) else 0.5
                self.ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
                self.ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()
    
    def start_auto_movement(self, callback=None):
        """Start automated node movement (physics simulation)"""
        self.auto_movement = True
        self._auto_move_step(callback)
    
    def stop_auto_movement(self):
        """Stop automated node movement"""
        self.auto_movement = False
        if self.auto_movement_timer:
            self.fig.canvas.stop_event_loop()
    
    def _auto_move_step(self, callback=None):
        """Perform one step of automated movement"""
        if not self.auto_movement:
            return
        
        # Apply spring force simulation (simplified)
        # Nodes move towards equilibrium positions
        try:
            # Calculate forces (simplified spring layout)
            forces = {node: np.array([0.0, 0.0]) for node in self.graph.nodes()}
            
            # Repulsion between all nodes
            k_repel = 0.15
            for node1 in self.graph.nodes():
                for node2 in self.graph.nodes():
                    if node1 != node2 and node1 in self.pos and node2 in self.pos:
                        dx = self.pos[node2][0] - self.pos[node1][0]
                        dy = self.pos[node2][1] - self.pos[node1][1]
                        dist = np.sqrt(dx*dx + dy*dy)
                        if dist > 0:
                            force = k_repel / (dist * dist + 0.01)  # Add small value to avoid division by zero
                            forces[node1] -= np.array([force * dx / dist, force * dy / dist])
            
            # Attraction along edges
            k_attract = 0.02
            for edge in self.graph.edges():
                if edge[0] in self.pos and edge[1] in self.pos:
                    dx = self.pos[edge[1]][0] - self.pos[edge[0]][0]
                    dy = self.pos[edge[1]][1] - self.pos[edge[0]][1]
                    dist = np.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        force = k_attract * dist
                        forces[edge[0]] += np.array([force * dx / dist, force * dy / dist])
                        forces[edge[1]] -= np.array([force * dx / dist, force * dy / dist])
            
            # Apply forces (with damping)
            damping = 0.7
            max_velocity = 0.5  # Limit maximum movement per step
            for node in self.graph.nodes():
                if node in self.pos and node in forces:
                    # Don't move if being dragged
                    if self.dragging and node == self.dragged_node:
                        continue
                    
                    force = forces[node] * damping
                    # Limit velocity
                    force_magnitude = np.sqrt(force[0]*force[0] + force[1]*force[1])
                    if force_magnitude > max_velocity:
                        force = force * (max_velocity / force_magnitude)
                    
                    self.pos[node] = (
                        self.pos[node][0] + force[0],
                        self.pos[node][1] + force[1]
                    )
            
            # Redraw
            self.redraw()
            
            # Schedule next step using Tkinter's after method if callback provided
            if callback:
                callback()
            else:
                # Use matplotlib's timer for continuous animation
                if self.auto_movement:
                    self.fig.canvas.start_event_loop(timeout=0.05)
                    if self.auto_movement:
                        self._auto_move_step(callback)
        except Exception as e:
            print(f"Auto movement error: {e}")
            import traceback
            traceback.print_exc()
            self.auto_movement = False
    
    def disconnect(self):
        """Disconnect event handlers"""
        if hasattr(self, 'cid_press'):
            self.fig.canvas.mpl_disconnect(self.cid_press)
        if hasattr(self, 'cid_release'):
            self.fig.canvas.mpl_disconnect(self.cid_release)
        if hasattr(self, 'cid_motion'):
            self.fig.canvas.mpl_disconnect(self.cid_motion)
        self.stop_auto_movement()

