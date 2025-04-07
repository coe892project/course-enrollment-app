from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional
from pydantic import BaseModel
import logging
import os
import json
from pathlib import Path
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

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
    section: Optional[str] = None
    semester: str
    prerequisites: List[str] = []
    corequisites: List[str] = []
    available_seats: int
    instructor: str
    lecture_time: List[str] = []
    possible_lab_times: List[str] = []
    department_id: Optional[str] = None

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
    seats_per_section: int

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

class CourseIntention(BaseModel):
    intention_id: str
    student_id: str
    course_code: str
    semester: str
    timestamp: Optional[datetime] = None
    status: Optional[str] = "pending"
    error: Optional[str] = None

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = db.accounts.find_one({"username": username})
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
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
    except JWTError as jwt_err:
        logger.error(jwt_err)
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

@app.post("/course_intentions/", response_model=CourseIntention)
async def create_intention(
    intention: CourseIntention,
    current_user: Annotated[Accounts, Depends(get_current_user)]
):
    intention.timestamp = datetime.utcnow()
    
    if not db.students.find_one({"student_id": intention.student_id}):
        raise HTTPException(status_code=400, detail="Student not found")

    if not db.courses.find_one({"course_code": intention.course_code}):
        raise HTTPException(status_code=400, detail="Course not found")

    existing = db.course_intentions.find_one({
        "student_id": intention.student_id,
        "course_code": intention.course_code,
        "semester": intention.semester
    })
    if existing:
        raise HTTPException(status_code=400, detail="Intention already exists")
    
    db.course_intentions.insert_one(intention.model_dump())
    return intention

@app.get("/course_intentions/", response_model=List[CourseIntention])
async def get_all_intentions(
    current_user: Annotated[Accounts, Depends(get_current_user)],
    status: Optional[str] = None,
    student_id: Optional[str] = None,
    semester: Optional[str] = None
):
    query = {}
    if status:
        query["status"] = status
    if student_id:
        query["student_id"] = student_id
    if semester:
        query["semester"] = semester
    
    return list(db.course_intentions.find(query))

@app.get("/course_intentions/{intention_id}", response_model=CourseIntention)
async def get_intention(
    intention_id: str,
    current_user: Annotated[Accounts, Depends(get_current_user)]
):
    """Get a specific intention by ID"""
    intention = db.course_intentions.find_one({"intention_id": intention_id})
    if not intention:
        raise HTTPException(status_code=404, detail="Intention not found")
    return intention

@app.put("/course_intentions/{intention_id}", response_model=CourseIntention)
async def update_intention(
    intention_id: str,
    intention_update: CourseIntention,
    current_user: Annotated[Accounts, Depends(get_current_user)]
):
    existing = db.course_intentions.find_one({"intention_id": intention_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Intention not found")
    
    if intention_update.student_id != existing["student_id"]:
        raise HTTPException(status_code=400, detail="Cannot change student_id")
    if intention_update.course_code != existing["course_code"]:
        raise HTTPException(status_code=400, detail="Cannot change course_code")
    
    update_data = intention_update.model_dump(exclude_unset=True)
    update_data["timestamp"] = datetime.strftime("%d/%m/%Y %H:%M:%S")
    
    db.course_intentions.update_one(
        {"intention_id": intention_id},
        {"$set": update_data}
    )
    return db.course_intentions.find_one({"intention_id": intention_id})

@app.delete("/course_intentions/{intention_id}")
async def delete_intention(
    intention_id: str,
    current_user: Annotated[Accounts, Depends(get_current_user)]
):
    """Delete a course intention"""
    result = db.course_intentions.delete_one({"intention_id": intention_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Intention not found")
    return {"message": "Intention deleted"}

# Course intention conversions
@app.post("/process_intentions/")
async def process_course_intentions(current_user: Annotated[Accounts, Depends(get_current_user)]):
    intentions = list(db.course_intentions.find({"status": "pending"}))
    if not intentions:
        return {"message": "No course intentions to process"}
    
    student_intentions = defaultdict(list)
    for intention in intentions:
        student_intentions[intention['student_id']].append(intention)
    
    course_intentions = defaultdict(list)
    for intention in intentions:
        key = (intention['course_code'], intention['semester'])
        course_intentions[key].append(intention)
    
    results = {
        "successful_enrollments": 0,
        "failed_prerequisites": 0,
        "failed_scheduling": 0,
        "sections_created": 0,
        "details": []
    }

    offerings = {}
    for (course_code, semester), intentions in course_intentions.items():
        offering = db.course_offerings.find_one({"course_code": course_code, "semester": semester})
        if not offering:
            offering = {
                "offering_id": f"{course_code}-{semester}",
                "course_code": course_code,
                "course_name": f"{course_code} Lecture",
                "semester": semester,
                "year": datetime.now().year,
                "instructor": "",
                "room_id": "",
                "course_time": [],
                "max_sections": 1,
                "seats_per_section": 30,
                "total_hours": 3
            }
            db.course_offerings.insert_one(offering)
            results['details'].append(f"Created new offering for {course_code}")
        offerings[(course_code, semester)] = offering

        sections = list(db.courses.find({"course_code": course_code, "semester": semester}).sort("section", 1))
        num_sections_needed = (len(intentions) // offering['seats_per_section']) + 1
        while len(sections) < num_sections_needed:
            section_num = len(sections) + 1
            new_section = {
                "course_code": course_code,
                "course_name": f"{course_code} Section {section_num}",
                "semester": semester,
                "section": str(section_num),
                "available_seats": offering['seats_per_section'],
                "prerequisites": [],
                "corequisites": [],
                "course_time": [],
                "instructor": "",
                "room_id": ""
            }
            db.courses.insert_one(new_section)
            sections.append(new_section)
            results['sections_created'] += 1
            results['details'].append(f"Created section {section_num} for {course_code}")

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    hours = [f"{h}:00" for h in range(8, 21)]
    all_time_slots = [f"{day} {start}-{end}" for day in days for start, end in zip(hours, hours[1:])]

    def generate_all_3hour_combinations():
        combinations = []
        for day in days:
            for i in range(len(hours) - 3):
                combinations.append([f"{day} {hours[i]}-{hours[i+3]}"])
        for day in days:
            for i in range(len(hours) - 2):
                for j in range(len(hours) - 1):
                    if i == j or abs(i - j) < 2:
                        continue
                    combinations.append([f"{day} {hours[i]}-{hours[i+2]}", f"{day} {hours[j]}-{hours[j+1]}"])
        for day1 in days:
            for day2 in days:
                if day1 == day2:
                    continue
                for i in range(len(hours) - 2):
                    for j in range(len(hours) - 1):
                        combinations.append([f"{day1} {hours[i]}-{hours[i+2]}", f"{day2} {hours[j]}-{hours[j+1]}"])
        for day in days:
            for i in range(len(hours) - 1):
                for j in range(len(hours) - 1):
                    for k in range(len(hours) - 1):
                        if i == j or i == k or j == k:
                            continue
                        combinations.append([f"{day} {hours[i]}-{hours[i+1]}", f"{day} {hours[j]}-{hours[j+1]}", f"{day} {hours[k]}-{hours[k+1]}"])
        for day1 in days:
            for day2 in days:
                for day3 in days:
                    if day1 == day2 or day1 == day3 or day2 == day3:
                        continue
                    for i in range(len(hours) - 1):
                        for j in range(len(hours) - 1):
                            for k in range(len(hours) - 1):
                                combinations.append([f"{day1} {hours[i]}-{hours[i+1]}", f"{day2} {hours[j]}-{hours[j+1]}", f"{day3} {hours[k]}-{hours[k+1]}"])
        return combinations

    all_possible_combinations = generate_all_3hour_combinations()
    sorted_courses = sorted(course_intentions.keys(), key=lambda k: len(course_intentions[k]), reverse=True)
    scheduled_courses = {}
    used_time_slots = set()
    instructor_schedules = defaultdict(set)
    room_schedules = defaultdict(set)

    for course_key in sorted_courses:
        course_code, semester = course_key
        offering = offerings[course_key]
        students_in_course = {i['student_id'] for i in course_intentions[course_key]}
        selected_time = None
        selected_instructor = None
        selected_room = None
        
        for time_combo in all_possible_combinations:
            flat_time_combo = []
            for item in time_combo:
                if isinstance(item, list):
                    flat_time_combo.extend(item)
                else:
                    flat_time_combo.append(item)
            if set(flat_time_combo) & used_time_slots:
                continue
            
            student_conflict = False
            for student_id in students_in_course:
                student_courses = []
                for intention in student_intentions[student_id]:
                    other_course_key = (intention['course_code'], intention['semester'])
                    if other_course_key in scheduled_courses:
                        student_courses.extend(scheduled_courses[other_course_key])
                if set(flat_time_combo) & set(student_courses):
                    student_conflict = True
                    break
            if student_conflict:
                continue
            
            available_instructors = list(db.instructors.find({"courses_teachable": course_code}))
            instructor_found = False
            for instructor in available_instructors:
                instructor_busy = False
                for slot in flat_time_combo:
                    if slot in instructor_schedules[instructor['instructor_id']]:
                        instructor_busy = True
                        break
                if not instructor_busy:
                    selected_instructor = instructor['instructor_id']
                    instructor_found = True
                    break
            
            if not instructor_found:
                continue
            
            available_rooms = list(db.locations.find({"available_seats": {"$gte": offering['seats_per_section']}}))
            room_found = False
            for room in available_rooms:
                room_busy = False
                for slot in flat_time_combo:
                    if slot in room_schedules[room['room_id']]:
                        room_busy = True
                        break
                if not room_busy:
                    selected_room = room['room_id']
                    room_found = True
                    break
            
            if room_found:
                selected_time = flat_time_combo
                break
        
        if not selected_time:
            results['details'].append(f"Could not schedule {course_code}")
            continue
        
        used_time_slots.update(selected_time)
        for slot in selected_time:
            instructor_schedules[selected_instructor].add(slot)
            room_schedules[selected_room].add(slot)
        
        db.course_offerings.update_one(
            {"offering_id": offering['offering_id']},
            {"$set": {
                "course_time": selected_time,
                "instructor": selected_instructor,
                "room_id": selected_room
            }}
        )
        
        db.courses.update_many(
            {"course_code": course_code, "semester": semester},
            {"$set": {
                "course_time": selected_time,
                "instructor": selected_instructor,
                "room_id": selected_room
            }}
        )
        
        scheduled_courses[course_key] = selected_time
        results['details'].append(f"Scheduled {course_code} at {selected_time}")

    for (course_code, semester), intentions in course_intentions.items():
        offering = offerings[(course_code, semester)]
        sections = list(db.courses.find({"course_code": course_code, "semester": semester}).sort("section", 1))
        for intention in intentions:
            student_id = intention['student_id']
            student = db.students.find_one({"student_id": student_id})
            if not student or not all(prereq in student.get('completed_courses', []) for prereq in sections[0].get('prerequisites', [])):
                await update_intention(
                    intention['intention_id'],
                    CourseIntention(
                        intention_id=intention['intention_id'],
                        student_id=student_id,
                        course_code=course_code,
                        semester=semester,
                        status="failed",
                        error="Missing prerequisites"
                    ),
                    current_user
                )
                results['failed_prerequisites'] += 1
                continue

            enrolled = False
            for section in sections:
                if section['available_seats'] > 0:
                    create_enrollment(student_id, section['_id'])
                    db.courses.update_one({"_id": section['_id']}, {"$inc": {"available_seats": -1}})
                    await update_intention(
                        intention['intention_id'],
                        CourseIntention(
                            intention_id=intention['intention_id'],
                            student_id=student_id,
                            course_code=course_code,
                            semester=semester,
                            status="enrolled",
                            section=section['section']
                        ),
                        current_user
                    )
                    results['successful_enrollments'] += 1
                    enrolled = True
                    break

            if not enrolled:
                await update_intention(
                    intention['intention_id'],
                    CourseIntention(
                        intention_id=intention['intention_id'],
                        student_id=student_id,
                        course_code=course_code,
                        semester=semester,
                        status="failed",
                        error="No available seats"
                    ),
                    current_user
                )
                results['failed_scheduling'] += 1

    return results

def assign_instructor(offering):
    instructors = list(db.instructors.find({
        "courses_teachable": offering['course_code']
    }))
    for instructor in instructors:
        if is_instructor_available(instructor['instructor_id'], offering.get('course_time', [])):
            db.course_offerings.update_one(
                {"offering_id": offering['offering_id']},
                {"$set": {"instructor": instructor['instructor_id']}}
            )
            return True
    return False

def assign_room(offering):
    rooms = list(db.locations.find({"available_seats": {"$gte": 30}}))
    for room in rooms:
        if is_room_available(room['room_id'], offering.get('course_time', [])):
            db.course_offerings.update_one(
                {"offering_id": offering['offering_id']},
                {"$set": {"room_id": room['room_id']}}
            )
            return True
    return False

def is_instructor_available(instructor_id, course_times):
    conflicts = db.course_offerings.count_documents({
        "instructor": instructor_id,
        "course_time": {"$in": course_times}
    })
    return conflicts == 0

def is_room_available(room_id, course_times):
    conflicts = db.course_offerings.count_documents({
        "room_id": room_id,
        "course_time": {"$in": course_times}
    })
    return conflicts == 0

def create_enrollment(student_id, section_id):
    enrollment = {
        "enrollment_id": f"{student_id}-{section_id}",
        "student_id": student_id,
        "section_id": str(section_id),
        "enrollment_date": datetime.now().isoformat(),
        "grade": None
    }
    db.enrollments.insert_one(enrollment)

COLLECTIONS = {
    "accounts": "accounts",
    "courses": "courses",
    "students": "students",
    "course_offerings": "course_offerings",
    "locations": "locations",
    "instructors": "instructors",
    "programs": "programs",
    "departments": "departments",
    "faculties": "faculties",
    "enrollments": "enrollments",
    "prerequisites": "prerequisites",
    "course_intentions": "course_intentions"
}

FILE_TO_COLLECTION = {
    "DummyAccounts.json": "accounts",
    "DummyCourses.json": "courses",
    "DummyStudents.json": "students",
    "DummyCoursesOffered.json": "course_offerings",
    "DummyLocations.json": "locations",
    "DummyInstructor.json": "instructors",
    "DummyPrograms.json": "programs",
    "DummyDepartments.json": "departments",
    "DummyFaculties.json": "faculties",
    "DummyEnrollments.json": "enrollments",
    "DummyPrerequisites.json": "prerequisites",
    "DummyCourseIntentions.json": "course_intentions"
}

@app.post("/reset/", status_code=200)
async def reset_database():
    try:
        for collection in COLLECTIONS.values():
            db[collection].delete_many({})

        dummy_data_path = Path("./DummyData")
        for filename, collection_name in FILE_TO_COLLECTION.items():
            file_path = dummy_data_path / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data:
                        db[collection_name].insert_many(data)

        return {"message": "Database reset and populated with dummy data successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting database: {str(e)}")