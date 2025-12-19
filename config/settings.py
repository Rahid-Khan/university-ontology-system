"""
Application settings and configuration
"""

class Colors:
    """Color scheme for the application"""
    PRIMARY = '#3498db'
    SECONDARY = '#2ecc71'
    ACCENT = '#e74c3c'
    DARK = '#2c3e50'
    LIGHT = '#ecf0f1'
    SUCCESS = '#27ae60'
    WARNING = '#f39c12'
    DANGER = '#e74c3c'
    INFO = '#3498db'
    
    @classmethod
    def get_palette(cls, n):
        """Get color palette for n items"""
        import matplotlib.cm as cm
        cmap = cm.get_cmap('viridis', n)
        return [cmap(i) for i in range(n)]

class Fonts:
    """Font settings"""
    TITLE = ('Helvetica', 24, 'bold')
    SUBTITLE = ('Helvetica', 14)
    HEADING = ('Helvetica', 12, 'bold')
    BODY = ('Helvetica', 10)
    MONOSPACE = ('Courier', 10)

class Settings:
    """Application settings"""
    # Window settings
    WINDOW_TITLE = "University Management Ontology System"
    WINDOW_SIZE = "1400x800"
    MIN_WINDOW_SIZE = (1000, 600)
    
    # Visualization settings
    DEFAULT_VIZ_SIZE = (800, 600)
    NODE_SIZE = 500
    EDGE_WIDTH = 2
    FONT_SIZE = 10
    
    # Data settings
    ONTOLOGY_NAMESPACE = "http://www.semanticweb.org/khaled/ontologies/2024/university-management#"
    DEFAULT_SAMPLE_SIZE = 20
    
    # Query settings
    QUERY_TIMEOUT = 30  # seconds
    MAX_RESULTS = 1000