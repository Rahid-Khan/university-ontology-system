"""
Import and export functionality
"""

import json
import csv
import os
from tkinter import filedialog, messagebox
from datetime import datetime

def export_ontology(ontology, format='turtle'):
    """Export ontology in specified format"""
    filename = filedialog.asksaveasfilename(
        defaultextension=get_extension(format),
        filetypes=get_filetypes(format),
        title=f"Export as {format.upper()}"
    )
    
    if filename:
        try:
            ontology.save_ontology(filename, format)
            messagebox.showinfo("Success", f"Ontology exported to {filename}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
            return False
    return False

def get_extension(format):
    """Get file extension for format"""
    extensions = {
        'turtle': '.ttl',
        'xml': '.rdf',
        'rdf': '.rdf',
        'json-ld': '.jsonld',
        'nt': '.nt',
        'n3': '.n3'
    }
    return extensions.get(format, '.ttl')

def get_filetypes(format):
    """Get file types for dialog"""
    filetypes = {
        'turtle': [("Turtle files", "*.ttl"), ("All files", "*.*")],
        'xml': [("RDF/XML files", "*.rdf"), ("XML files", "*.xml"), ("All files", "*.*")],
        'rdf': [("RDF files", "*.rdf"), ("All files", "*.*")],
        'json-ld': [("JSON-LD files", "*.jsonld"), ("JSON files", "*.json"), ("All files", "*.*")],
        'nt': [("N-Triples files", "*.nt"), ("All files", "*.*")],
        'n3': [("N3 files", "*.n3"), ("All files", "*.*")]
    }
    return filetypes.get(format, [("All files", "*.*")])

def export_instances_csv(ontology, class_filter=None):
    """Export instances to CSV"""
    filename = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Export Instances as CSV"
    )
    
    if not filename:
        return False
        
    try:
        # Build query based on filter
        if class_filter and class_filter != "All":
            class_uri = ontology.univ_ns[class_filter]
            query = f"""
            SELECT ?instance ?name ?id ?description
            WHERE {{
                ?instance rdf:type owl:NamedIndividual .
                ?instance rdf:type <{class_uri}> .
                OPTIONAL {{ ?instance univ:name ?name }}
                OPTIONAL {{ ?instance univ:id ?id }}
                OPTIONAL {{ ?instance univ:description ?description }}
            }}
            """
        else:
            query = """
            SELECT ?instance ?class ?name ?id ?description
            WHERE {
                ?instance rdf:type owl:NamedIndividual .
                ?instance rdf:type ?class .
                FILTER (?class != owl:NamedIndividual)
                OPTIONAL { ?instance univ:name ?name }
                OPTIONAL { ?instance univ:id ?id }
                OPTIONAL { ?instance univ:description ?description }
            }
            """
            
        results = ontology.query(query)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if class_filter and class_filter != "All":
                writer = csv.writer(f)
                writer.writerow(['Instance', 'Name', 'ID', 'Description'])
                
                for row in results:
                    instance = str(row['instance']).split('#')[-1]
                    name = str(row['name']) if row.get('name') else ""
                    id_ = str(row['id']) if row.get('id') else ""
                    description = str(row['description']) if row.get('description') else ""
                    writer.writerow([instance, name, id_, description])
            else:
                writer = csv.writer(f)
                writer.writerow(['Instance', 'Class', 'Name', 'ID', 'Description'])
                
                for row in results:
                    instance = str(row['instance']).split('#')[-1]
                    class_ = str(row['class']).split('#')[-1]
                    name = str(row['name']) if row.get('name') else ""
                    id_ = str(row['id']) if row.get('id') else ""
                    description = str(row['description']) if row.get('description') else ""
                    writer.writerow([instance, class_, name, id_, description])
                    
        messagebox.showinfo("Success", f"Instances exported to {filename}")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export: {str(e)}")
        return False
        
def export_relationships_csv(ontology):
    """Export relationships to CSV"""
    filename = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Export Relationships as CSV"
    )
    
    if not filename:
        return False
        
    try:
        query = """
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object .
            FILTER (isURI(?object))
            FILTER (STRSTARTS(STR(?predicate), STR(univ:)))
        }
        ORDER BY ?predicate ?subject
        """
        
        results = ontology.query(query)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Subject', 'Predicate', 'Object'])
            
            for row in results:
                subject = str(row['subject']).split('#')[-1]
                predicate = str(row['predicate']).split('#')[-1]
                object_ = str(row['object']).split('#')[-1]
                writer.writerow([subject, predicate, object_])
                
        messagebox.showinfo("Success", f"Relationships exported to {filename}")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export: {str(e)}")
        return False
        
def import_csv_instances(ontology, filename):
    """Import instances from CSV"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            imported = 0
            for row in reader:
                if 'Class' in row and 'Instance' in row:
                    class_name = row['Class']
                    instance_id = row['Instance']
                    
                    # Collect properties
                    properties = {}
                    if 'Name' in row and row['Name']:
                        properties['name'] = row['Name']
                    if 'ID' in row and row['ID']:
                        properties['id'] = row['ID']
                    if 'Description' in row and row['Description']:
                        properties['description'] = row['Description']
                        
                    # Add instance
                    ontology.add_instance(class_name, instance_id, properties)
                    imported += 1
                    
        return imported
        
    except Exception as e:
        raise Exception(f"Failed to import CSV: {str(e)}")
        
def import_csv_relationships(ontology, filename):
    """Import relationships from CSV"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            imported = 0
            for row in reader:
                if all(k in row for k in ['Subject', 'Predicate', 'Object']):
                    subject = row['Subject']
                    predicate = row['Predicate']
                    object_ = row['Object']
                    
                    # Add relationship
                    ontology.add_relationship(subject, predicate, object_)
                    imported += 1
                    
        return imported
        
    except Exception as e:
        raise Exception(f"Failed to import CSV: {str(e)}")
        
def create_backup(ontology, backup_dir='backups'):
    """Create backup of ontology"""
    import os
    from datetime import datetime
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(backup_dir, f'ontology_backup_{timestamp}.ttl')
    
    try:
        ontology.save_ontology(filename)
        return filename
    except Exception as e:
        raise Exception(f"Failed to create backup: {str(e)}")
        
def restore_backup(ontology, filename):
    """Restore ontology from backup"""
    try:
        ontology.load_ontology(filename)
        return True
    except Exception as e:
        raise Exception(f"Failed to restore backup: {str(e)}")