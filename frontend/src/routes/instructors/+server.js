import { ENDPOINTS } from '$lib/config.js';
import { json } from '@sveltejs/kit';
import { token } from '$lib/stores.js';
import { get } from 'svelte/store';

/**
 * @typedef {Object} ApiInstructor
 * @property {string} instructor_id
 * @property {string} first_name
 * @property {string} last_name
 * @property {string} department_id
 * @property {string} title
 * @property {string[]} courses_teachable
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
    const response = await fetch(ENDPOINTS.INSTRUCTORS, {
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

/**
 * Create a new instructor
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const instructorData = await request.json();

    // Get the authorization token from the request headers
    const authHeader = request.headers.get('Authorization');

    // Get the token from the store if no authorization header is provided
    const authToken = authHeader || (get(token) ? `Bearer ${get(token)}` : '');

    // Make a POST request to the backend API with the authorization token
    const response = await fetch(ENDPOINTS.INSTRUCTORS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authToken
      },
      body: JSON.stringify(instructorData)
    });

    // If unauthorized, return 401 to trigger logout in the frontend
    if (response.status === 401) {
      return json({ error: 'Unauthorized' }, { status: 401 });
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    // Return the created instructor
    const createdInstructor = await response.json();
    return json(createdInstructor);
  } catch (error) {
    console.error('Error creating instructor:', error);
    return json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
