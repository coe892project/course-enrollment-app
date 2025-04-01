import { login } from '$lib/api.js';
import { json } from '@sveltejs/kit';

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    // Try to parse JSON first
    let username, password;

    const contentType = request.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {
      const data = await request.json();
      username = data.username;
      password = data.password;
    } else if (contentType.includes('application/x-www-form-urlencoded')) {
      const formData = await request.formData();
      username = formData.get('username');
      password = formData.get('password');
    } else {
      return json({ error: 'Unsupported content type' }, { status: 415 });
    }

    if (!username || !password) {
      return json({ error: 'Username and password are required' }, { status: 400 });
    }

    console.log(`Login attempt for user: ${username}`);

    try {
      // Use the login function from api.js
      const tokenData = await login(username, password);

      // Return the token response
      return json(tokenData, { status: 200 });
    } catch (loginError) {
      console.error('Login error:', loginError);
      // Handle login errors
      return json({
        error: loginError instanceof Error ? loginError.message : 'Invalid credentials'
      }, { status: 401 });
    }
  } catch (error) {
    console.error('Error during login:', error);
    return json({
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
