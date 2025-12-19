"""
Utility helper functions
"""

import json
import os
from datetime import datetime
import hashlib

def format_date(date_string):
    """Format date string"""
    try:
        if isinstance(date_string, str):
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return date_string
    
def generate_id(prefix="", length=8):
    """Generate unique ID"""
    import random
    import string
    
    if prefix:
        prefix = prefix + "_"
        
    chars = string.ascii_letters + string.digits
    random_part = ''.join(random.choice(chars) for _ in range(length))
    
    return f"{prefix}{random_part}"
    
def calculate_hash(data):
    """Calculate hash of data"""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    elif not isinstance(data, str):
        data = str(data)
        
    return hashlib.md5(data.encode()).hexdigest()
    
def ensure_directory(directory):
    """Ensure directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def get_file_size(filename):
    """Get file size in human readable format"""
    size = os.path.getsize(filename)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
        
    return f"{size:.2f} TB"