"""
Core ontology management classes
"""

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD
from rdflib.namespace import FOAF
import logging

logger = logging.getLogger(__name__)

class UniversityOntology:
    """University Management Ontology"""
    
    def __init__(self, namespace=None):
        self.graph = Graph()
        self.namespace = namespace or "http://www.semanticweb.org/khaled/ontologies/2024/university-management#"
        self.univ_ns = Namespace(self.namespace)
        self.init_ontology()
        
    def init_ontology(self):
        """Initialize the ontology structure"""
        # Bind namespaces
        self.graph.bind("univ", self.univ_ns)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("foaf", FOAF)
        self.graph.bind("xsd", XSD)
        
        # Define classes
        self._define_classes()
        # Define properties
        self._define_properties()
        
    def _define_classes(self):
        """Define ontology classes"""
        classes = [
            ("University", "An educational institution"),
            ("Faculty", "Academic division within university"),
            ("Department", "Academic department within faculty"),
            ("Program", "Academic degree program"),
            ("Course", "Academic course"),
            ("Person", "Person associated with university"),
            ("Student", "University student"),
            ("Professor", "University professor"),
            ("Staff", "University staff"),
            ("Researcher", "Research personnel"),
            ("Research", "Research project"),
            ("Publication", "Academic publication"),
            ("Event", "University event"),
            ("Resource", "University resource"),
            ("Building", "University building"),
            ("Room", "Room in a building"),
            ("Lab", "Laboratory facility"),
            ("Library", "University library"),
            ("AdministrativeUnit", "Administrative unit"),
            ("Thesis", "Student thesis or dissertation"),
            ("Grant", "Research grant"),
            ("Conference", "Academic conference")
        ]
        
        for class_name, comment in classes:
            class_uri = self.univ_ns[class_name]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.comment, Literal(comment)))
            
    def _define_properties(self):
        """Define object and data properties"""
        # Object properties
        obj_properties = [
            ("hasFaculty", "University", "Faculty", "University has faculties"),
            ("hasDepartment", "Faculty", "Department", "Faculty has departments"),
            ("offersProgram", "Department", "Program", "Department offers programs"),
            ("hasCourse", "Program", "Course", "Program has courses"),
            ("teaches", "Professor", "Course", "Professor teaches course"),
            ("enrolledIn", "Student", "Program", "Student enrolled in program"),
            ("takesCourse", "Student", "Course", "Student takes course"),
            ("worksIn", "Professor", "Department", "Professor works in department"),
            ("manages", "Staff", "AdministrativeUnit", "Staff manages unit"),
            ("hasAdvisor", "Student", "Professor", "Student has advisor"),
            ("published", "Professor", "Publication", "Professor published work"),
            ("partOfResearch", "Researcher", "Research", "Researcher part of research"),
            ("locatedIn", "Room", "Building", "Room located in building"),
            ("hasLab", "Department", "Lab", "Department has lab"),
            ("hasResource", "Course", "Resource", "Course has resources"),
            ("organizedBy", "Event", "Department", "Event organized by department"),
            ("attends", "Student", "Event", "Student attends event"),
            ("hasPrerequisite", "Course", "Course", "Course has prerequisite"),
            ("supervisedBy", "Student", "Professor", "Student supervised by professor"),
            ("memberOf", "Person", "Department", "Person member of department"),
            ("fundedBy", "Research", "Grant", "Research funded by grant"),
            ("presentedAt", "Publication", "Conference", "Publication presented at conference")
        ]
        
        for prop, domain, range_, comment in obj_properties:
            prop_uri = self.univ_ns[prop]
            self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.graph.add((prop_uri, RDFS.domain, self.univ_ns[domain]))
            self.graph.add((prop_uri, RDFS.range, self.univ_ns[range_]))
            self.graph.add((prop_uri, RDFS.comment, Literal(comment)))
            
        # Data properties
        data_props = [
            ("name", XSD.string, "Name of entity"),
            ("id", XSD.string, "ID of entity"),
            ("email", XSD.string, "Email address"),
            ("phone", XSD.string, "Phone number"),
            ("startDate", XSD.date, "Start date"),
            ("endDate", XSD.date, "End date"),
            ("credits", XSD.integer, "Credit hours"),
            ("capacity", XSD.integer, "Capacity"),
            ("gpa", XSD.float, "Grade point average"),
            ("salary", XSD.float, "Salary amount"),
            ("budget", XSD.float, "Budget amount"),
            ("title", XSD.string, "Title/Position"),
            ("code", XSD.string, "Course/Program code"),
            ("description", XSD.string, "Description"),
            ("address", XSD.string, "Address"),
            ("roomNumber", XSD.string, "Room number"),
            ("ISBN", XSD.string, "ISBN for publication"),
            ("year", XSD.integer, "Year"),
            ("duration", XSD.duration, "Duration"),
            ("status", XSD.string, "Status"),
            ("level", XSD.string, "Academic level"),
            ("semester", XSD.string, "Semester"),
            ("grade", XSD.string, "Grade received")
        ]
        
        for prop, dtype, comment in data_props:
            prop_uri = self.univ_ns[prop]
            self.graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.graph.add((prop_uri, RDFS.range, dtype))
            self.graph.add((prop_uri, RDFS.comment, Literal(comment)))
            
    def add_instance(self, class_name, instance_id, properties=None):
        """Add an instance to the ontology"""
        try:
            instance_uri = self.univ_ns[instance_id]
            class_uri = self.univ_ns[class_name]
            
            # Check if instance already exists
            if (instance_uri, RDF.type, OWL.NamedIndividual) in self.graph:
                raise ValueError(f"Instance '{instance_id}' already exists")
                
            self.graph.add((instance_uri, RDF.type, class_uri))
            self.graph.add((instance_uri, RDF.type, OWL.NamedIndividual))
            
            if properties:
                for prop, value in properties.items():
                    prop_uri = self.univ_ns[prop]
                    if isinstance(value, str) and value.startswith("http"):
                        self.graph.add((instance_uri, prop_uri, URIRef(value)))
                    else:
                        self.graph.add((instance_uri, prop_uri, Literal(value)))
                        
            logger.info(f"Added instance '{instance_id}' of class '{class_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add instance: {e}")
            raise
            
    def add_relationship(self, subject_id, predicate, object_id):
        """Add relationship between instances"""
        try:
            subj_uri = self.univ_ns[subject_id]
            obj_uri = self.univ_ns[object_id]
            pred_uri = self.univ_ns[predicate]
            
            # Check if relationship already exists
            if (subj_uri, pred_uri, obj_uri) in self.graph:
                logger.warning(f"Relationship already exists: {subject_id} {predicate} {object_id}")
                return False
                
            self.graph.add((subj_uri, pred_uri, obj_uri))
            logger.info(f"Added relationship: {subject_id} {predicate} {object_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            raise
            
    def remove_instance(self, instance_id):
        """Remove an instance and all its relationships"""
        try:
            instance_uri = self.univ_ns[instance_id]
            
            # Remove all triples where instance is subject or object
            triples_to_remove = list(self.graph.triples((instance_uri, None, None))) + \
                               list(self.graph.triples((None, None, instance_uri)))
            
            for triple in triples_to_remove:
                self.graph.remove(triple)
                
            logger.info(f"Removed instance '{instance_id}'")
            return len(triples_to_remove)
            
        except Exception as e:
            logger.error(f"Failed to remove instance: {e}")
            raise
            
    def query(self, sparql_query, limit=None):
        """Execute SPARQL query"""
        try:
            if limit:
                sparql_query = f"{sparql_query.rstrip(';')} LIMIT {limit}"
            return self.graph.query(sparql_query)
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            raise
            
    def get_statistics(self):
        """Get ontology statistics"""
        stats = {}
        
        # Count classes
        classes_query = "SELECT (COUNT(DISTINCT ?class) as ?count) WHERE { ?class rdf:type owl:Class }"
        stats['classes'] = int(list(self.query(classes_query))[0]['count'])
        
        # Count instances
        instances_query = "SELECT (COUNT(DISTINCT ?instance) as ?count) WHERE { ?instance rdf:type owl:NamedIndividual }"
        stats['instances'] = int(list(self.query(instances_query))[0]['count'])
        
        # Count object properties
        obj_props_query = "SELECT (COUNT(DISTINCT ?prop) as ?count) WHERE { ?prop rdf:type owl:ObjectProperty }"
        stats['object_properties'] = int(list(self.query(obj_props_query))[0]['count'])
        
        # Count data properties
        data_props_query = "SELECT (COUNT(DISTINCT ?prop) as ?count) WHERE { ?prop rdf:type owl:DatatypeProperty }"
        stats['data_properties'] = int(list(self.query(data_props_query))[0]['count'])
        
        # Count relationships
        rel_query = """
        SELECT (COUNT(*) as ?count) WHERE {
            ?s ?p ?o .
            FILTER (isURI(?o))
            FILTER (STRSTARTS(STR(?p), STR(univ:)))
        }
        """
        stats['relationships'] = int(list(self.query(rel_query))[0]['count'])
        
        return stats
        
    def get_class_hierarchy(self):
        """Get class hierarchy as nested dictionary"""
        hierarchy = {}
        
        # Get all classes
        classes_query = """
        SELECT ?class ?label ?comment
        WHERE {
            ?class rdf:type owl:Class .
            OPTIONAL { ?class rdfs:label ?label }
            OPTIONAL { ?class rdfs:comment ?comment }
        }
        """
        
        for row in self.query(classes_query):
            class_uri = str(row['class'])
            class_name = class_uri.split('#')[-1]
            label = str(row['label']) if row['label'] else class_name
            comment = str(row['comment']) if row['comment'] else ""
            
            # Get subclass relationships
            sub_query = f"""
            SELECT ?subclass WHERE {{
                ?subclass rdfs:subClassOf <{class_uri}> .
            }}
            """
            
            subclasses = []
            for sub_row in self.query(sub_query):
                sub_uri = str(sub_row['subclass'])
                sub_name = sub_uri.split('#')[-1]
                subclasses.append(sub_name)
                
            hierarchy[class_name] = {
                'label': label,
                'comment': comment,
                'subclasses': subclasses,
                'instance_count': self._count_instances(class_uri)
            }
            
        return hierarchy
        
    def _count_instances(self, class_uri):
        """Count instances of a class"""
        query = f"""
        SELECT (COUNT(?instance) as ?count)
        WHERE {{
            ?instance rdf:type <{class_uri}> .
            ?instance rdf:type owl:NamedIndividual .
        }}
        """
        
        result = list(self.query(query))
        return int(result[0]['count']) if result else 0
        
    def save_ontology(self, filename, format='turtle'):
        """Save ontology to file"""
        self.graph.serialize(destination=filename, format=format)
        logger.info(f"Ontology saved to {filename}")
        
    def load_ontology(self, filename, format=None):
        """Load ontology from file"""
        self.graph.parse(filename, format=format)
        logger.info(f"Ontology loaded from {filename}")
        
    def clear(self):
        """Clear all data from ontology"""
        self.graph.remove((None, None, None))
        self.init_ontology()