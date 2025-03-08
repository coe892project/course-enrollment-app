import { mockUser } from '../../../mocks.js';

export async function POST({ request }) {
  const { email, password } = await request.json();

  // Simple mock validation
  if (email === 'test@example.com' && password === 'password') {
    return new Response(JSON.stringify(mockUser), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify({ error: 'Invalid credentials' }), {
    status: 401
  });
}
