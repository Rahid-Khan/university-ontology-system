"""
Animation helper for visualizations
"""

import matplotlib.animation as animation
from matplotlib import pyplot as plt
import networkx as nx

class GraphAnimator:
    """Helper class for animating graph visualizations"""
    
    @staticmethod
    def animate_progressive_drawing(ax, graph, pos, node_colors, node_sizes, 
                                   edge_width=2, node_alpha=0.85, edge_alpha=0.6,
                                   labels=None, interval=50):
        """Animate progressive drawing of graph nodes and edges"""
        
        nodes_list = list(graph.nodes())
        edges_list = list(graph.edges())
        
        def animate(frame):
            ax.clear()
            
            # Draw nodes up to current frame
            nodes_to_draw = nodes_list[:min(frame + 1, len(nodes_list))]
            if nodes_to_draw:
                subgraph = graph.subgraph(nodes_to_draw)
                node_colors_sub = [node_colors[nodes_list.index(n)] for n in nodes_to_draw]
                node_sizes_sub = [node_sizes[nodes_list.index(n)] for n in nodes_to_draw]
                
                nx.draw_networkx_nodes(
                    subgraph, pos, ax=ax,
                    node_color=node_colors_sub,
                    node_size=node_sizes_sub,
                    edgecolors='black',
                    linewidths=1,
                    alpha=node_alpha
                )
            
            # Draw edges for nodes that are already drawn
            if len(nodes_to_draw) > 1:
                edges_to_draw = [e for e in edges_list 
                                if e[0] in nodes_to_draw and e[1] in nodes_to_draw]
                if edges_to_draw:
                    edge_subgraph = graph.edge_subgraph(edges_to_draw)
                    nx.draw_networkx_edges(
                        edge_subgraph, pos, ax=ax,
                        edge_color='gray',
                        width=edge_width,
                        alpha=edge_alpha
                    )
            
            # Draw labels
            if labels and nodes_to_draw:
                labels_sub = {n: labels.get(n, n) for n in nodes_to_draw if n in labels}
                if labels_sub:
                    nx.draw_networkx_labels(
                        graph.subgraph(nodes_to_draw), pos, labels_sub, ax=ax,
                        font_size=9,
                        font_weight='bold'
                    )
            
            ax.set_axis_off()
            ax.relim()
            ax.autoscale_view()
            
            return []
        
        frames = len(nodes_list)
        anim = animation.FuncAnimation(
            ax.figure, animate, frames=frames,
            interval=interval, blit=False, repeat=False
        )
        
        return anim

