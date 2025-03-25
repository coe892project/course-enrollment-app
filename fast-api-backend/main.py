from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Annotated, List, Optional
from pydantic import BaseModel
from http.client import HTTPException
import logging
import os
from urllib.parse import quote_plus
import pymongo
from dotenv import load_dotenv
from collections import defaultdict

# Setup logging and MongoDB connection
logger = logging.getLogger('uvicorn.error')
load_dotenv()

proj_name = os.getenv("MONGODB_APP_NAME") if os.getenv("MONGODB_APP_NAME") is not None else "COE892Project"
logger.info(f"Project name: {proj_name}")
conString = f"mongodb+srv://" \
            f'{quote_plus(os.getenv("MONGODB_USER"))}:{quote_plus(os.getenv("MONGODB_PASSWORD"))}' \
            f'@{os.getenv("MONGODB_CLUSTER_URL")}/?retryWrites=true&w=majority' \
            f'&appName={proj_name}'

client = pymongo.MongoClient(conString)
try:
    client.admin.command('ping')
    logger.info("MongoDB is connected!")
except Exception as e:
    logger.error(e)
    exit(1)

db = client.CourseEnrollment
app = FastAPI()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class Course(BaseModel):
    course_code: str
    course_name: str
    section: str
    semester: str
    prerequisites: List[str] = []
    corequisites: List[str] = []
    available_seats: int
    instructor: str
    course_time: List[str] = []

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

class Accounts(BaseModel):
    username: str
    password: str

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = db.accounts.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.accounts.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user

# Public endpoints
@app.post("/accounts/", response_model=Accounts)
def create_account(account: Accounts):
    if db.accounts.find_one({"username": account.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = get_password_hash(account.password)
    account_dict = account.model_dump()
    account_dict["password"] = hashed_password
    db.accounts.insert_one(account_dict)
    return account

@app.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoints
@app.get("/accounts/", response_model=List[Accounts])
async def get_accounts(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.accounts.find())

@app.get("/accounts/{username}", response_model=Accounts)
async def get_account(username: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    account = db.accounts.find_one({"username": username})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.put("/accounts/{username}", response_model=Accounts)
async def update_account(username: str, account: Accounts, current_user: Annotated[Accounts, Depends(get_current_user)]):
    existing = db.accounts.find_one({"username": username})
    if not existing:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.username != username and db.accounts.find_one({"username": account.username}):
        raise HTTPException(status_code=400, detail="New username already exists")
    db.accounts.update_one({"username": username}, {"$set": account.model_dump()})
    return account

@app.delete("/accounts/{username}")
async def delete_account(username: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    result = db.accounts.delete_one({"username": username})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}

# Courses endpoints
@app.get("/courses/", response_model=List[Course])
async def get_courses(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.courses.find())

@app.post("/courses/", response_model=Course)
async def create_course(course: Course, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.courses.insert_one(course.model_dump())
    return course

@app.put("/courses/{course_code}", response_model=Course)
async def update_course(course_code: str, course: Course, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.courses.update_one({"course_code": course_code}, {"$set": course.model_dump()})
    return course

@app.delete("/courses/{course_code}")
async def delete_course(course_code: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.courses.delete_one({"course_code": course_code})
    return {"message": "Course deleted"}

# Students endpoints
@app.get("/students/", response_model=List[Student])
async def get_students(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.students.find())

@app.post("/students/", response_model=Student)
async def create_student(student: Student, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.students.insert_one(student.model_dump())
    return student

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, student: Student, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.students.update_one({"student_id": student_id}, {"$set": student.model_dump()})
    return student

@app.delete("/students/{student_id}")
async def delete_student(student_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.students.delete_one({"student_id": student_id})
    return {"message": "Student deleted"}

# Course Offerings endpoints
@app.get("/course_offerings/", response_model=List[CourseOffering])
async def get_course_offerings(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.course_offerings.find())

@app.post("/course_offerings/", response_model=CourseOffering)
async def create_course_offering(course_offering: CourseOffering, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.course_offerings.insert_one(course_offering.model_dump())
    return course_offering

@app.put("/course_offerings/{offering_id}", response_model=CourseOffering)
async def update_course_offering(offering_id: str, course_offering: CourseOffering, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.course_offerings.update_one({"offering_id": offering_id}, {"$set": course_offering.model_dump()})
    return course_offering

@app.delete("/course_offerings/{offering_id}")
async def delete_course_offering(offering_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.course_offerings.delete_one({"offering_id": offering_id})
    return {"message": "Course Offering deleted"}

# Location endpoints
@app.get("/locations/", response_model=List[Location])
async def get_locations(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.locations.find())

@app.post("/locations/", response_model=Location)
async def create_location(location: Location, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.locations.insert_one(location.model_dump())
    return location

@app.put("/locations/{room_id}", response_model=Location)
async def update_location(room_id: str, location: Location, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.locations.update_one({"room_id": room_id}, {"$set": location.model_dump()})
    return location

@app.delete("/locations/{room_id}")
async def delete_location(room_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.locations.delete_one({"room_id": room_id})
    return {"message": "Location deleted"}

# Instructors endpoints
@app.get("/instructors/", response_model=List[Instructor])
async def get_instructors(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.instructors.find())

@app.post("/instructors/", response_model=Instructor)
async def create_instructor(instructor: Instructor, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.instructors.insert_one(instructor.model_dump())
    return instructor

@app.put("/instructors/{instructor_id}", response_model=Instructor)
async def update_instructor(instructor_id: str, instructor: Instructor, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.instructors.update_one({"instructor_id": instructor_id}, {"$set": instructor.model_dump()})
    return instructor

@app.delete("/instructors/{instructor_id}")
async def delete_instructor(instructor_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.instructors.delete_one({"instructor_id": instructor_id})
    return {"message": "Instructor deleted"}

# Programs endpoints
@app.get("/programs/", response_model=List[Program])
async def get_programs(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.programs.find())

@app.post("/programs/", response_model=Program)
async def create_program(program: Program, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.programs.insert_one(program.model_dump())
    return program

@app.put("/programs/{program_id}", response_model=Program)
async def update_program(program_id: str, program: Program, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.programs.update_one({"program_id": program_id}, {"$set": program.model_dump()})
    return program

@app.delete("/programs/{program_id}")
async def delete_program(program_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.programs.delete_one({"program_id": program_id})
    return {"message": "Program deleted"}

# Departments endpoints
@app.get("/departments/", response_model=List[Department])
async def get_departments(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.departments.find())

@app.post("/departments/", response_model=Department)
async def create_department(department: Department, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.departments.insert_one(department.model_dump())
    return department

@app.put("/departments/{department_id}", response_model=Department)
async def update_department(department_id: str, department: Department, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.departments.update_one({"department_id": department_id}, {"$set": department.model_dump()})
    return department

@app.delete("/departments/{department_id}")
async def delete_department(department_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.departments.delete_one({"department_id": department_id})
    return {"message": "Department deleted"}

# Faculty endpoints
@app.get("/faculties/", response_model=List[Faculty])
async def get_faculties(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.faculties.find())

@app.post("/faculties/", response_model=Faculty)
async def create_faculty(faculty: Faculty, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.faculties.insert_one(faculty.model_dump())
    return faculty

@app.put("/faculties/{faculty_id}", response_model=Faculty)
async def update_faculty(faculty_id: str, faculty: Faculty, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.faculties.update_one({"faculty_id": faculty_id}, {"$set": faculty.model_dump()})
    return faculty

@app.delete("/faculties/{faculty_id}")
async def delete_faculty(faculty_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.faculties.delete_one({"faculty_id": faculty_id})
    return {"message": "Faculty deleted"}

# Enrollments endpoints
@app.get("/enrollments/", response_model=List[Enrollment])
async def get_enrollments(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.enrollments.find())

@app.post("/enrollments/", response_model=Enrollment)
async def create_enrollment(enrollment: Enrollment, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.enrollments.insert_one(enrollment.model_dump())
    return enrollment

@app.put("/enrollments/{enrollment_id}", response_model=Enrollment)
async def update_enrollment(enrollment_id: str, enrollment: Enrollment, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.enrollments.update_one({"enrollment_id": enrollment_id}, {"$set": enrollment.model_dump()})
    return enrollment

@app.delete("/enrollments/{enrollment_id}")
async def delete_enrollment(enrollment_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.enrollments.delete_one({"enrollment_id": enrollment_id})
    return {"message": "Enrollment deleted"}

# Prerequisites endpoints
@app.get("/prerequisites/", response_model=List[Prerequisite])
async def get_prerequisites(current_user: Annotated[Accounts, Depends(get_current_user)]):
    return list(db.prerequisites.find())

@app.post("/prerequisites/", response_model=Prerequisite)
async def create_prerequisite(prerequisite: Prerequisite, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.prerequisites.insert_one(prerequisite.model_dump())
    return prerequisite

@app.put("/prerequisites/{course_id}", response_model=Prerequisite)
async def update_prerequisite(course_id: str, prerequisite: Prerequisite, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.prerequisites.update_one({"course_id": course_id}, {"$set": prerequisite.model_dump()})
    return prerequisite

@app.delete("/prerequisites/{course_id}")
async def delete_prerequisite(course_id: str, current_user: Annotated[Accounts, Depends(get_current_user)]):
    db.prerequisites.delete_one({"course_id": course_id})
    return {"message": "Prerequisite deleted"}

# Course intention conversions
@app.post("/process_intentions/")
async def process_course_intentions(current_user: Annotated[Accounts, Depends(get_current_user)]):
    intentions = list(db.course_intentions.find())
    if not intentions:
        return {"message": "No course intentions to process"}
    
    course_intentions = defaultdict(list)
    for intention in intentions:
        key = (intention['course_code'], intention['semester'])
        course_intentions[key].append(intention)
    
    results = {
        "successful_enrollments": 0,
        "failed_prerequisites": 0,
        "failed_scheduling": 0,
        "details": []
    }
    
    for (course_code, semester), intentions in course_intentions.items():
        course = db.courses.find_one({"course_code": course_code})
        if not course:
            results['details'].append(f"Course {course_code} not found")
            continue
        
        offerings = list(db.course_offerings.find({
            "course_code": course_code,
            "semester": semester
        }))
        
        num_sections_needed = (len(intentions) // 30) + 1
        
        while len(offerings) < num_sections_needed:
            new_offering = {
                "offering_id": f"{course_code}-{semester}-S{len(offerings)+1}",
                "course_code": course_code,
                "course_name": course['course_name'],
                "instructor": "",
                "semester": semester,
                "available_seats": 30,
                "course_time": course.get('course_time', [])
            }
            db.course_offerings.insert_one(new_offering)
            offerings.append(new_offering)
        
        for intention in intentions:
            student_id = intention['student_id']
            student = db.students.find_one({"student_id": student_id})
            if not student or not all(prereq in student.get('completed_courses', []) 
                                    for prereq in course.get('prerequisites', [])):
                results['failed_prerequisites'] += 1
                results['details'].append(f"Student {student_id} missing prerequisites for {course_code}")
                continue
            
            enrolled = False
            for offering in sorted(offerings, key=lambda x: x['available_seats'], reverse=True):
                if offering['available_seats'] > 0:
                    if not offering.get('instructor'):
                        if not assign_instructor(offering, course):
                            continue
                    
                    if not offering.get('room_id'):
                        if not assign_room(offering):
                            continue
                    
                    enrollment = {
                        "enrollment_id": f"{student_id}-{offering['offering_id']}",
                        "student_id": student_id,
                        "offering_id": offering['offering_id'],
                        "enrollment_date": datetime.now().isoformat(),
                        "grade": None
                    }
                    db.enrollments.insert_one(enrollment)
                    db.course_offerings.update_one(
                        {"offering_id": offering['offering_id']},
                        {"$inc": {"available_seats": -1}}
                    )
                    db.students.update_one(
                        {"student_id": student_id},
                        {"$addToSet": {"enrolled_courses": offering['offering_id']}}
                    )
                    results['successful_enrollments'] += 1
                    enrolled = True
                    break
            
            if not enrolled:
                results['failed_scheduling'] += 1
                results['details'].append(f"Could not enroll student {student_id} in {course_code}")
    
    db.course_intentions.delete_many({})
    return results

def assign_instructor(offering, course):
    instructors = list(db.instructors.find({
        "courses_teachable": offering['course_code'],
        "department_id": course.get('department_id', '')
    }))
    for instructor in instructors:
        if is_instructor_available(instructor['instructor_id'], offering['course_time']):
            db.course_offerings.update_one(
                {"offering_id": offering['offering_id']},
                {"$set": {"instructor": instructor['instructor_id']}}
            )
            return True
    return False

def assign_room(offering):
    rooms = list(db.locations.find({
        "available_seats": {"$gte": 30}
    }))
    for room in rooms:
        if is_room_available(room['room_id'], offering['course_time']):
            db.course_offerings.update_one(
                {"offering_id": offering['offering_id']},
                {"$set": {"room_id": room['room_id']}}
            )
            return True
    return False

def is_instructor_available(instructor_id, course_times):
    instructor_offerings = list(db.course_offerings.find({
        "instructor": instructor_id,
        "course_time": {"$exists": True, "$ne": []}
    }))
    for other_offering in instructor_offerings:
        if any(time in other_offering['course_time'] for time in course_times):
            return False
    return True

def is_room_available(room_id, course_times):
    room_offerings = list(db.course_offerings.find({
        "room_id": room_id,
        "course_time": {"$exists": True, "$ne": []}
    }))
    for other_offering in room_offerings:
        if any(time in other_offering['course_time'] for time in course_times):
            return False
    return True