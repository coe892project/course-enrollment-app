import os
import logging
from typing import List, Optional

import pymongo
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from urllib.parse import quote_plus

logger = logging.getLogger('uvicorn.error')

load_dotenv()
conString = os.getenv("MONGODB_URL")
conString = conString.replace("<db_username>", quote_plus(os.getenv("MONGODB_USER")))
conString = conString.replace("<db_password>", quote_plus(os.getenv("MONGODB_PASSWORD")))

client = pymongo.MongoClient(conString)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    logger.info(f"MongoDB is connected!")
except Exception as e:
    logger.error(e)
    exit(1)

db = client["CourseEnrollment"]

app = FastAPI()

# Pydantic models for request bodies
class Course(BaseModel):
    course_code: str
    course_name: str
    section: str
    semester: str
    prerequisites: List[str] = []
    corequisites: List[str] = []
    available_seats: int
    instructor: str
    course_time: str

class Student(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    status: str
    program_id: str
    enrolled_courses: List[str] = []
    completed_courses: List[str] = []

class CourseOffering(BaseModel):
    offering_id: str
    course_code: str
    course_name: str
    instructor: str
    semester: str
    year: int
    available_seats: int

class Location(BaseModel):
    room_id: str
    room_name: str
    available_seats: int
    available_times: List[str]

class Instructor(BaseModel):
    instructor_id: str
    first_name: str
    last_name: str
    department_id: str
    title: str
    courses_teachable: List[str]

class Program(BaseModel):
    program_id: str
    program_name: str
    degree_type: str
    department_id: str

class Department(BaseModel):
    department_id: str
    department_name: str
    faculty_id: str

class Faculty(BaseModel):
    faculty_id: str
    faculty_name: str

class Enrollment(BaseModel):
    enrollment_id: str
    student_id: str
    offering_id: str
    enrollment_date: str
    grade: Optional[str] = None

class Prerequisite(BaseModel):
    course_id: str
    prerequisite_course_id: str

# Courses endpoints
@app.get("/courses/", response_model=List[Course])
def get_courses():
    return list(db.courses.find())

@app.post("/courses/", response_model=Course)
def create_course(course: Course):
    db.courses.insert_one(course.model_dump())
    return course

@app.put("/courses/{course_code}", response_model=Course)
def update_course(course_code: str, course: Course):
    db.courses.update_one({"course_code": course_code}, {"$set": course.model_dump()})
    return course

@app.delete("/courses/{course_code}")
def delete_course(course_code: str):
    db.courses.delete_one({"course_code": course_code})
    return {"message": "Course deleted"}

# Students endpoints
@app.get("/students/", response_model=List[Student])
def get_students():
    return list(db.students.find())

@app.post("/students/", response_model=Student)
def create_student(student: Student):
    db.students.insert_one(student.model_dump())
    return student

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: str, student: Student):
    db.students.update_one({"student_id": student_id}, {"$set": student.model_dump()})
    return student

@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    db.students.delete_one({"student_id": student_id})
    return {"message": "Student deleted"}

# Course Offerings endpoints
@app.get("/course_offerings/", response_model=List[CourseOffering])
def get_course_offerings():
    return list(db.course_offerings.find())

@app.post("/course_offerings/", response_model=CourseOffering)
def create_course_offering(course_offering: CourseOffering):
    db.course_offerings.insert_one(course_offering.model_dump())
    return course_offering

@app.put("/course_offerings/{offering_id}", response_model=CourseOffering)
def update_course_offering(offering_id: str, course_offering: CourseOffering):
    db.course_offerings.update_one({"offering_id": offering_id}, {"$set": course_offering.model_dump()})
    return course_offering

@app.delete("/course_offerings/{offering_id}")
def delete_course_offering(offering_id: str):
    db.course_offerings.delete_one({"offering_id": offering_id})
    return {"message": "Course Offering deleted"}

# Location endpoints
@app.get("/locations/", response_model=List[Location])
def get_locations():
    return list(db.locations.find())

@app.post("/locations/", response_model=Location)
def create_location(location: Location):
    db.locations.insert_one(location.model_dump())
    return location

@app.put("/locations/{room_id}", response_model=Location)
def update_location(room_id: str, location: Location):
    db.locations.update_one({"room_id": room_id}, {"$set": location.model_dump()})
    return location

@app.delete("/locations/{room_id}")
def delete_location(room_id: str):
    db.locations.delete_one({"room_id": room_id})
    return {"message": "Location deleted"}

# Instructors endpoints
@app.get("/instructors/", response_model=List[Instructor])
def get_instructors():
    return list(db.instructors.find())

@app.post("/instructors/", response_model=Instructor)
def create_instructor(instructor: Instructor):
    db.instructors.insert_one(instructor.model_dump())
    return instructor

@app.put("/instructors/{instructor_id}", response_model=Instructor)
def update_instructor(instructor_id: str, instructor: Instructor):
    db.instructors.update_one({"instructor_id": instructor_id}, {"$set": instructor.model_dump()})
    return instructor

@app.delete("/instructors/{instructor_id}")
def delete_instructor(instructor_id: str):
    db.instructors.delete_one({"instructor_id": instructor_id})
    return {"message": "Instructor deleted"}

# Programs endpoints
@app.get("/programs/", response_model=List[Program])
def get_programs():
    return list(db.programs.find())

@app.post("/programs/", response_model=Program)
def create_program(program: Program):
    db.programs.insert_one(program.model_dump())
    return program

@app.put("/programs/{program_id}", response_model=Program)
def update_program(program_id: str, program: Program):
    db.programs.update_one({"program_id": program_id}, {"$set": program.model_dump()})
    return program

@app.delete("/programs/{program_id}")
def delete_program(program_id: str):
    db.programs.delete_one({"program_id": program_id})
    return {"message": "Program deleted"}

# Departments endpoints
@app.get("/departments/", response_model=List[Department])
def get_departments():
    return list(db.departments.find())

@app.post("/departments/", response_model=Department)
def create_department(department: Department):
    db.departments.insert_one(department.model_dump())
    return department

@app.put("/departments/{department_id}", response_model=Department)
def update_department(department_id: str, department: Department):
    db.departments.update_one({"department_id": department_id}, {"$set": department.model_dump()})
    return department

@app.delete("/departments/{department_id}")
def delete_department(department_id: str):
    db.departments.delete_one({"department_id": department_id})
    return {"message": "Department deleted"}

# Faculty endpoints
@app.get("/faculties/", response_model=List[Faculty])
def get_faculties():
    return list(db.faculties.find())

@app.post("/faculties/", response_model=Faculty)
def create_faculty(faculty: Faculty):
    db.faculties.insert_one(faculty.model_dump())
    return faculty

@app.put("/faculties/{faculty_id}", response_model=Faculty)
def update_faculty(faculty_id: str, faculty: Faculty):
    db.faculties.update_one({"faculty_id": faculty_id}, {"$set": faculty.model_dump()})
    return faculty

@app.delete("/faculties/{faculty_id}")
def delete_faculty(faculty_id: str):
    db.faculties.delete_one({"faculty_id": faculty_id})
    return {"message": "Faculty deleted"}

# Enrollments endpoints
@app.get("/enrollments/", response_model=List[Enrollment])
def get_enrollments():
    return list(db.enrollments.find())

@app.post("/enrollments/", response_model=Enrollment)
def create_enrollment(enrollment: Enrollment):
    db.enrollments.insert_one(enrollment.model_dump())
    return enrollment

@app.put("/enrollments/{enrollment_id}", response_model=Enrollment)
def update_enrollment(enrollment_id: str, enrollment: Enrollment):
    db.enrollments.update_one({"enrollment_id": enrollment_id}, {"$set": enrollment.model_dump()})
    return enrollment

@app.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: str):
    db.enrollments.delete_one({"enrollment_id": enrollment_id})
    return {"message": "Enrollment deleted"}

# Prerequisites endpoints
@app.get("/prerequisites/", response_model=List[Prerequisite])
def get_prerequisites():
    return list(db.prerequisites.find())

@app.post("/prerequisites/", response_model=Prerequisite)
def create_prerequisite(prerequisite: Prerequisite):
    db.prerequisites.insert_one(prerequisite.model_dump())
    return prerequisite

@app.put("/prerequisites/{course_id}", response_model=Prerequisite)
def update_prerequisite(course_id: str, prerequisite: Prerequisite):
    db.prerequisites.update_one({"course_id": course_id}, {"$set": prerequisite.model_dump()})
    return prerequisite

@app.delete("/prerequisites/{course_id}")
def delete_prerequisite(course_id: str):
    db.prerequisites.delete_one({"course_id": course_id})
    return {"message": "Prerequisite deleted"}

# NOTE: Use fastapi dev main.py
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
