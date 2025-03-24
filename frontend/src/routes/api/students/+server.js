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

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.STUDENTS);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiStudent[]} */
    const students = await response.json();

    return new Response(JSON.stringify(students), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching students:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
