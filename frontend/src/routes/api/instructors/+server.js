import { ENDPOINTS } from '$lib/config.js';
import { json } from '@sveltejs/kit';

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

/**
 * Create a new instructor
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const instructorData = await request.json();

    // Make a POST request to the backend API
    const response = await fetch(ENDPOINTS.INSTRUCTORS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(instructorData)
    });

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
