import { mockCourses } from '../../../mocks.js';

export async function POST({ request }) {
  const { courseId } = await request.json();
  const course = mockCourses.find(c => c.id === Number(courseId));

  if (!course) {
    return new Response(JSON.stringify({ error: 'Course not found' }), {
      status: 404
    });
  }

  if (course.seats <= 0) {
    return new Response(JSON.stringify({ error: 'Course is full' }), {
      status: 400
    });
  }

  // Mock enrollment response
  return new Response(JSON.stringify({
    ...course,
    enrollmentDate: new Date().toISOString()
  }), {
    status: 201,
    headers: { 'Content-Type': 'application/json' }
  });
}
