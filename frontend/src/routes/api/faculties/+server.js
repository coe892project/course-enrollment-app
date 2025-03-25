import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiFaculty
 * @property {string} faculty_id
 * @property {string} faculty_name
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.FACULTIES);

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    /** @type {ApiFaculty[]} */
    const faculties = await response.json();

    return new Response(JSON.stringify(faculties), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching faculties:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
