import { ENDPOINTS } from '$lib/config.js';
import { token } from '$lib/stores.js';
import { get } from 'svelte/store';

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

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function GET({ request }) {
  try {
    // Get the token from the request headers
    const authHeader = request.headers.get('Authorization');

    // Use the token from the request headers or fall back to the token from the store
    const authToken = authHeader || (get(token) ? `Bearer ${get(token)}` : '');

    const response = await fetch(ENDPOINTS.COURSE_OFFERINGS, {
      headers: {
        'Authorization': authToken
      }
    });

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
