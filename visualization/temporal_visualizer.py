"""
Temporal analysis visualization
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

class TemporalVisualizer:
    """Temporal analysis visualizer"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.graph = nx.DiGraph()
        self.node_info = {}
        self.time_data = {}
        
    def build_temporal_graph(self, filter_text=None):
        """Build temporal graph"""
        self.graph.clear()
        self.node_info.clear()
        self.time_data.clear()
        
        # Query temporal data (events, courses by semester, etc.) - match actual data structure
        query = """
        SELECT ?event ?eventName ?eventDate ?course ?courseName ?semester
               ?student ?studentName ?startDate
        WHERE {
            {
                ?event rdf:type univ:Event .
                ?event univ:name ?eventName .
                OPTIONAL { ?event univ:startDate ?eventDate }
            } UNION {
                ?course rdf:type univ:Course .
                ?course univ:name ?courseName .
                OPTIONAL { ?course univ:semester ?semester }
            } UNION {
                ?student rdf:type univ:Student .
                ?student univ:name ?studentName .
                OPTIONAL { ?student univ:startDate ?startDate }
            }
        }
        LIMIT 300
        """
        
        results = self.ontology.query(query)
        
        events = {}
        courses = {}
        students = {}
        
        for row in results:
            # Collect all names for filter check
            event_name = str(row.get('eventName', '')) if row.get('eventName') else ''
            course_name = str(row.get('courseName', '')) if row.get('courseName') else ''
            student_name = str(row.get('studentName', '')) if row.get('studentName') else ''
            
            # Check if filter matches any entity
            if filter_text:
                filter_lower = filter_text.lower()
                matches = (filter_lower in event_name.lower() or 
                          filter_lower in course_name.lower() or 
                          filter_lower in student_name.lower())
                if not matches:
                    continue
            
            # Process events
            if row.get('event'):
                event_uri = str(row['event'])
                event_name = str(row['eventName'])
                    
                if event_uri not in events:
                    events[event_uri] = event_name
                    event_date = row.get('eventDate') or row.get('startDate')
                    date_str = str(event_date) if event_date else None
                    
                    self.graph.add_node(event_uri, type='event', label=event_name)
                    self.node_info[event_uri] = {
                        'type': 'event',
                        'name': event_name,
                        'date': date_str
                    }
                    if date_str:
                        self.time_data[event_uri] = self._parse_date(date_str)
            
            # Process courses
            if row.get('course'):
                course_uri = str(row['course'])
                course_name = str(row['courseName'])
                    
                if course_uri not in courses:
                    courses[course_uri] = course_name
                    semester = str(row['semester']) if row.get('semester') else None
                    
                    self.graph.add_node(course_uri, type='course', label=course_name)
                    self.node_info[course_uri] = {
                        'type': 'course',
                        'name': course_name,
                        'semester': semester
                    }
                    if semester:
                        self.time_data[course_uri] = self._parse_semester(semester)
            
            # Process students
            if row.get('student'):
                student_uri = str(row['student'])
                student_name = str(row['studentName'])
                    
                if student_uri not in students:
                    students[student_uri] = student_name
                    enroll_date = row.get('startDate')
                    date_str = str(enroll_date) if enroll_date else None
                    
                    self.graph.add_node(student_uri, type='student', label=student_name)
                    self.node_info[student_uri] = {
                        'type': 'student',
                        'name': student_name,
                        'startDate': date_str
                    }
                    if date_str:
                        self.time_data[student_uri] = self._parse_date(date_str)
        
        # Create temporal edges based on time ordering
        nodes_with_time = [(node, time) for node, time in self.time_data.items()]
        nodes_with_time.sort(key=lambda x: x[1])
        
        for i in range(len(nodes_with_time) - 1):
            node1, time1 = nodes_with_time[i]
            node2, time2 = nodes_with_time[i + 1]
            
            # Only connect if time difference is reasonable (same year or consecutive)
            if abs(time2 - time1) < 365:  # Within a year
                if not self.graph.has_edge(node1, node2):
                    self.graph.add_edge(node1, node2)
                    
        return self.graph
        
    def _parse_date(self, date_str):
        """Parse date string to numeric value"""
        try:
            # Try various date formats
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
            return (dt.year - 2000) * 365 + dt.timetuple().tm_yday
        except:
            try:
                # Try year only
                year = int(date_str[:4])
                return (year - 2000) * 365
            except:
                return 0
                
    def _parse_semester(self, semester_str):
        """Parse semester string to numeric value"""
        try:
            # Format: "Fall 2023" or "2023 Fall" or "2023-1"
            parts = semester_str.lower().split()
            if len(parts) >= 2:
                year = int(parts[-1]) if parts[-1].isdigit() else int(parts[0])
                season = parts[0] if not parts[0].isdigit() else parts[1]
                
                base = (year - 2000) * 365
                if 'fall' in season or 'autumn' in season:
                    return base + 273  # September
                elif 'spring' in season:
                    return base + 60   # March
                elif 'summer' in season:
                    return base + 182  # July
                elif 'winter' in season:
                    return base + 1    # January
            return base
        except:
            return 0
            
    def visualize(self, ax, filter_text=None, layout='spring', **kwargs):
        """Visualize temporal analysis"""
        ax.clear()
        
        # Build graph
        self.build_temporal_graph(filter_text)
        
        if len(self.graph.nodes) == 0:
            ax.text(0.5, 0.5, "No temporal data found",
                   ha='center', va='center', fontsize=14)
            ax.set_axis_off()
            return
            
        # Use time-based layout if possible
        if layout == 'spring' and self.time_data:
            # Create time-based positions
            pos = {}
            nodes_by_time = sorted(self.time_data.items(), key=lambda x: x[1])
            
            # Group nodes by time periods
            time_groups = defaultdict(list)
            for node, time_val in nodes_by_time:
                # Group into time periods (years)
                time_period = int(time_val / 365) if time_val > 0 else 0
                time_groups[time_period].append(node)
            
            # Position nodes in time-based layout
            # NetworkX expects (x, y) tuples, not just integers
            initial_pos = {}
            for period, nodes in sorted(time_groups.items()):
                # Distribute nodes horizontally within each time period
                num_nodes = len(nodes)
                for i, node in enumerate(nodes):
                    # x-coordinate: distribute evenly, y-coordinate: use time period
                    x = (i - num_nodes/2) * 0.5 if num_nodes > 1 else 0
                    y = period * 0.1  # Scale period to reasonable y-coordinate
                    initial_pos[node] = (x, y)
                    
            # Use spring layout with initial positions
            pos = nx.spring_layout(self.graph, seed=42, k=2, pos=initial_pos, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == 'shell':
            pos = nx.shell_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph, seed=42, k=2)
            
        # Prepare node colors and sizes
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'unknown')
            degree = self.graph.degree(node)
            
            # Color by type
            if node_type == 'event':
                color = '#FF9999'  # Light red
                size = kwargs.get('node_size', 500) + 300
            elif node_type == 'course':
                color = '#99CCFF'  # Light blue
                size = kwargs.get('node_size', 400) + degree * 30
            elif node_type == 'student':
                color = '#99FF99'  # Light green
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
        
        # Draw edges (temporal flow)
        edge_width = kwargs.get('edge_width', 1.5)
        nx.draw_networkx_edges(self.graph, pos, ax=ax,
                              arrowstyle='->',
                              arrowsize=12,
                              edge_color='gray',
                              width=edge_width,
                              alpha=0.5)
        
        # Draw labels - show all nodes
        font_size = kwargs.get('font_size', 9)
        labels = {}
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('type', 'unknown')
            label = self.graph.nodes[node].get('label', node.split('#')[-1])
            
            # Show all labels, truncate if too long
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
            'fig': ax.figure,
            'title': f"Temporal Analysis ({len(self.graph.nodes)} nodes)"
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
        title = f"Temporal Analysis ({len(self.graph.nodes)} nodes)"
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
            mpatches.Patch(color='#FF9999', label='Event'),
            mpatches.Patch(color='#99CCFF', label='Course'),
            mpatches.Patch(color='#99FF99', label='Student')
        ]
        
        ax.legend(handles=legend_patches, loc='upper right',
                 fontsize=8, framealpha=0.7)
                 
    def get_details(self):
        """Get details about current visualization"""
        if not self.node_info:
            return "No data available"
            
        details = f"TEMPORAL ANALYSIS VISUALIZATION\n"
        details += "="*40 + "\n\n"
        
        # Count by type
        type_counts = defaultdict(int)
        for info in self.node_info.values():
            type_counts[info['type']] += 1
            
        details += f"Total nodes: {len(self.graph.nodes)}\n"
        details += f"Total edges: {len(self.graph.edges)}\n\n"
        
        details += "NODE TYPE DISTRIBUTION:\n"
        details += "-"*30 + "\n"
        for type_name in ['event', 'course', 'student']:
            if type_name in type_counts:
                details += f"{type_name.capitalize()}s: {type_counts[type_name]}\n"
                
        # Time range
        if self.time_data:
            time_values = list(self.time_data.values())
            if time_values:
                min_time = min(time_values)
                max_time = max(time_values)
                min_year = 2000 + int(min_time / 365)
                max_year = 2000 + int(max_time / 365)
                details += f"\nTime Range: {min_year} - {max_year}\n"
                
        return details
        
    def get_node_info(self, node_uri):
        """Get detailed information about a specific node"""
        if node_uri in self.node_info:
            info = self.node_info[node_uri]
            details = f"Node: {info.get('name', node_uri.split('#')[-1])}\n"
            details += f"Type: {info['type'].capitalize()}\n"
            
            if 'date' in info and info['date']:
                details += f"Date: {info['date']}\n"
            if 'semester' in info and info['semester']:
                details += f"Semester: {info['semester']}\n"
            if 'startDate' in info and info['startDate']:
                details += f"Start Date: {info['startDate']}\n"
                
            return details
        return f"Node not found: {node_uri}"

