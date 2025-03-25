import { PUBLIC_API_URL } from '$env/static/public';

// API configuration
export const API_URL = PUBLIC_API_URL;

// API endpoints
export const ENDPOINTS = {
  COURSES: `${API_URL}/courses/`,
  ENROLLMENTS: `${API_URL}/enrollments/`,
  COURSE_OFFERINGS: `${API_URL}/course_offerings/`,
  STUDENTS: `${API_URL}/students/`,
  DEPARTMENTS: `${API_URL}/departments/`,
  FACULTIES: `${API_URL}/faculties/`,
  INSTRUCTORS: `${API_URL}/instructors/`,
  LOCATIONS: `${API_URL}/locations/`,
  PROGRAMS: `${API_URL}/programs/`,
  PREREQUISITES: `${API_URL}/prerequisites/`,
};
