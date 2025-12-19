"""
Department structure visualization
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class DepartmentVisualizer:
    """Department structure visualizer"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.DiGraph()
        self.node_info = {}
        
    def build_department_graph(self, filter_text=None):
        """Build department structure graph"""
        self.graph.clear()
        self.node_info.clear()
        
        # Query department structure
        query = """
        SELECT ?dept ?deptName ?program ?programName ?course ?courseName
        WHERE {
            ?dept rdf:type univ:Department .
            ?dept univ:name ?deptName .
            OPTIONAL {
                ?dept univ:offersProgram ?program .
                ?program univ:name ?programName .
                OPTIONAL {
                    ?program univ:hasCourse ?course .
                    ?course univ:name ?courseName
                }
            }
        }
        ORDER BY ?dept ?program ?course
        """
        
        results = self.ontology.query(query)
        
        departments = set()
        programs = set()
        courses = set()
        
        for row in results:
            dept_uri = str(row['dept'])
            dept_name = str(row['deptName'])
            
            # Check if filter matches department, program, or course
            program_name = str(row.get('programName', '')) if row.get('programName') else ''
            course_name = str(row.get('courseName', '')) if row.get('courseName') else ''
            
            if filter_text:
                filter_lower = filter_text.lower()
                matches = (filter_lower in dept_name.lower() or 
                          filter_lower in program_name.lower() or 
                          filter_lower in course_name.lower())
                if not matches:
                    continue
                
            departments.add(dept_uri)
            self.graph.add_node(dept_uri, type='department', label=dept_name)
            self.node_info[dept_uri] = {
                'type': 'department',
                'name': dept_name,
                'programs': []
            }
            
            if row.get('program'):
                program_uri = str(row['program'])
                program_name = str(row['programName'])
                    
                programs.add(program_uri)
                self.graph.add_node(program_uri, type='program', label=program_name)
                self.graph.add_edge(dept_uri, program_uri)
                
                self.node_info[dept_uri]['programs'].append(program_uri)
                self.node_info[program_uri] = {
                    'type': 'program',
                    'name': program_name,
                    'courses': []
                }
                
                if row.get('course'):
                    course_uri = str(row['course'])
                    course_name = str(row['courseName'])
                        
                    courses.add(course_uri)
                    self.graph.add_node(course_uri, type='course', label=course_name)
                    self.graph.add_edge(program_uri, course_uri)
                    
                    self.node_info[program_uri]['courses'].append(course_uri)
                    self.node_info[course_uri] = {
                        'type': 'course',
                        'name': course_name
                    }
                    
        return self.graph
        
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize department structure"""
        ax.clear()
        # Build graph
        self.build_department_graph(filter_text)
        
        if len(self.graph.nodes) == 0:
            ax.text(0.5, 0.5, "No departments found",
                   ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return
            
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, seed=42, k=2)
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
            
            # Color by type
            if node_type == 'department':
                color = '#FF9999'  # Light red
                size = kwargs.get('node_size', 500) + 500
            elif node_type == 'program':
                color = '#99CCFF'  # Light blue
                size = kwargs.get('node_size', 500) + 200
            elif node_type == 'course':
                color = '#99FF99'  # Light green
                size = kwargs.get('node_size', 500)
            else:
                color = '#CCCCCC'  # Gray
                size = kwargs.get('node_size', 500)
                
            node_colors.append(color)
            node_sizes.append(size)
            
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
                              arrowstyle='->',
                              arrowsize=15,
                              edge_color='gray',
                              width=edge_width,
                              alpha=0.6)
        
        # Draw labels
        font_size = kwargs.get('font_size', 10)
        labels = {node: self.graph.nodes[node].get('label', node.split('#')[-1])
                 for node in self.graph.nodes()}
        
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
        title = f"Department Structure"
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
            mpatches.Patch(color='#FF9999', label='Department'),
            mpatches.Patch(color='#99CCFF', label='Program'),
            mpatches.Patch(color='#99FF99', label='Course')
        ]
        
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.node_info:
            return "No data available"
            
        details = f"DEPARTMENT STRUCTURE VISUALIZATION\n"
        details += "="*40 + "\n\n"
        
        # Count by type
        type_counts = defaultdict(int)
        for info in self.node_info.values():
            type_counts[info['type']] += 1
            
        details += f"Total nodes: {len(self.graph.nodes)}\n"
        details += f"Total edges: {len(self.graph.edges)}\n\n"
        
        details += "NODE TYPE DISTRIBUTION:\n"
        details += "-"*30 + "\n"
        for type_name in ['department', 'program', 'course']:
            if type_name in type_counts:
                details += f"{type_name.capitalize()}s: {type_counts[type_name]}\n"
                
        # List departments
        departments = [node for node, info in self.node_info.items() 
                      if info['type'] == 'department']
        
        if departments:
            details += "\nDEPARTMENTS:\n"
            details += "-"*30 + "\n"
            
            for dept in departments[:10]:  # Show first 10
                info = self.node_info[dept]
                details += f"\n{info['name']}:\n"
                if info['programs']:
                    details += f"  Programs: {len(info['programs'])}\n"
                    for prog_uri in info['programs'][:3]:  # Show first 3 programs
                        prog_info = self.node_info.get(prog_uri, {})
                        details += f"    • {prog_info.get('name', 'Unknown')}"
                        if 'courses' in prog_info:
                            details += f" ({len(prog_info['courses'])} courses)"
                        details += "\n"
                    if len(info['programs']) > 3:
                        details += f"    ... and {len(info['programs']) - 3} more\n"
                        
        return details
        
    def get_node_info(self, node_uri):
        """Get detailed information about a specific node"""
        if node_uri in self.node_info:
            info = self.node_info[node_uri]
            details = f"Node: {info.get('name', node_uri.split('#')[-1])}\n"
            details += f"Type: {info['type'].capitalize()}\n"
            
            if info['type'] == 'department' and 'programs' in info:
                details += f"Programs: {len(info['programs'])}\n"
                if info['programs']:
                    details += "\nProgram List:\n"
                    for prog_uri in info['programs'][:5]:  # Show first 5
                        prog_info = self.node_info.get(prog_uri, {})
                        details += f"  • {prog_info.get('name', 'Unknown')}\n"
                        
            elif info['type'] == 'program' and 'courses' in info:
                details += f"Courses: {len(info['courses'])}\n"
                if info['courses']:
                    details += "\nCourse List:\n"
                    for course_uri in info['courses'][:5]:  # Show first 5
                        course_info = self.node_info.get(course_uri, {})
                        details += f"  • {course_info.get('name', 'Unknown')}\n"
                        
            return details
        return f"Node not found: {node_uri}"