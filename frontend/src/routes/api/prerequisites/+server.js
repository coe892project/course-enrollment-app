import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiPrerequisite
 * @property {string} course_id
 * @property {string} prerequisite_course_id
 */

export async function GET() {
  try {
    const response = await fetch(`${ENDPOINTS.PREREQUISITES}`);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiPrerequisite[]} */
    const prerequisites = await response.json();

    return new Response(JSON.stringify(prerequisites), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching prerequisites:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
