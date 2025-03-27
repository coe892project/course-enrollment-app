import { ENDPOINTS } from '$lib/config.js';
import { json } from '@sveltejs/kit';

/**
 * @typedef {Object} ApiLocation
 * @property {string} room_id
 * @property {string} room_name
 * @property {number} available_seats
 * @property {string[]} available_times
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.LOCATIONS);

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

    const response = await fetch(ENDPOINTS.LOCATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(locationData)
    });

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
