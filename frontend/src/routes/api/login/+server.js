import { login } from '$lib/api.js';

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const { username, password } = await request.json();

    try {
      // Use the login function from api.js
      const tokenData = await login(username, password);

      // Return the token response
      return new Response(JSON.stringify(tokenData), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (loginError) {
      // Handle login errors
      return new Response(JSON.stringify({
        error: loginError instanceof Error ? loginError.message : 'Invalid credentials'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  } catch (error) {
    console.error('Error during login:', error);
    return new Response(JSON.stringify({
      error: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
