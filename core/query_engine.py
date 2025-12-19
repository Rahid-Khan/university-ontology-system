"""
Advanced SPARQL query engine with caching and optimization
"""

import re
import time
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class QueryEngine:
    """Enhanced SPARQL query engine"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        self.query_cache = {}
        self.query_history = []  # Store query history
        
    def execute_query(self, sparql_query, limit=100, timeout=30):
        """Execute SPARQL query with timeout and limit"""
        start_time = time.time()
        
        try:
            # Apply limit if not already present
            if 'LIMIT' not in sparql_query.upper():
                sparql_query = f"{sparql_query.rstrip(';')} LIMIT {limit}"
                
            # Check cache
            cache_key = self._get_cache_key(sparql_query)
            if cache_key in self.query_cache:
                logger.info("Query result retrieved from cache")
                return self.query_cache[cache_key]
                
            # Execute query
            result = self.ontology.query(sparql_query)
            
            # Cache result
            self.query_cache[cache_key] = result
            
            # Add to history
            result_list = list(result)
            self.query_history.append({
                'query': sparql_query,
                'timestamp': time.time(),
                'result_count': len(result_list),
                'execution_time': time.time() - start_time
            })
            
            # Keep only last 100 queries
            if len(self.query_history) > 100:
                self.query_history = self.query_history[-100:]
            
            elapsed = time.time() - start_time
            logger.info(f"Query executed in {elapsed:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
            
    def _get_cache_key(self, sparql_query):
        """Generate cache key for query"""
        # Normalize query by removing whitespace and comments
        normalized = re.sub(r'\s+', ' ', sparql_query.strip())
        normalized = re.sub(r'#.*$', '', normalized, flags=re.MULTILINE)
        return hash(normalized)
        
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        
    def get_common_queries(self):
        """Get common SPARQL queries for the university ontology"""
        return {
            'all_students': """
                SELECT ?student ?name ?email ?gpa ?program
                WHERE {
                    ?student rdf:type univ:Student .
                    ?student univ:name ?name .
                    OPTIONAL { ?student univ:email ?email }
                    OPTIONAL { ?student univ:gpa ?gpa }
                    OPTIONAL { ?student univ:enrolledIn ?program }
                }
                ORDER BY ?name
                LIMIT 50
            """,
            
            'all_professors': """
                SELECT ?prof ?name ?email ?department ?title
                WHERE {
                    ?prof rdf:type univ:Professor .
                    ?prof univ:name ?name .
                    OPTIONAL { ?prof univ:email ?email }
                    OPTIONAL { ?prof univ:worksIn ?dept . ?dept univ:name ?department }
                    OPTIONAL { ?prof univ:title ?title }
                }
                ORDER BY ?name
                LIMIT 50
            """,
            
            'course_prerequisites': """
                SELECT ?course ?name ?prereq ?prereqName
                WHERE {
                    ?course rdf:type univ:Course .
                    ?course univ:name ?name .
                    OPTIONAL {
                        ?course univ:hasPrerequisite ?prereq .
                        ?prereq univ:name ?prereqName
                    }
                }
                ORDER BY ?course
                LIMIT 50
            """,
            
            'department_structure': """
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
                LIMIT 100
            """,
            
            'student_enrollments': """
                SELECT ?student ?studentName ?course ?courseName ?prof ?profName
                WHERE {
                    ?student rdf:type univ:Student .
                    ?student univ:name ?studentName .
                    ?student univ:takesCourse ?course .
                    ?course univ:name ?courseName .
                    OPTIONAL {
                        ?prof univ:teaches ?course .
                        ?prof univ:name ?profName
                    }
                }
                ORDER BY ?studentName
                LIMIT 50
            """
        }
    
    def get_query_history(self, limit=50):
        """Get query history"""
        return self.query_history[-limit:] if limit else self.query_history
    
    def clear_history(self):
        """Clear query history"""
        self.query_history.clear()