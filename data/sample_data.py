"""
Sample data generation for university ontology
"""

import random
from datetime import datetime, timedelta

class SampleDataLoader:
    """Load sample data into ontology"""
    
    def __init__(self, ontology):
        self.ontology = ontology
        
    def load_all(self):
        """Load all sample data"""
        self.load_university_structure()
        self.load_people()
        self.load_courses()
        self.load_relationships()
        
    def load_university_structure(self):
        """Load university structure"""
        # University
        self.ontology.add_instance("University", "UniversityOfExample", {
            "name": "University of Example",
            "address": "123 University Avenue, Example City",
            "description": "A leading research university"
        })
        
        # Faculties
        faculties = [
            ("ScienceFaculty", "Faculty of Science"),
            ("EngineeringFaculty", "Faculty of Engineering"),
            ("ArtsFaculty", "Faculty of Arts"),
            ("BusinessFaculty", "Faculty of Business")
        ]
        
        for fid, name in faculties:
            self.ontology.add_instance("Faculty", fid, {
                "name": name,
                "description": f"{name} at University of Example"
            })
            self.ontology.add_relationship("UniversityOfExample", "hasFaculty", fid)
            
        # Departments
        departments = [
            ("ComputerScience", "Department of Computer Science", "ScienceFaculty"),
            ("Mathematics", "Department of Mathematics", "ScienceFaculty"),
            ("Physics", "Department of Physics", "ScienceFaculty"),
            ("ElectricalEngineering", "Department of Electrical Engineering", "EngineeringFaculty"),
            ("MechanicalEngineering", "Department of Mechanical Engineering", "EngineeringFaculty"),
            ("English", "Department of English", "ArtsFaculty"),
            ("History", "Department of History", "ArtsFaculty"),
            ("BusinessAdmin", "Department of Business Administration", "BusinessFaculty")
        ]
        
        for did, name, faculty in departments:
            self.ontology.add_instance("Department", did, {
                "name": name,
                "description": f"{name} department"
            })
            self.ontology.add_relationship(faculty, "hasDepartment", did)
            
        # Programs
        programs = [
            ("CS_BSC", "Bachelor of Science in Computer Science", "ComputerScience", 4),
            ("CS_MSC", "Master of Science in Computer Science", "ComputerScience", 2),
            ("CS_PHD", "PhD in Computer Science", "ComputerScience", 5),
            ("MATH_BSC", "Bachelor of Science in Mathematics", "Mathematics", 4),
            ("EE_BSC", "Bachelor of Science in Electrical Engineering", "ElectricalEngineering", 4),
            ("ENG_BA", "Bachelor of Arts in English", "English", 4),
            ("MBA", "Master of Business Administration", "BusinessAdmin", 2)
        ]
        
        for pid, name, dept, duration in programs:
            self.ontology.add_instance("Program", pid, {
                "name": name,
                "code": pid,
                "duration": f"P{duration}Y",
                "description": f"Degree program in {name}",
                "level": "Undergraduate" if "B" in pid else "Graduate"
            })
            self.ontology.add_relationship(dept, "offersProgram", pid)
            
    def load_people(self):
        """Load sample people data"""
        # Professors
        professors = [
            ("ProfSmith", "John Smith", "jsmith@university.edu", "Professor", "ComputerScience", 85000),
            ("ProfJohnson", "Alice Johnson", "ajohnson@university.edu", "Associate Professor", "Mathematics", 75000),
            ("ProfBrown", "Robert Brown", "rbrown@university.edu", "Professor", "Physics", 90000),
            ("ProfDavis", "Emily Davis", "edavis@university.edu", "Assistant Professor", "ElectricalEngineering", 70000),
            ("ProfWilson", "Michael Wilson", "mwilson@university.edu", "Professor", "English", 80000),
            ("ProfTaylor", "Sarah Taylor", "staylor@university.edu", "Associate Professor", "BusinessAdmin", 95000)
        ]
        
        for pid, name, email, title, dept, salary in professors:
            self.ontology.add_instance("Professor", pid, {
                "name": name,
                "email": email,
                "title": title,
                "salary": salary,
                "id": f"P{pid}"
            })
            self.ontology.add_relationship(pid, "worksIn", dept)
            self.ontology.add_relationship(pid, "memberOf", dept)
            
        # Students
        students = []
        for i in range(1, 31):
            program = random.choice(["CS_BSC", "MATH_BSC", "EE_BSC", "ENG_BA"])
            gpa = round(random.uniform(2.5, 4.0), 2)
            
            student_id = f"Student{i:03d}"
            name = random.choice(["Alice", "Bob", "Charlie", "Diana", "Edward", 
                                 "Fiona", "George", "Helen", "Ian", "Julia"])
            surname = random.choice(["Johnson", "Williams", "Brown", "Jones", 
                                    "Garcia", "Miller", "Davis", "Rodriguez"])
            full_name = f"{name} {surname}"
            email = f"{name.lower()}.{surname.lower()}@student.edu"
            
            self.ontology.add_instance("Student", student_id, {
                "name": full_name,
                "email": email,
                "gpa": gpa,
                "id": student_id,
                "startDate": "2023-09-01"
            })
            self.ontology.add_relationship(student_id, "enrolledIn", program)
            
            students.append(student_id)
            
        # Staff
        staff = [
            ("Staff001", "Admin Officer", "admin@university.edu"),
            ("Staff002", "Library Manager", "library@university.edu"),
            ("Staff003", "Lab Technician", "labtech@university.edu")
        ]
        
        for sid, name, email in staff:
            self.ontology.add_instance("Staff", sid, {
                "name": name,
                "email": email,
                "title": name
            })
            
    def load_courses(self):
        """Load sample courses"""
        courses = [
            ("CS101", "Introduction to Programming", 3, "ComputerScience", "Fall"),
            ("CS201", "Data Structures", 4, "ComputerScience", "Spring"),
            ("CS301", "Algorithms", 4, "ComputerScience", "Fall"),
            ("CS401", "Machine Learning", 4, "ComputerScience", "Spring"),
            ("MATH101", "Calculus I", 3, "Mathematics", "Fall"),
            ("MATH201", "Linear Algebra", 3, "Mathematics", "Spring"),
            ("PHYS101", "Physics I", 4, "Physics", "Fall"),
            ("EE101", "Circuit Analysis", 4, "ElectricalEngineering", "Fall"),
            ("ENG101", "Composition I", 3, "English", "Fall"),
            ("BUS101", "Introduction to Business", 3, "BusinessAdmin", "Spring")
        ]
        
        for cid, name, credits, dept, semester in courses:
            self.ontology.add_instance("Course", cid, {
                "name": name,
                "code": cid,
                "credits": credits,
                "description": f"Course: {name}",
                "semester": semester,
                "capacity": random.randint(20, 50)
            })
            self.ontology.add_relationship("CS_BSC", "hasCourse", cid)
            
        # Add course prerequisites
        self.ontology.add_relationship("CS201", "hasPrerequisite", "CS101")
        self.ontology.add_relationship("CS301", "hasPrerequisite", "CS201")
        self.ontology.add_relationship("CS401", "hasPrerequisite", "CS301")
        
    def load_relationships(self):
        """Load sample relationships"""
        # Teaching assignments
        teaching = [
            ("ProfSmith", "CS101"),
            ("ProfSmith", "CS201"),
            ("ProfJohnson", "MATH101"),
            ("ProfJohnson", "MATH201"),
            ("ProfBrown", "PHYS101"),
            ("ProfDavis", "EE101"),
            ("ProfWilson", "ENG101"),
            ("ProfTaylor", "BUS101")
        ]
        
        for prof, course in teaching:
            self.ontology.add_relationship(prof, "teaches", course)
            
        # Student course enrollments
        students = [f"Student{i:03d}" for i in range(1, 31)]
        courses = ["CS101", "MATH101", "ENG101", "BUS101"]
        
        for student in students[:20]:  # First 20 students
            enrolled_courses = random.sample(courses, random.randint(1, 3))
            for course in enrolled_courses:
                self.ontology.add_relationship(student, "takesCourse", course)
                
        # Advisor relationships
        for i, student in enumerate(students[:10]):
            prof = ["ProfSmith", "ProfJohnson", "ProfBrown"][i % 3]
            self.ontology.add_relationship(student, "hasAdvisor", prof)
            self.ontology.add_relationship(student, "supervisedBy", prof)
            
        # Research projects
        research_projects = [
            ("AI_Research", "Artificial Intelligence Research", "ProfSmith"),
            ("Quantum_Research", "Quantum Computing Research", "ProfBrown"),
            ("Business_Analytics", "Business Analytics Research", "ProfTaylor")
        ]
        
        for rid, name, prof in research_projects:
            self.ontology.add_instance("Research", rid, {
                "name": name,
                "description": f"Research project on {name}",
                "startDate": "2023-01-01",
                "status": "Active"
            })
            self.ontology.add_relationship(prof, "partOfResearch", rid)
            
        # Publications
        publications = [
            ("Pub001", "Advances in Machine Learning", "ProfSmith", "AI_Research", 2023),
            ("Pub002", "Quantum Algorithms", "ProfBrown", "Quantum_Research", 2023),
            ("Pub003", "Business Intelligence", "ProfTaylor", "Business_Analytics", 2022)
        ]
        
        for pubid, title, author, research, year in publications:
            self.ontology.add_instance("Publication", pubid, {
                "name": title,
                "title": title,
                "year": year,
                "ISBN": f"ISBN-{random.randint(1000000000, 9999999999)}"
            })
            self.ontology.add_relationship(author, "published", pubid)
            
        # Buildings and rooms
        buildings = [
            ("ScienceBuilding", "Science Building", "123 Science Ave"),
            ("EngineeringBuilding", "Engineering Building", "456 Engineering St"),
            ("ArtsBuilding", "Arts Building", "789 Arts Blvd")
        ]
        
        for bid, name, address in buildings:
            self.ontology.add_instance("Building", bid, {
                "name": name,
                "address": address
            })
            
        rooms = [
            ("SB101", "Classroom 101", "ScienceBuilding"),
            ("SB201", "Lab 201", "ScienceBuilding"),
            ("EB301", "Computer Lab", "EngineeringBuilding"),
            ("AB101", "Lecture Hall", "ArtsBuilding")
        ]
        
        for rid, name, building in rooms:
            self.ontology.add_instance("Room", rid, {
                "name": name,
                "roomNumber": rid
            })
            self.ontology.add_relationship(rid, "locatedIn", building)
            
        # Labs
        labs = [
            ("CS_Lab1", "Computer Science Lab 1", "ComputerScience"),
            ("Physics_Lab", "Physics Laboratory", "Physics"),
            ("EE_Lab", "Electrical Engineering Lab", "ElectricalEngineering")
        ]
        
        for lid, name, dept in labs:
            self.ontology.add_instance("Lab", lid, {"name": name})
            self.ontology.add_relationship(dept, "hasLab", lid)
            
        # Events
        events = [
            ("CS_Seminar", "Computer Science Seminar", "2024-03-15", "ComputerScience"),
            ("Math_Conference", "Mathematics Conference", "2024-04-20", "Mathematics"),
            ("Business_Workshop", "Business Workshop", "2024-05-10", "BusinessAdmin")
        ]
        
        for eid, name, date, dept in events:
            self.ontology.add_instance("Event", eid, {
                "name": name,
                "description": f"{name} event",
                "startDate": date
            })
            self.ontology.add_relationship(eid, "organizedBy", dept)