import sqlite3
import os
import random

# --- CONFIGURATION ---
CONFIG = {
    "universities": [(1, 'MIT'), (2, 'Stanford')],# (3, 'Harvard')],
    "teachers_per_uni": 4,
    "students_per_uni": 25,
    "courses_per_uni": 3,
    "db_path": 'data/university.db'
}

def setup_database(config):
    # Ensure the directory exists
    os.makedirs('data', exist_ok=True)
    db_path = config["db_path"]
    
    # Reset database if it exists
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

    # 2. Expanded Data Pools
    classes_list = ["AI", "Physics", "Maths", "Computer Science", "Biology", "History", "Ethics", "Astronomy"]
    first_names = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen",
    "Charles", "Lisa", "Daniel", "Nancy", "Matthew", "Sandra", "Anthony", "Betty", "Mark", "Ashley",
    "Donald", "Emily", "Steven", "Kimberly", "Andrew", "Donna", "Paul", "Emily", "Joshua", "Carol",
    "Kenneth", "Michelle", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa", "Timothy", "Deborah"
]

    last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

    # 3. Data Generation Logic
    cursor.executemany("INSERT INTO universities VALUES (?, ?)", config["universities"])

    # FIXED: Correctly unpacking (ID, Name)
    for u_id, u_name in config["universities"]:
        # 3.1 Teachers
        u_teacher_ids = []
        for _ in range(config["teachers_per_uni"]):
            cursor.execute(
                "INSERT INTO teachers (univ_id, first_name, last_name, department) VALUES (?, ?, ?, ?)",
                (u_id, random.choice(first_names), random.choice(last_names), random.choice(classes_list))
            )
            u_teacher_ids.append(cursor.lastrowid)

        # 3.2 Courses
        u_course_ids = []
        for i in range(config["courses_per_uni"]):
            cursor.execute(
                "INSERT INTO courses (univ_id, name) VALUES (?, ?)",
                (u_id, f"{random.choice(classes_list)} {101 + i}")
            )
            c_id = cursor.lastrowid
            u_course_ids.append(c_id)
            
            # 3.3 Assignments
            num_t = min(len(u_teacher_ids), random.randint(1, 2))
            for t_id in random.sample(u_teacher_ids, k=num_t):
                cursor.execute("INSERT INTO course_assignments VALUES (?, ?)", (c_id, t_id))

        # 3.4 Students
        for _ in range(config["students_per_uni"]):
            cursor.execute(
                "INSERT INTO students (univ_id, first_name, last_name) VALUES (?, ?, ?)",
                (u_id, random.choice(first_names), random.choice(last_names))
            )
            s_id = cursor.lastrowid

            # 3.5 Enrollments
            num_c = min(len(u_course_ids), 3)
            for c_id in random.sample(u_course_ids, k=num_c):
                cursor.execute("INSERT INTO enrollments VALUES (?, ?, ?)", (s_id, c_id, random.randint(65, 98)))

    conn.commit()
    conn.close()


    print(f"Success: Database created at {db_path}")
    print(f"Loaded {len(config['universities'])} universities with {config['students_per_uni']} students each.")

if __name__ == "__main__":
    setup_database(CONFIG)