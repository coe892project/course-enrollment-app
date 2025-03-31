import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiProgram
 * @property {string} program_id
 * @property {string} program_name
 * @property {string} degree_type
 * @property {string} department_id
 */

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function GET({ request }) {
  try {
    // Get the authorization token from the request headers
    const authHeader = request.headers.get('Authorization');

    // Make a GET request to the backend API with the authorization token
    const response = await fetch(ENDPOINTS.PROGRAMS, {
      headers: {
        'Authorization': authHeader || ''
      }
    });

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

    /** @type {ApiProgram[]} */
    const programs = await response.json();

    return new Response(JSON.stringify(programs), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching programs:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
