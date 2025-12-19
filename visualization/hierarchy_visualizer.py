"""
Class hierarchy visualization with interactive features
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import matplotlib.cm as cm

class HierarchyVisualizer:
    """Interactive class hierarchy visualizer"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.DiGraph()
        self.node_details = {}
        
    def build_hierarchy(self, filter_text=None):
        """Build hierarchy graph from ontology"""
        self.graph.clear()
        self.node_details.clear()
        
        # Get class hierarchy
        hierarchy = self.ontology.get_class_hierarchy()
        
        # Add ALL nodes first (even without subclasses)
        # First pass: collect all nodes that match filter or are connected to matching nodes
        matching_classes = set()
        all_classes = set()
        
        for class_name, info in hierarchy.items():
            all_classes.add(class_name)
            if filter_text:
                filter_lower = filter_text.lower()
                # Match if class name, label, or comment contains filter
                label = info.get('label', '').lower()
                comment = info.get('comment', '').lower()
                if (filter_lower in class_name.lower() or 
                    filter_lower in label or 
                    filter_lower in comment):
                    matching_classes.add(class_name)
                    # Also include subclasses
                    for subclass in info.get('subclasses', []):
                        matching_classes.add(subclass)
            else:
                matching_classes.add(class_name)
        
        # Add nodes (all if no filter, or matching ones if filter exists)
        for class_name, info in hierarchy.items():
            if not filter_text or class_name in matching_classes:
                self.graph.add_node(class_name)
                self.node_details[class_name] = {
                    'label': info['label'],
                    'comment': info['comment'],
                    'instance_count': info['instance_count'],
                    'subclasses': info['subclasses']
                }
            
        # Add edges for subclass relationships
        for class_name, info in hierarchy.items():
            if class_name not in self.graph:
                continue
                
            for subclass in info['subclasses']:
                if subclass in self.graph:
                    # Add edge from parent to child (subclass is child of parent)
                    self.graph.add_edge(class_name, subclass)
                    
        return self.graph
        
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize hierarchy"""
        ax.clear()  # ✅ IMPORTANT

        # Build graph
        self.build_hierarchy(filter_text)

        if len(self.graph.nodes) == 0:
            ax.text(0.5, 0.5, "No classes found",
                    ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return

        # Choose layout - use hierarchical layout if there are edges, otherwise use simpler layout
        if len(self.graph.edges) > 0:
            # Use hierarchical layout for better visualization of subclass relationships
            if layout == 'spring':
                pos = nx.spring_layout(self.graph, seed=42, k=2.0)
            elif layout == 'circular':
                pos = nx.circular_layout(self.graph)
            elif layout == 'kamada_kawai':
                try:
                    pos = nx.kamada_kawai_layout(self.graph)
                except:
                    pos = nx.spring_layout(self.graph, seed=42, k=2.0)
            elif layout == 'spectral':
                try:
                    pos = nx.spectral_layout(self.graph)
                except:
                    pos = nx.spring_layout(self.graph, seed=42, k=2.0)
            elif layout == 'shell':
                pos = nx.shell_layout(self.graph)
            else:
                pos = nx.random_layout(self.graph, seed=42)
        else:
            # If no edges (no subclass relationships), use a grid or circular layout
            if layout == 'circular':
                pos = nx.circular_layout(self.graph)
            elif layout == 'spring':
                # Use spring layout even without edges - it will distribute nodes
                pos = nx.spring_layout(self.graph, seed=42, k=2.0, iterations=50)
            else:
                # Create a grid layout for isolated nodes
                nodes = list(self.graph.nodes())
                n = len(nodes)
                if n > 0:
                    cols = int(n ** 0.5) + 1
                    pos = {}
                    for i, node in enumerate(nodes):
                        row = i // cols
                        col = i % cols
                        pos[node] = (col * 2, -row * 2)  # Spacing between nodes
                else:
                    pos = {}

        node_colors = []
        node_sizes = []

        for node in self.graph.nodes():
            details = self.node_details[node]
            count = details['instance_count']

            if count == 0:
                color = 'lightgray'
            elif count < 5:
                color = 'lightblue'
            elif count < 20:
                color = 'lightgreen'
            else:
                color = 'lightcoral'

            node_colors.append(color)

            size = kwargs.get('node_size', 600) + count * 30
            node_sizes.append(min(size, 2200))

        # Animation support
        animate = kwargs.get('animate', False)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos, ax=ax,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors='black',
            linewidths=1,
            alpha=0.85
        )

        # Draw edges
        nx.draw_networkx_edges(
            self.graph, pos, ax=ax,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=14,
            edge_color='gray',
            width=kwargs.get('edge_width', 2),
            alpha=0.6
        )

        # Labels - show all labels for hierarchy
        labels = {node: self.node_details[node]['label'] for node in self.graph.nodes()}
        nx.draw_networkx_labels(
            self.graph, pos, labels, ax=ax,
            font_size=kwargs.get('font_size', 10),
            font_weight='bold',
            alpha=0.8
        )
        
        # Store data for animation and interaction
        animate = kwargs.get('animate', False)
        interactive = kwargs.get('interactive', True)
        
        self._viz_data = {
            'graph': self.graph,
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
        if interactive and not animate:
            try:
                from visualization.interactive_dragger import InteractiveNodeDragger
                self._dragger = InteractiveNodeDragger(
                    ax.figure, ax, self.graph, pos, node_colors, node_sizes, labels
                )
            except Exception as e:
                print(f"Could not enable interactive dragging: {e}")
                self._dragger = None

        ax.set_title(
            f"Class Hierarchy ({len(self.graph.nodes)} classes)",
            fontsize=14,
            fontweight='bold'
        )

        ax.set_axis_off()

        # ✅ VERY IMPORTANT - Set proper axis limits
        ax.relim()
        ax.autoscale_view()
        
        # Ensure we have proper view limits with adequate margins
        if len(self.graph.nodes) > 0 and len(pos) > 0:
            x_coords = [pos[node][0] for node in self.graph.nodes() if node in pos]
            y_coords = [pos[node][1] for node in self.graph.nodes() if node in pos]
            if x_coords and y_coords:
                x_range = max(x_coords) - min(x_coords)
                y_range = max(y_coords) - min(y_coords)
                x_margin = max(x_range * 0.15, 0.5) if x_range > 0 else 1.0
                y_margin = max(y_range * 0.15, 0.5) if y_range > 0 else 1.0
                ax.set_xlim(min(x_coords) - x_margin, max(x_coords) + x_margin)
                ax.set_ylim(min(y_coords) - y_margin, max(y_coords) + y_margin)

        self._add_legend(ax)

        
    def _add_legend(self, ax):
        """Add legend to plot"""
        import matplotlib.patches as mpatches
        
        legend_patches = [
            mpatches.Patch(color='lightgray', label='No instances'),
            mpatches.Patch(color='lightblue', label='1-4 instances'),
            mpatches.Patch(color='lightgreen', label='5-19 instances'),
            mpatches.Patch(color='lightcoral', label='20+ instances')
        ]
        
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.node_details:
            return "No data available"
            
        details = f"CLASS HIERARCHY VISUALIZATION\n"
        details += "="*40 + "\n\n"
        details += f"Total classes: {len(self.graph.nodes)}\n"
        details += f"Total edges: {len(self.graph.edges)}\n\n"
        
        details += "CLASS DETAILS:\n"
        details += "-"*30 + "\n"
        
        for node, info in sorted(self.node_details.items()):
            details += f"\n{info['label']}:\n"
            details += f"  Instances: {info['instance_count']}\n"
            if info['subclasses']:
                details += f"  Subclasses: {', '.join(info['subclasses'][:3])}"
                if len(info['subclasses']) > 3:
                    details += f" ... and {len(info['subclasses']) - 3} more"
                details += "\n"
            if info['comment']:
                details += f"  Description: {info['comment'][:100]}...\n"
                
        return details
        
    def get_node_info(self, node_name):
        """Get detailed information about a specific node"""
        if node_name in self.node_details:
            info = self.node_details[node_name]
            details = f"Class: {info['label']}\n"
            details += f"Instances: {info['instance_count']}\n"
            details += f"Description: {info['comment']}\n"
            
            if info['subclasses']:
                details += f"Subclasses ({len(info['subclasses'])}):\n"
                for subclass in info['subclasses']:
                    details += f"  • {subclass}\n"
                    
            return details
        return f"Node '{node_name}' not found"