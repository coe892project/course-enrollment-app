import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiInstructor
 * @property {string} instructor_id
 * @property {string} first_name
 * @property {string} last_name
 * @property {string} department_id
 * @property {string} title
 * @property {string[]} courses_teachable
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.INSTRUCTORS);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiInstructor[]} */
    const instructors = await response.json();

    return new Response(JSON.stringify(instructors), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching instructors:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
