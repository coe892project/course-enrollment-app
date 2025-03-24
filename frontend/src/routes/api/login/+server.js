import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiStudent
 * @property {string} student_id
 * @property {string} first_name
 * @property {string} last_name
 * @property {string} status
 * @property {string} program_id
 * @property {string[]} enrolled_courses
 * @property {string[]} completed_courses
 */

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const { email, password } = await request.json();

    // For demo purposes, we'll use a simple authentication method
    // In a real app, you would have proper authentication with JWT, etc.

    // Fetch all students
    const response = await fetch(ENDPOINTS.STUDENTS);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiStudent[]} */
    const students = await response.json();

    // For demo purposes, we'll authenticate using the student ID as both email and password
    // In a real app, you would have proper authentication
    const student = students.find(s => s.student_id === email && password === 'password');

    if (student) {
      // Transform student data to match the expected user format in the frontend
      const user = {
        id: student.student_id,
        name: `${student.first_name} ${student.last_name}`,
        email: `${student.student_id}@example.com`, // Generate a fake email
        role: 'student'
      };

      return new Response(JSON.stringify(user), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error during login:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
