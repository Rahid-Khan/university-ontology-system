"""
Student enrollment visualization
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

class StudentEnrollmentVisualizer:
    """Student enrollment visualizer"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.Graph()
        self.node_info = {}
        
    def build_enrollment_graph(self, filter_text=None):
        """Build student enrollment graph"""
        self.graph.clear()
        self.node_info.clear()
        
        # Query student enrollments
        query = """
        SELECT ?student ?studentName ?program ?programName ?course ?courseName ?gpa
        WHERE {
            ?student rdf:type univ:Student .
            ?student univ:name ?studentName .
            OPTIONAL { ?student univ:gpa ?gpa }
            OPTIONAL {
                ?student univ:enrolledIn ?program .
                ?program univ:name ?programName
            }
            OPTIONAL {
                ?student univ:takesCourse ?course .
                ?course univ:name ?courseName
            }
        }
        LIMIT 200
        """
        
        results = self.ontology.query(query)
        
        students = {}
        programs = {}
        courses = {}
        
        for row in results:
            student_uri = str(row['student'])
            student_name = str(row['studentName'])
            program_name = str(row.get('programName', '')) if row.get('programName') else ''
            course_name = str(row.get('courseName', '')) if row.get('courseName') else ''
            
            # Check if filter matches student, program, or course
            if filter_text:
                filter_lower = filter_text.lower()
                matches = (filter_lower in student_name.lower() or 
                          filter_lower in program_name.lower() or 
                          filter_lower in course_name.lower())
                if not matches:
                    continue
                
            # Add student node
            if student_uri not in students:
                gpa = float(row['gpa']) if row.get('gpa') else 0.0
                students[student_uri] = {
                    'name': student_name,
                    'gpa': gpa
                }
                self.graph.add_node(student_uri, type='student', label=student_name)
                self.node_info[student_uri] = {
                    'type': 'student',
                    'name': student_name,
                    'gpa': gpa,
                    'programs': [],
                    'courses': []
                }
            
            # Add program connection
            if row.get('program'):
                program_uri = str(row['program'])
                program_name = str(row['programName'])
                    
                if program_uri not in programs:
                    programs[program_uri] = program_name
                    self.graph.add_node(program_uri, type='program', label=program_name)
                    self.node_info[program_uri] = {
                        'type': 'program',
                        'name': program_name,
                        'students': []
                    }
                
                if not self.graph.has_edge(student_uri, program_uri):
                    self.graph.add_edge(student_uri, program_uri)
                    self.node_info[student_uri]['programs'].append(program_uri)
                    self.node_info[program_uri]['students'].append(student_uri)
            
            # Add course connection
            if row.get('course'):
                course_uri = str(row['course'])
                course_name = str(row['courseName'])
                    
                if course_uri not in courses:
                    courses[course_uri] = course_name
                    self.graph.add_node(course_uri, type='course', label=course_name)
                    self.node_info[course_uri] = {
                        'type': 'course',
                        'name': course_name,
                        'students': []
                    }
                
                if not self.graph.has_edge(student_uri, course_uri):
                    self.graph.add_edge(student_uri, course_uri)
                    self.node_info[student_uri]['courses'].append(course_uri)
                    self.node_info[course_uri]['students'].append(student_uri)
                    
        return self.graph
        
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize student enrollment"""
        ax.clear()
        
        # Build graph
        self.build_enrollment_graph(filter_text)
        
        if len(self.graph.nodes) == 0:
            ax.text(0.5, 0.5, "No enrollment data found",
                   ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return
            
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, seed=42, k=1.5)
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
            if node_type == 'student':
                # Color by GPA if available
                info = self.node_info.get(node, {})
                gpa = info.get('gpa', 0.0)
                if gpa >= 3.5:
                    color = '#99FF99'  # Green (high GPA)
                elif gpa >= 2.5:
                    color = '#FFCC99'  # Orange (medium GPA)
                elif gpa > 0:
                    color = '#FF9999'  # Red (low GPA)
                else:
                    color = '#CCCCCC'  # Gray (no GPA)
                size = kwargs.get('node_size', 400) + degree * 30
            elif node_type == 'program':
                color = '#99CCFF'  # Light blue
                size = kwargs.get('node_size', 500) + 300
            elif node_type == 'course':
                color = '#FF99CC'  # Light pink
                size = kwargs.get('node_size', 400) + degree * 20
            else:
                color = '#CCCCCC'
                size = kwargs.get('node_size', 400)
                
            node_colors.append(color)
            node_sizes.append(min(size, 2000))
            
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, ax=ax,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8,
                              edgecolors='black',
                              linewidths=1)
        
        # Draw edges
        edge_width = kwargs.get('edge_width', 1.5)
        nx.draw_networkx_edges(self.graph, pos, ax=ax,
                              edge_color='gray',
                              width=edge_width,
                              alpha=0.5)
        
        # Draw labels - show all nodes with proper names
        font_size = kwargs.get('font_size', 9)
        labels = {}
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'unknown')
            label = self.graph.nodes[node].get('label', node.split('#')[-1])
            
            # Show all labels, but adjust size based on importance
            if len(label) > 15:
                label = label[:12] + '...'
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
        title = f"Student Enrollment Network ({len(self.graph.nodes)} nodes)"
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
            mpatches.Patch(color='#99FF99', label='Student (High GPA)'),
            mpatches.Patch(color='#FFCC99', label='Student (Medium GPA)'),
            mpatches.Patch(color='#FF9999', label='Student (Low GPA)'),
            mpatches.Patch(color='#99CCFF', label='Program'),
            mpatches.Patch(color='#FF99CC', label='Course')
        ]
        
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.node_info:
            return "No data available"
            
        details = f"STUDENT ENROLLMENT VISUALIZATION\n"
        details += "="*40 + "\n\n"
        
        # Count by type
        type_counts = defaultdict(int)
        for info in self.node_info.values():
            type_counts[info['type']] += 1
            
        details += f"Total nodes: {len(self.graph.nodes)}\n"
        details += f"Total edges: {len(self.graph.edges)}\n\n"
        
        details += "NODE TYPE DISTRIBUTION:\n"
        details += "-"*30 + "\n"
        for type_name in ['student', 'program', 'course']:
            if type_name in type_counts:
                details += f"{type_name.capitalize()}s: {type_counts[type_name]}\n"
                
        # Student statistics
        students = [node for node, info in self.node_info.items() 
                   if info['type'] == 'student']
        
        if students:
            gpas = [self.node_info[s]['gpa'] for s in students if self.node_info[s]['gpa'] > 0]
            if gpas:
                avg_gpa = sum(gpas) / len(gpas)
                details += f"\nAverage GPA: {avg_gpa:.2f}\n"
                details += f"Students with GPA: {len(gpas)}/{len(students)}\n"
                
        # Most enrolled programs
        programs = [node for node, info in self.node_info.items() 
                   if info['type'] == 'program']
        
        if programs:
            program_enrollments = [(p, len(self.node_info[p]['students'])) 
                                  for p in programs]
            program_enrollments.sort(key=lambda x: x[1], reverse=True)
            
            details += "\nMOST ENROLLED PROGRAMS:\n"
            details += "-"*30 + "\n"
            for prog_uri, count in program_enrollments[:5]:
                prog_info = self.node_info[prog_uri]
                details += f"{prog_info['name']}: {count} students\n"
                
        return details
        
    def get_node_info(self, node_uri):
        """Get detailed information about a specific node"""
        if node_uri in self.node_info:
            info = self.node_info[node_uri]
            details = f"Node: {info.get('name', node_uri.split('#')[-1])}\n"
            details += f"Type: {info['type'].capitalize()}\n"
            
            if info['type'] == 'student':
                if info.get('gpa', 0) > 0:
                    details += f"GPA: {info['gpa']:.2f}\n"
                if 'programs' in info:
                    details += f"Programs: {len(info['programs'])}\n"
                if 'courses' in info:
                    details += f"Courses: {len(info['courses'])}\n"
                    
            elif info['type'] == 'program' and 'students' in info:
                details += f"Students: {len(info['students'])}\n"
                
            elif info['type'] == 'course' and 'students' in info:
                details += f"Students: {len(info['students'])}\n"
                
            return details
        return f"Node not found: {node_uri}"

