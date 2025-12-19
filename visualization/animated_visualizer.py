"""
Professional animation support for graph visualizations
Uses matplotlib FuncAnimation compatible with Tkinter backend
"""

try:
    import matplotlib.animation as animation
    import networkx as nx
    import numpy as np
    ANIMATION_AVAILABLE = True
except ImportError:
    ANIMATION_AVAILABLE = False
    animation = None
    np = None

class AnimatedGraphVisualizer:
    """Professional animation helper for graph visualizations"""
    
    @staticmethod
    def create_progressive_animation(fig, ax, graph, pos, node_colors, node_sizes,
                                    edge_width=2, node_alpha=0.85, edge_alpha=0.6,
                                    labels=None, interval=100, repeat=True):
        """
        Create a professional progressive animation showing nodes and edges appearing
        
        Args:
            fig: matplotlib figure
            ax: matplotlib axes
            graph: NetworkX graph
            pos: node positions dictionary
            node_colors: list of node colors
            node_sizes: list of node sizes
            edge_width: edge width
            node_alpha: node alpha transparency
            edge_alpha: edge alpha transparency
            labels: dictionary of node labels
            interval: animation interval in milliseconds
            repeat: whether to repeat animation
            
        Returns:
            matplotlib.animation.FuncAnimation object
        """
        if not ANIMATION_AVAILABLE or animation is None:
            return None
            
        nodes_list = list(graph.nodes())
        edges_list = list(graph.edges())
        
        # Create node color and size mappings
        node_color_map = {node: node_colors[i] for i, node in enumerate(nodes_list)}
        node_size_map = {node: node_sizes[i] for i, node in enumerate(nodes_list)}
        
        def animate(frame):
            """Animation function called for each frame"""
            ax.clear()
            ax.set_axis_off()
            
            # Calculate how many nodes/edges to show
            total_frames = len(nodes_list) + len(edges_list)
            if total_frames == 0:
                return []
            
            # Phase 1: Show nodes progressively
            nodes_to_show = min(frame, len(nodes_list))
            if nodes_to_show > 0:
                visible_nodes = nodes_list[:nodes_to_show]
                subgraph_nodes = graph.subgraph(visible_nodes)
                
                # Get colors and sizes for visible nodes
                visible_colors = [node_color_map[n] for n in visible_nodes]
                visible_sizes = [node_size_map[n] for n in visible_nodes]
                
                # Draw nodes with fade-in effect
                alpha = min(1.0, node_alpha * (nodes_to_show / len(nodes_list)))
                nx.draw_networkx_nodes(
                    subgraph_nodes, pos, ax=ax,
                    node_color=visible_colors,
                    node_size=visible_sizes,
                    edgecolors='black',
                    linewidths=1,
                    alpha=alpha
                )
                
                # Draw labels for visible nodes
                if labels:
                    visible_labels = {n: labels.get(n, str(n)) for n in visible_nodes if n in labels}
                    if visible_labels:
                        nx.draw_networkx_labels(
                            subgraph_nodes, pos, visible_labels, ax=ax,
                            font_size=9,
                            font_weight='bold',
                            alpha=0.8
                        )
            
            # Phase 2: Show edges progressively (after all nodes are shown)
            edges_start_frame = len(nodes_list)
            if frame > edges_start_frame:
                edges_to_show = min(frame - edges_start_frame, len(edges_list))
                if edges_to_show > 0:
                    visible_edges = edges_list[:edges_to_show]
                    edge_subgraph = graph.edge_subgraph(visible_edges)
                    
                    # Draw edges with fade-in effect
                    edge_alpha_val = min(1.0, edge_alpha * (edges_to_show / max(1, len(edges_list))))
                    nx.draw_networkx_edges(
                        edge_subgraph, pos, ax=ax,
                        edge_color='gray',
                        width=edge_width,
                        alpha=edge_alpha_val
                    )
            
            # Set title with progress (only during loading)
            if frame < total_frames:
                progress = min(100, int((frame / total_frames) * 100))
                ax.set_title(f"Loading... {progress}%", fontsize=12, alpha=0.5)
            
            # Set limits
            if len(nodes_list) > 0:
                x_coords = [pos[n][0] for n in nodes_list if n in pos]
                y_coords = [pos[n][1] for n in nodes_list if n in pos]
                if x_coords and y_coords:
                    x_margin = (max(x_coords) - min(x_coords)) * 0.1 if max(x_coords) != min(x_coords) else 0.5
                    y_margin = (max(y_coords) - min(y_coords)) * 0.1 if max(y_coords) != min(y_coords) else 0.5
                    ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
                    ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
            
            ax.relim()
            ax.autoscale_view()
            
            return []
        
        # Calculate total frames
        total_frames = len(nodes_list) + len(edges_list)
        
        # Create animation
        anim = animation.FuncAnimation(
            fig, animate,
            frames=total_frames,
            interval=interval,
            blit=False,
            repeat=repeat
        )
        
        return anim
    
    @staticmethod
    def create_pulsing_animation(fig, ax, graph, pos, node_colors, node_sizes,
                                base_sizes=None, pulse_factor=1.3, interval=200,
                                labels=None, edge_width=2, title=None):
        """
        Create a pulsing animation effect on nodes
        
        Args:
            fig: matplotlib figure
            ax: matplotlib axes
            graph: NetworkX graph
            pos: node positions dictionary
            node_colors: list of node colors
            node_sizes: list of node sizes (base sizes)
            base_sizes: original node sizes (if different from node_sizes)
            pulse_factor: factor by which nodes pulse (1.3 = 30% larger)
            interval: animation interval in milliseconds
            labels: dictionary of node labels
            edge_width: width of edges
            title: title for the plot
            
        Returns:
            matplotlib.animation.FuncAnimation object
        """
        if not ANIMATION_AVAILABLE or animation is None or np is None:
            return None
            
        if base_sizes is None:
            base_sizes = node_sizes.copy()
        
        nodes_list = list(graph.nodes())
        
        # Create default labels if not provided
        if labels is None:
            labels = {n: str(n)[:15] + '...' if len(str(n)) > 15 else str(n) 
                     for n in nodes_list}
        
        def animate(frame):
            """Animation function for pulsing effect"""
            ax.clear()
            ax.set_axis_off()
            
            # Calculate pulse based on sine wave
            pulse = 1.0 + (pulse_factor - 1.0) * (np.sin(frame * 0.1) * 0.5 + 0.5)
            
            # Apply pulse to node sizes
            pulsed_sizes = [int(size * pulse) for size in base_sizes]
            
            # Draw graph with pulsed sizes
            nx.draw_networkx_nodes(
                graph, pos, ax=ax,
                node_color=node_colors,
                node_size=pulsed_sizes,
                edgecolors='black',
                linewidths=1,
                alpha=0.85
            )
            
            nx.draw_networkx_edges(
                graph, pos, ax=ax,
                edge_color='gray',
                width=edge_width,
                alpha=0.6
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                graph, pos, labels, ax=ax,
                font_size=9,
                font_weight='bold',
                alpha=0.8
            )
            
            # Set title if provided
            if title:
                ax.set_title(title, fontsize=14, fontweight='bold')
            
            # Set limits
            if len(nodes_list) > 0:
                x_coords = [pos[n][0] for n in nodes_list if n in pos]
                y_coords = [pos[n][1] for n in nodes_list if n in pos]
                if x_coords and y_coords:
                    x_margin = (max(x_coords) - min(x_coords)) * 0.1 if max(x_coords) != min(x_coords) else 0.5
                    y_margin = (max(y_coords) - min(y_coords)) * 0.1 if max(y_coords) != min(y_coords) else 0.5
                    ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
                    ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)
            
            ax.relim()
            ax.autoscale_view()
            
            return []
        
        # Create infinite animation
        anim = animation.FuncAnimation(
            fig, animate,
            frames=200,  # Enough frames for smooth animation
            interval=interval,
            blit=False,
            repeat=True
        )
        
        return anim
