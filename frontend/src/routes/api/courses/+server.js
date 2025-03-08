import { mockCourses } from '../../../mocks.js';

export function GET() {
  return new Response(JSON.stringify(mockCourses), {
    headers: { 'Content-Type': 'application/json' }
  });
}
