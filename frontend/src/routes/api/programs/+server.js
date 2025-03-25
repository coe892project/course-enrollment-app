import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiProgram
 * @property {string} program_id
 * @property {string} program_name
 * @property {string} degree_type
 * @property {string} department_id
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.PROGRAMS);

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
