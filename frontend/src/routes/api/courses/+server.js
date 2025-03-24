import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiCourse
 * @property {string} course_code
 * @property {string} course_name
 * @property {string} section
 * @property {string} semester
 * @property {string[]} prerequisites
 * @property {string[]} corequisites
 * @property {number} available_seats
 * @property {string} instructor
 * @property {string[]} course_time
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.COURSES);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiCourse[]} */
    const courses = await response.json();

    // Transform the API response to match the expected format in the frontend
    const transformedCourses = courses.map((course) => ({
      id: course.course_code,
      title: course.course_name,
      description: `${course.course_code} - ${course.section} - ${course.semester}`,
      instructor: course.instructor,
      seats: course.available_seats
    }));

    return new Response(JSON.stringify(transformedCourses), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching courses:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
