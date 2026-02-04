import sqlite3
import os
import random

def setup_database():
    os.makedirs('data', exist_ok=True)
    db_path = 'data/university.db'
    
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create Tables
    cursor.executescript('''
        CREATE TABLE universities (id INTEGER PRIMARY KEY, name TEXT);
        
        CREATE TABLE students (
            id INTEGER PRIMARY KEY, 
            univ_id INTEGER, 
            first_name TEXT, 
            last_name TEXT,
            FOREIGN KEY(univ_id) REFERENCES universities(id)
        );

        CREATE TABLE teachers (
            id INTEGER PRIMARY KEY, 
            univ_id INTEGER, 
            first_name TEXT, 
            last_name TEXT,
            department TEXT,
            FOREIGN KEY(univ_id) REFERENCES universities(id)
        );

        CREATE TABLE courses (
            id INTEGER PRIMARY KEY, 
            univ_id INTEGER, 
            name TEXT,
            FOREIGN KEY(univ_id) REFERENCES universities(id)
        );

        CREATE TABLE course_assignments (
            course_id INTEGER, 
            teacher_id INTEGER,
            FOREIGN KEY(course_id) REFERENCES courses(id),
            FOREIGN KEY(teacher_id) REFERENCES teachers(id)
        );

        CREATE TABLE enrollments (
            student_id INTEGER, 
            course_id INTEGER, 
            grade REAL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
    ''')

    # 2. Insert Sample Data

    # 2.1. Two Universities
    cursor.executemany("INSERT INTO universities VALUES (?, ?)", [(1, 'MIT'), (2, 'Stanford')])

    # 2.2 Teachers per Univ
    teachers = [
        # MIT (Univ 1)
        (1, 1, 'Albert', 'Einstein', 'Physics'),
        (2, 1, 'Marie', 'Curie', 'Chemistry'),
        (3, 1, 'Isaac', 'Newton', 'Maths'),
        (4, 1, 'Hypatia', 'of Alexandria', 'Astronomy'),
        
        # Stanford (Univ 2)
        (5, 2, 'Alan', 'Turing', 'Computer Science'),
        (6, 2, 'Ada', 'Lovelace', 'AI'),
        (7, 2, 'Charles', 'Darwin', 'Biology'),
        (8, 2, 'Nikola', 'Tesla', 'Electrical Engineering')
    ]
    cursor.executemany("INSERT INTO teachers VALUES (?, ?, ?, ?, ?)", teachers)

    # 2.3. Courses (Note: Course 103 and 203 are both "Maths 101")
    cursor.executemany("INSERT INTO courses VALUES (?, ?, ?)", [
        (101, 1, 'Physics 101'), (102, 1, 'Organic Chemistry'), (103, 1, 'Maths 101'), # MIT
        (201, 2, 'Intro to AI'), (202, 2, 'Data Structures'), (203, 2, 'Maths 101')    # Stanford
    ])

    # 2.4 Multi-Teacher Assignment (MIT Physics 101 co-taught by Einstein AND Curie)
    cursor.execute("INSERT INTO course_assignments VALUES (101, 1)")
    cursor.execute("INSERT INTO course_assignments VALUES (101, 2)")
    cursor.execute("INSERT INTO course_assignments VALUES (102, 2)") # Curie also teaches Chemistry
    cursor.execute("INSERT INTO course_assignments VALUES (103, 3)") # Newton - Calculus
    cursor.execute("INSERT INTO course_assignments VALUES (201, 6)") # Lovelace - AI
    cursor.execute("INSERT INTO course_assignments VALUES (202, 5)") # Turing - Data Structures
    cursor.execute("INSERT INTO course_assignments VALUES (203, 7)") # Darwin - Bio

    # 2.5 Students
    random.seed(42) # For reproducibility

    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", 
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                   "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
                   "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", 
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]

    all_students = []
    
    # MIT Students (IDs 1-30). If updating this, need to update Enroll MIT Students and Standford students below (around line 140)
    for i in range(1, 31):
        f = random.choice(first_names)
        l = random.choice(last_names)
        all_students.append((i, 1, f, l))
        
    # Stanford Students (IDs 31-60)
    for i in range(31, 61):
        f = random.choice(first_names)
        l = random.choice(last_names)
        all_students.append((i, 2, f, l))
    
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?)", all_students)



    # 2.6 Sample Enrollment
    all_enrollments = []
    mit_courses = [101, 102, 103]
    stan_courses = [201, 202, 203]

    def enroll_students(student_range, course_list):
        for s_id in student_range:
            # Randomly decide if a student takes 1, 2, or 3 courses
            num_courses = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            assigned_courses = random.sample(course_list, k=num_courses)
            
            for c_id in assigned_courses:
                # Assign a unique grade for diversification
                grade = random.randint(65, 98)
                all_enrollments.append((s_id, c_id, grade))

    # Enroll MIT Students
    enroll_students(range(1, 31), mit_courses)

    # Enroll Stanford Students
    enroll_students(range(31, 61), stan_courses)

    cursor.executemany("INSERT INTO enrollments VALUES (?, ?, ?)", all_enrollments)

    conn.commit()
    conn.close()
    print("Success: Data loaded.")

if __name__ == "__main__":
    setup_database()