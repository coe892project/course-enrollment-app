export interface Student {
  student_id: string;
  first_name: string;
  last_name: string;
  status: string;
  program_id: string;
  enrolled_courses: string[];
  completed_courses: string[];
}

export interface Enrollment {
  enrollment_id: string;
  student_id: string;
  offering_id: string;
  enrollment_date: string;
  grade: string | null;
}

export interface CourseOffering {
  offering_id: string;
  course_code: string;
  course_name: string;
  instructor: string;
  semester: string;
  year: number;
  available_seats: number;
}

export interface EnrolledCourse {
  id: string;
  title: string;
  description: string;
  instructor: string;
  seats: number;
  enrollmentDate: string;
  grade: string | null;
}

export interface Department {
  department_id: string;
  department_name: string;
  faculty_id: string;
}

export interface Instructor {
  instructor_id: string;
  first_name: string;
  last_name: string;
  department_id: string;
  title: string;
  courses_teachable: string[];
}
