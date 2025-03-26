import { ENDPOINTS } from '$lib/config.js';
import { json } from '@sveltejs/kit';

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

/**
 * Create a new course
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const courseData = await request.json();

    // Make a POST request to the backend API
    const response = await fetch(ENDPOINTS.COURSES, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(courseData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    // Return the created course
    const createdCourse = await response.json();
    return json(createdCourse);
  } catch (error) {
    console.error('Error creating course:', error);
    return json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
