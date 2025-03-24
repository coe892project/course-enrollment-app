import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiCourseOffering
 * @property {string} offering_id
 * @property {string} course_code
 * @property {string} course_name
 * @property {string} instructor
 * @property {string} semester
 * @property {number} year
 * @property {number} available_seats
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.COURSE_OFFERINGS);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiCourseOffering[]} */
    const courseOfferings = await response.json();

    return new Response(JSON.stringify(courseOfferings), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching course offerings:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
