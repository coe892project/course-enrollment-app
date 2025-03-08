import { mockCourses } from '../../../mocks.js';

export function GET({ url }) {
  const userId = url.searchParams.get('userId');

  // Mock enrolled courses for user 1
  const enrolledCourses = userId === '1' ? [
    {
      ...mockCourses[0],
      enrollmentDate: '2025-03-01'
    }
  ] : [];

  return new Response(JSON.stringify(enrolledCourses), {
    headers: { 'Content-Type': 'application/json' }
  });
}
