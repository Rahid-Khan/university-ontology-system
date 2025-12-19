"""
Research network visualization
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class ResearchNetworkVisualizer:
    """Research network visualizer"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.Graph()
        self.node_info = {}
        
    def build_research_graph(self, filter_text=None):
        """Build research network graph"""
        self.graph.clear()
        self.node_info.clear()
        
        # Query research network - match actual data structure
        query = """
        SELECT ?research ?researchName ?researcher ?researcherName 
               ?publication ?pubName
        WHERE {
            ?research rdf:type univ:Research .
            ?research univ:name ?researchName .
            OPTIONAL {
                ?researcher univ:partOfResearch ?research .
                ?researcher univ:name ?researcherName
            }
            OPTIONAL {
                ?researcher univ:partOfResearch ?research .
                ?researcher univ:published ?publication .
                ?publication univ:name ?pubName
            }
        }
        LIMIT 200
        """
        
        results = self.ontology.query(query)
        
        researches = {}
        researchers = {}
        publications = {}
        
        for row in results:
            research_uri = str(row['research'])
            research_name = str(row['researchName'])
            researcher_name = str(row.get('researcherName', '')) if row.get('researcherName') else ''
            pub_name = str(row.get('pubName', '')) if row.get('pubName') else ''
            
            # Check if filter matches research, researcher, or publication
            if filter_text:
                filter_lower = filter_text.lower()
                matches = (filter_lower in research_name.lower() or 
                          filter_lower in researcher_name.lower() or 
                          filter_lower in pub_name.lower())
                if not matches:
                    continue
                
            # Add research node
            if research_uri not in researches:
                researches[research_uri] = research_name
                self.graph.add_node(research_uri, type='research', label=research_name)
                self.node_info[research_uri] = {
                    'type': 'research',
                    'name': research_name,
                    'researchers': [],
                    'publications': [],
                    'grants': []
                }
            
            # Add researcher connection
            if row.get('researcher'):
                researcher_uri = str(row['researcher'])
                researcher_name = str(row['researcherName'])
                    
                if researcher_uri not in researchers:
                    researchers[researcher_uri] = researcher_name
                    self.graph.add_node(researcher_uri, type='researcher', label=researcher_name)
                    self.node_info[researcher_uri] = {
                        'type': 'researcher',
                        'name': researcher_name,
                        'researches': [],
                        'publications': []
                    }
                
                if not self.graph.has_edge(research_uri, researcher_uri):
                    self.graph.add_edge(research_uri, researcher_uri)
                    self.node_info[research_uri]['researchers'].append(researcher_uri)
                    self.node_info[researcher_uri]['researches'].append(research_uri)
            
            # Add publication connection
            if row.get('publication'):
                pub_uri = str(row['publication'])
                pub_name = str(row['pubName'])
                    
                if pub_uri not in publications:
                    publications[pub_uri] = pub_name
                    self.graph.add_node(pub_uri, type='publication', label=pub_name)
                    self.node_info[pub_uri] = {
                        'type': 'publication',
                        'name': pub_name,
                        'researches': []
                    }
                
                if not self.graph.has_edge(research_uri, pub_uri):
                    self.graph.add_edge(research_uri, pub_uri)
                    self.node_info[research_uri]['publications'].append(pub_uri)
                    self.node_info[pub_uri]['researches'].append(research_uri)
            
                    
        return self.graph
        
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize research network"""
        ax.clear()
        
        # Build graph
        self.build_research_graph(filter_text)
        
        if len(self.graph.nodes) == 0:
            ax.text(0.5, 0.5, "No research data found",
                   ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return
            
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, seed=42, k=1.8)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == 'shell':
            pos = nx.shell_layout(self.graph)
        else:
            pos = nx.random_layout(self.graph, seed=42)
            
        # Prepare node colors and sizes
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'unknown')
            degree = self.graph.degree(node)
            
            # Color by type
            if node_type == 'research':
                color = '#FF9999'  # Light red
                size = kwargs.get('node_size', 600) + 400
            elif node_type == 'researcher':
                color = '#99CCFF'  # Light blue
                size = kwargs.get('node_size', 500) + degree * 40
            elif node_type == 'publication':
                color = '#99FF99'  # Light green
                size = kwargs.get('node_size', 400) + degree * 30
            else:
                color = '#CCCCCC'
                size = kwargs.get('node_size', 400)
                
            node_colors.append(color)
            node_sizes.append(min(size, 2200))
            
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, ax=ax,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8,
                              edgecolors='black',
                              linewidths=1)
        
        # Draw edges
        edge_width = kwargs.get('edge_width', 2)
        nx.draw_networkx_edges(self.graph, pos, ax=ax,
                              edge_color='gray',
                              width=edge_width,
                              alpha=0.6)
        
        # Draw labels - show all nodes
        font_size = kwargs.get('font_size', 9)
        labels = {}
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'unknown')
            label = self.graph.nodes[node].get('label', node.split('#')[-1])
            
            # Show all labels, truncate if too long
            if len(label) > 20:
                label = label[:17] + '...'
            labels[node] = label
                
        nx.draw_networkx_labels(self.graph, pos, labels, ax=ax,
                               font_size=font_size,
                               font_weight='bold',
                               alpha=0.8)
        
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
        
        # Add title
        title = f"Research Network ({len(self.graph.nodes)} nodes)"
        if filter_text:
            title += f" - Filter: '{filter_text}'"
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Remove axes
        ax.set_axis_off()
        ax.relim()
        ax.autoscale_view()
        
        # Add legend
        self._add_legend(ax)
        
    def _add_legend(self, ax):
        """Add legend to plot"""
        import matplotlib.patches as mpatches
        
        legend_patches = [
            mpatches.Patch(color='#FF9999', label='Research'),
            mpatches.Patch(color='#99CCFF', label='Researcher'),
            mpatches.Patch(color='#99FF99', label='Publication')
        ]
        
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.node_info:
            return "No data available"
            
        details = f"RESEARCH NETWORK VISUALIZATION\n"
        details += "="*40 + "\n\n"
        
        # Count by type
        type_counts = defaultdict(int)
        for info in self.node_info.values():
            type_counts[info['type']] += 1
            
        details += f"Total nodes: {len(self.graph.nodes)}\n"
        details += f"Total edges: {len(self.graph.edges)}\n\n"
        
        details += "NODE TYPE DISTRIBUTION:\n"
        details += "-"*30 + "\n"
        for type_name in ['research', 'researcher', 'publication']:
            if type_name in type_counts:
                details += f"{type_name.capitalize()}s: {type_counts[type_name]}\n"
                
        # Most connected researchers
        researchers = [node for node, info in self.node_info.items() 
                      if info['type'] == 'researcher']
        
        if researchers:
            researcher_connections = [(r, len(self.node_info[r]['researches'])) 
                                     for r in researchers]
            researcher_connections.sort(key=lambda x: x[1], reverse=True)
            
            details += "\nMOST ACTIVE RESEARCHERS:\n"
            details += "-"*30 + "\n"
            for res_uri, count in researcher_connections[:5]:
                res_info = self.node_info[res_uri]
                details += f"{res_info['name']}: {count} research projects\n"
                
        return details
        
    def get_node_info(self, node_uri):
        """Get detailed information about a specific node"""
        if node_uri in self.node_info:
            info = self.node_info[node_uri]
            details = f"Node: {info.get('name', node_uri.split('#')[-1])}\n"
            details += f"Type: {info['type'].capitalize()}\n"
            
            if info['type'] == 'research':
                if 'researchers' in info:
                    details += f"Researchers: {len(info['researchers'])}\n"
                if 'publications' in info:
                    details += f"Publications: {len(info['publications'])}\n"
                    
            elif info['type'] == 'researcher' and 'researches' in info:
                details += f"Research Projects: {len(info['researches'])}\n"
                
            elif info['type'] == 'publication':
                if 'researches' in info:
                    details += f"Related Research: {len(info['researches'])}\n"
                    
            return details
        return f"Node not found: {node_uri}"

