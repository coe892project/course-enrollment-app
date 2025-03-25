import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiDepartment
 * @property {string} department_id
 * @property {string} department_name
 * @property {string} faculty_id
 */

export async function GET() {
  try {
    const response = await fetch(ENDPOINTS.DEPARTMENTS);

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
