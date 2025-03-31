import { ENDPOINTS } from '$lib/config.js';
import { token } from '$lib/stores.js';
import { get } from 'svelte/store';

/**
 * @typedef {Object} ApiDepartment
 * @property {string} department_id
 * @property {string} department_name
 * @property {string} faculty_id
 */

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function GET({ request }) {
  try {
    // Get the authorization token from the request headers
    const authHeader = request.headers.get('Authorization');

    // Get the token from the store if no authorization header is provided
    const authToken = authHeader || (get(token) ? `Bearer ${get(token)}` : '');

    // Make a GET request to the backend API with the authorization token
    const response = await fetch(ENDPOINTS.DEPARTMENTS, {
      headers: {
        'Authorization': authToken
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

    /** @type {ApiDepartment[]} */
    const departments = await response.json();

    return new Response(JSON.stringify(departments), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching departments:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
