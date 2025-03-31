import { ENDPOINTS } from '$lib/config.js';
import { json } from '@sveltejs/kit';

/**
 * @typedef {Object} ApiLocation
 * @property {string} room_id
 * @property {string} room_name
 * @property {number} available_seats
 * @property {string[]} available_times
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
    const response = await fetch(ENDPOINTS.LOCATIONS, {
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

    /** @type {ApiLocation[]} */
    const locations = await response.json();

    return new Response(JSON.stringify(locations), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching locations:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Create a new location
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const locationData = await request.json();

    // Get the authorization token from the request headers
    const authHeader = request.headers.get('Authorization');

    // Make a POST request to the backend API with the authorization token
    const response = await fetch(ENDPOINTS.LOCATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || ''
      },
      body: JSON.stringify(locationData)
    });

    // If unauthorized, return 401 to trigger logout in the frontend
    if (response.status === 401) {
      return json({ error: 'Unauthorized' }, { status: 401 });
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `API error: ${response.status}`);
    }

    // Return the created location
    const createdLocation = await response.json();
    return json(createdLocation);
  } catch (error) {
    console.error('Error creating location:', error);
    return json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 });
  }
}
