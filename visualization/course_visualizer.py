"""
Course dependencies visualization
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class CourseVisualizer:
    """Course dependencies visualizer"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.DiGraph()
        self.course_info = {}
        
    def build_course_graph(self, filter_text=None):
        """Build course dependencies graph"""
        self.graph.clear()
        self.course_info.clear()
        
        # Query courses and prerequisites
        query = """
        SELECT ?course ?courseName ?credits ?prereq ?prereqName
        WHERE {
            ?course rdf:type univ:Course .
            ?course univ:name ?courseName .
            OPTIONAL { ?course univ:credits ?credits }
            OPTIONAL {
                ?course univ:hasPrerequisite ?prereq .
                ?prereq univ:name ?prereqName
            }
        }
        ORDER BY ?course
        """
        
        results = self.ontology.query(query)
        
        for row in results:
            course_uri = str(row['course'])
            course_name = str(row['courseName'])
            prereq_name = str(row.get('prereqName', '')) if row.get('prereqName') else ''
            
            # Check if filter matches course or prerequisite
            if filter_text:
                filter_lower = filter_text.lower()
                matches = (filter_lower in course_name.lower() or 
                          filter_lower in prereq_name.lower())
                if not matches:
                    continue
                
            # Add course node
            if course_uri not in self.graph:
                credits_val = row.get('credits')
                credits = int(credits_val) if credits_val is not None and credits_val != '' else 0
                self.graph.add_node(course_uri)
                self.course_info[course_uri] = {
                    'name': course_name,
                    'credits': credits,
                    'prerequisites': [],
                    'dependents': []
                }
                
            # Add prerequisite if exists
            if row.get('prereq'):
                prereq_uri = str(row['prereq'])
                prereq_name = str(row['prereqName'])
                    
                # Add prerequisite node if not already present
                if prereq_uri not in self.graph:
                    self.graph.add_node(prereq_uri)
                    self.course_info[prereq_uri] = {
                        'name': prereq_name,
                        'credits': 0,
                        'prerequisites': [],
                        'dependents': []
                    }
                    
                # Add edge from prerequisite to course
                self.graph.add_edge(prereq_uri, course_uri)
                
                # Update course info
                if prereq_uri not in self.course_info[course_uri]['prerequisites']:
                    self.course_info[course_uri]['prerequisites'].append(prereq_uri)
                if course_uri not in self.course_info[prereq_uri]['dependents']:
                    self.course_info[prereq_uri]['dependents'].append(course_uri)
                    
        return self.graph
        
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize course dependencies"""
        ax.clear()  # ✅ ADD THIS AT START
        # Build graph
        self.build_course_graph(filter_text)
        
        if len(self.graph.nodes) == 0:
            ax.text(0.5, 0.5, "No courses found",
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
            
        # Prepare node colors and sizes based on connectivity
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes():
            info = self.course_info[node]
            
            # Color based on position in dependency chain
            if not info['prerequisites'] and info['dependents']:
                # Starting course (no prerequisites)
                color = '#99FF99'  # Light green
            elif info['prerequisites'] and not info['dependents']:
                # Ending course (no dependents)
                color = '#FF9999'  # Light red
            elif info['prerequisites'] and info['dependents']:
                # Intermediate course
                color = '#99CCFF'  # Light blue
            else:
                # Isolated course
                color = '#CCCCCC'  # Gray
                
            node_colors.append(color)
            
            # Size based on credits
            base_size = kwargs.get('node_size', 500)
            credit_size = info['credits'] * 50
            size = base_size + credit_size
            node_sizes.append(min(size, 1500))
            
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
        labels = {}
        for node in self.graph.nodes():
            info = self.course_info[node]
            # Truncate long course names
            name = info['name']
            if len(name) > 20:
                name = name[:17] + '...'
            labels[node] = f"{name}\n({info['credits']} cr)"
            
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
        title = f"Course Prerequisites ({len(self.graph.nodes)} courses)"
        if filter_text:
            title += f" - Filter: '{filter_text}'"
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Remove axes
        ax.set_axis_off()
        # ✅ ADD THESE CRITICAL LINES:
        ax.relim()
        ax.autoscale_view()
        
        # Add legend
        self._add_legend(ax)
        
    def _add_legend(self, ax):
        """Add legend to plot"""
        import matplotlib.patches as mpatches
        
        legend_patches = [
            mpatches.Patch(color='#99FF99', label='Starting Course'),
            mpatches.Patch(color='#99CCFF', label='Intermediate Course'),
            mpatches.Patch(color='#FF9999', label='Ending Course'),
            mpatches.Patch(color='#CCCCCC', label='Isolated Course')
        ]
        
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.course_info:
            return "No data available"
            
        details = f"COURSE DEPENDENCIES VISUALIZATION\n"
        details += "="*40 + "\n\n"
        
        details += f"Total courses: {len(self.graph.nodes)}\n"
        details += f"Total prerequisites: {len(self.graph.edges)}\n\n"
        
        # Calculate statistics
        total_credits = sum(info['credits'] for info in self.course_info.values())
        courses_with_prereqs = sum(1 for info in self.course_info.values() 
                                 if info['prerequisites'])
        courses_with_dependents = sum(1 for info in self.course_info.values() 
                                    if info['dependents'])
        
        details += "STATISTICS:\n"
        details += "-"*30 + "\n"
        details += f"Total credits: {total_credits}\n"
        details += f"Courses with prerequisites: {courses_with_prereqs}\n"
        details += f"Courses that are prerequisites: {courses_with_dependents}\n\n"
        
        # Find starting courses (no prerequisites)
        starting_courses = [node for node, info in self.course_info.items() 
                          if not info['prerequisites']]
        
        if starting_courses:
            details += "STARTING COURSES (no prerequisites):\n"
            details += "-"*40 + "\n"
            for course_uri in starting_courses[:10]:  # Show first 10
                info = self.course_info[course_uri]
                details += f"• {info['name']} ({info['credits']} credits)\n"
                if info['dependents']:
                    details += f"  → {len(info['dependents'])} dependent courses\n"
                    
        # Find ending courses (no dependents)
        ending_courses = [node for node, info in self.course_info.items() 
                        if not info['dependents']]
        
        if ending_courses:
            details += "\nENDING COURSES (no dependents):\n"
            details += "-"*40 + "\n"
            for course_uri in ending_courses[:10]:  # Show first 10
                info = self.course_info[course_uri]
                details += f"• {info['name']} ({info['credits']} credits)\n"
                if info['prerequisites']:
                    details += f"  ← {len(info['prerequisites'])} prerequisite courses\n"
                    
        return details
        
    def get_node_info(self, node_uri):
        """Get detailed information about a specific course"""
        if node_uri in self.course_info:
            info = self.course_info[node_uri]
            details = f"Course: {info['name']}\n"
            details += f"Credits: {info['credits']}\n"
            details += f"Prerequisites: {len(info['prerequisites'])}\n"
            details += f"Dependents: {len(info['dependents'])}\n"
            
            if info['prerequisites']:
                details += "\nPREREQUISITES:\n"
                for prereq_uri in info['prerequisites'][:5]:  # Show first 5
                    prereq_info = self.course_info.get(prereq_uri, {})
                    details += f"  • {prereq_info.get('name', 'Unknown')}\n"
                    
            if info['dependents']:
                details += "\nDEPENDENT COURSES:\n"
                for dependent_uri in info['dependents'][:5]:  # Show first 5
                    dependent_info = self.course_info.get(dependent_uri, {})
                    details += f"  • {dependent_info.get('name', 'Unknown')}\n"
                    
            return details
        return f"Course not found: {node_uri}"