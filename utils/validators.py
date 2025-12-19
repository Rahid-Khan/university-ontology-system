"""
Data validation utilities
"""

import re
from datetime import datetime

def validate_instance_id(instance_id):
    """Validate instance ID"""
    if not instance_id:
        return False, "Instance ID cannot be empty"
        
    if len(instance_id) > 100:
        return False, "Instance ID too long (max 100 characters)"
        
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', instance_id):
        return False, "Instance ID must start with letter or underscore and contain only letters, numbers, and underscores"
        
    return True, ""

def validate_class_name(class_name):
    """Validate class name"""
    if not class_name:
        return False, "Class name cannot be empty"
        
    if len(class_name) > 100:
        return False, "Class name too long (max 100 characters)"
        
    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
        return False, "Class name must start with capital letter and contain only letters and numbers"
        
    return True, ""

def validate_property_name(property_name):
    """Validate property name"""
    if not property_name:
        return False, "Property name cannot be empty"
        
    if len(property_name) > 100:
        return False, "Property name too long (max 100 characters)"
        
    if not re.match(r'^[a-z][a-zA-Z0-9]*$', property_name):
        return False, "Property name must start with lowercase letter and contain only letters and numbers"
        
    return True, ""

def validate_email(email):
    """Validate email address"""
    if not email:
        return True, ""  # Email is optional
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    else:
        return False, "Invalid email address"
        
def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return True, ""  # Phone is optional
        
    # Simple phone validation
    pattern = r'^[\d\s\-\+\(\)]{7,20}$'
    if re.match(pattern, phone):
        return True, ""
    else:
        return False, "Invalid phone number"
        
def validate_date(date_str):
    """Validate date string"""
    if not date_str:
        return True, ""  # Date is optional
        
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True, ""
    except ValueError:
        return False, "Invalid date format (use YYYY-MM-DD)"
        
def validate_number(value, min_val=None, max_val=None):
    """Validate number"""
    if not value:
        return True, ""  # Number is optional
        
    try:
        num = float(value)
        
        if min_val is not None and num < min_val:
            return False, f"Value must be at least {min_val}"
            
        if max_val is not None and num > max_val:
            return False, f"Value must be at most {max_val}"
            
        return True, ""
    except ValueError:
        return False, "Invalid number"
        
def validate_gpa(gpa):
    """Validate GPA"""
    return validate_number(gpa, 0.0, 4.0)

def validate_credits(credits):
    """Validate credit hours"""
    return validate_number(credits, 0, 999)

def validate_salary(salary):
    """Validate salary"""
    return validate_number(salary, 0, 1000000)

def validate_sparql_query(query):
    """Validate SPARQL query syntax (basic validation)"""
    if not query:
        return False, "Query cannot be empty"
        
    # Check for basic SPARQL keywords
    required_keywords = ['SELECT', 'WHERE']
    for keyword in required_keywords:
        if keyword not in query.upper():
            return False, f"Query must contain {keyword} keyword"
            
    # Check for balanced braces
    if query.count('{') != query.count('}'):
        return False, "Unbalanced braces in query"
        
    return True, ""