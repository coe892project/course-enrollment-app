import { ENDPOINTS } from '$lib/config.js';

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
