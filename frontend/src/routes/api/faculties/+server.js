import { ENDPOINTS } from '$lib/config.js';
import { apiRequest } from '$lib/api.js';

/**
 * @typedef {Object} ApiFaculty
 * @property {string} faculty_id
 * @property {string} faculty_name
 */

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function GET({ request }) {
  try {
    // Use apiRequest to ensure proper token handling
    const response = await apiRequest(ENDPOINTS.FACULTIES);

    // If unauthorized, return 401 to trigger logout in the frontend
    if (response.status === 401) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

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
