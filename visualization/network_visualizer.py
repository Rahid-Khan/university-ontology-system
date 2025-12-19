"""
Interactive network visualization for instances and relationships
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import math

class NetworkVisualizer:
    """Interactive network visualizer for instances"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.Graph()
        self.node_types = {}
        self.edge_types = {}
        
    def build_network(self, filter_text=None, max_nodes=100):
        """Build network graph from ontology instances"""
        self.graph.clear()
        self.node_types.clear()
        self.edge_types.clear()
        
        # Get relationships
        query = """
        SELECT ?subject ?predicate ?object ?subjectType ?objectType
        WHERE {
            ?subject ?predicate ?object .
            FILTER (isURI(?object))
            FILTER (STRSTARTS(STR(?predicate), STR(univ:)))
            ?subject rdf:type ?subjectType .
            ?object rdf:type ?objectType .
            FILTER (?subjectType != owl:NamedIndividual && ?objectType != owl:NamedIndividual)
        }
        LIMIT 500
        """
        
        results = self.ontology.query(query)
        
        node_counts = defaultdict(int)
        
        for row in results:
            subject = str(row['subject']).split('#')[-1]
            object_ = str(row['object']).split('#')[-1]
            predicate = str(row['predicate']).split('#')[-1]
            subject_type = str(row['subjectType']).split('#')[-1]
            object_type = str(row['objectType']).split('#')[-1]
            
            # Apply filter
            if filter_text:
                filter_lower = filter_text.lower()
                if (filter_lower not in subject.lower() and 
                    filter_lower not in object_.lower() and
                    filter_lower not in predicate.lower() and
                    filter_lower not in subject_type.lower() and
                    filter_lower not in object_type.lower()):
                    continue
                    
            # Add nodes with types
            if subject not in self.graph:
                self.graph.add_node(subject)
                self.node_types[subject] = subject_type
                node_counts[subject_type] += 1
                
            if object_ not in self.graph:
                self.graph.add_node(object_)
                self.node_types[object_] = object_type
                node_counts[object_type] += 1
                
            # Add edge with type
            edge_key = (subject, object_)
            self.graph.add_edge(subject, object_)
            self.edge_types[edge_key] = predicate
            
            # Limit number of nodes
            if len(self.graph.nodes) >= max_nodes:
                break
                
        return self.graph, node_counts
        
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize network"""
        ax.clear()  # ✅ IMPORTANT

        graph, node_counts = self.build_network(filter_text)

        if len(graph.nodes) == 0:
            ax.text(0.5, 0.5, "No instances found",
                    ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return

        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(graph, seed=42, k=1.3)
        elif layout == 'circular':
            pos = nx.circular_layout(graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(graph)
        elif layout == 'spectral':
            pos = nx.spectral_layout(graph)
        elif layout == 'shell':
            pos = nx.shell_layout(graph)
        else:
            pos = nx.random_layout(graph, seed=42)

        # Color mapping
        unique_types = list(set(self.node_types.values()))
        cmap = plt.cm.get_cmap(kwargs.get('color_scheme', 'viridis'))

        type_colors = {
            t: cmap(i / max(1, len(unique_types) - 1))
            for i, t in enumerate(unique_types)
        }

        node_colors = [type_colors[self.node_types[n]] for n in graph.nodes()]

        node_sizes = []
        for node in graph.nodes():
            degree = graph.degree(node)
            size = kwargs.get('node_size', 600) + degree * 60
            node_sizes.append(min(size, 2400))

        # Draw nodes
        nx.draw_networkx_nodes(
            graph, pos, ax=ax,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors='black',
            linewidths=1,
            alpha=0.85
        )

        # Draw edges
        nx.draw_networkx_edges(
            graph, pos, ax=ax,
            edge_color='gray',
            width=kwargs.get('edge_width', 2),
            alpha=0.6
        )
        
        # Labels - show all nodes, but truncate long names
        labels = {}
        font_size = kwargs.get('font_size', 9)
        for node in graph.nodes():
            node_name = str(node)
            # Truncate if too long
            if len(node_name) > 20:
                node_name = node_name[:17] + '...'
            labels[node] = node_name

        nx.draw_networkx_labels(
            graph, pos, labels, ax=ax,
            font_size=font_size,
            font_weight='bold',
            alpha=0.8
        )

        ax.set_title(
            f"Instance Network ({len(graph.nodes)} nodes, {len(graph.edges)} edges)",
            fontsize=14,
            fontweight='bold'
        )

        ax.set_axis_off()

        # ✅ CRITICAL
        ax.relim()
        ax.autoscale_view()

        self._add_legend(ax, type_colors, node_counts)
        
        # Store data for animation and interaction
        animate = kwargs.get('animate', False)
        interactive = kwargs.get('interactive', True)  # Enable by default
        
        # Store visualization data
        self._viz_data = {
            'graph': graph,
            'pos': pos,
            'node_colors': node_colors,
            'node_sizes': node_sizes,
            'labels': labels,
            'ax': ax,
            'fig': ax.figure
        }
        
        if animate:
            self._animation_data = self._viz_data.copy()
        
        # Setup interactive dragging if enabled
        if interactive and not animate:  # Don't enable dragging during animation
            try:
                from visualization.interactive_dragger import InteractiveNodeDragger
                self._dragger = InteractiveNodeDragger(
                    ax.figure, ax, graph, pos, node_colors, node_sizes, labels
                )
                # Store dragger reference
                self._dragger_ref = self._dragger
            except Exception as e:
                print(f"Could not enable interactive dragging: {e}")
                self._dragger = None

        
    def _add_legend(self, ax, type_colors, node_counts):
        """Add legend with node types"""
        import matplotlib.patches as mpatches
        
        legend_patches = []
        for type_name, color in sorted(type_colors.items()):
            count = node_counts.get(type_name, 0)
            patch = mpatches.Patch(color=color, 
                                  label=f"{type_name} ({count})")
            legend_patches.append(patch)
            
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.node_types:
            return "No data available"
            
        details = f"INSTANCE NETWORK VISUALIZATION\n"
        details += "="*40 + "\n\n"
        details += f"Total nodes: {len(self.graph.nodes)}\n"
        details += f"Total edges: {len(self.graph.edges)}\n\n"
        
        # Count by type
        type_counts = defaultdict(int)
        for node_type in self.node_types.values():
            type_counts[node_type] += 1
            
        details += "NODE TYPE DISTRIBUTION:\n"
        details += "-"*30 + "\n"
        for type_name, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            details += f"{type_name}: {count} nodes\n"
            
        # Most connected nodes
        if len(self.graph.nodes) > 0:
            details += "\nMOST CONNECTED NODES:\n"
            details += "-"*30 + "\n"
            
            nodes_by_degree = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)
            for node, degree in nodes_by_degree[:5]:
                node_type = self.node_types.get(node, 'Unknown')
                details += f"{node} ({node_type}): {degree} connections\n"
                
        return details
        
    def get_node_info(self, node_name):
        """Get detailed information about a specific node"""
        if node_name in self.node_types:
            node_type = self.node_types[node_name]
            details = f"Node: {node_name}\n"
            details += f"Type: {node_type}\n"
            
            # Get degree
            if node_name in self.graph:
                degree = self.graph.degree(node_name)
                details += f"Connections: {degree}\n"
                
                # Get neighbors
                neighbors = list(self.graph.neighbors(node_name))
                if neighbors:
                    details += f"\nConnected to ({len(neighbors)}):\n"
                    for neighbor in neighbors[:10]:  # Limit to 10
                        neighbor_type = self.node_types.get(neighbor, 'Unknown')
                        edge_key = (node_name, neighbor)
                        if edge_key in self.edge_types:
                            relationship = self.edge_types[edge_key]
                            details += f"  • {neighbor} ({neighbor_type}) via {relationship}\n"
                        else:
                            details += f"  • {neighbor} ({neighbor_type})\n"
                            
                    if len(neighbors) > 10:
                        details += f"  ... and {len(neighbors) - 10} more\n"
                        
            return details
        return f"Node '{node_name}' not found"