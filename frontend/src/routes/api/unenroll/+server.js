import { ENDPOINTS } from '$lib/config.js';

/**
 * @typedef {Object} ApiEnrollment
 * @property {string} enrollment_id
 * @property {string} student_id
 * @property {string} offering_id
 * @property {string} enrollment_date
 * @property {string|null} grade
 */

/**
 * @typedef {Object} ApiCourseOffering
 * @property {string} offering_id
 * @property {string} course_code
 * @property {string} course_name
 * @property {string} instructor
 * @property {string} semester
 * @property {number} year
 * @property {number} available_seats
 */

/**
 * @param {Object} params
 * @param {Request} params.request
 */
export async function POST({ request }) {
  try {
    const { userId, courseId } = await request.json();

    if (!userId || !courseId) {
      return new Response(JSON.stringify({ error: 'User ID and Course ID are required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // First, fetch all enrollments
    const enrollmentsResponse = await fetch(ENDPOINTS.ENROLLMENTS);

    if (!enrollmentsResponse.ok) {
      throw new Error(`API error: ${enrollmentsResponse.status}`);
    }

    /** @type {ApiEnrollment[]} */
    const allEnrollments = await enrollmentsResponse.json();

    // Find course offerings to get the offering ID for this course
    const offeringsResponse = await fetch(ENDPOINTS.COURSE_OFFERINGS);

    if (!offeringsResponse.ok) {
      throw new Error(`API error: ${offeringsResponse.status}`);
    }

    /** @type {ApiCourseOffering[]} */
    const courseOfferings = await offeringsResponse.json();
    const offering = courseOfferings.find((o) => o.course_code === courseId);

    if (!offering) {
      return new Response(JSON.stringify({ error: 'Course not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Find the enrollment to delete
    const enrollment = allEnrollments.find(
      e => e.student_id === userId && e.offering_id === offering.offering_id
    );

    if (!enrollment) {
      return new Response(JSON.stringify({ error: 'Enrollment not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Delete the enrollment
    const deleteResponse = await fetch(`${ENDPOINTS.ENROLLMENTS}${enrollment.enrollment_id}`, {
      method: 'DELETE'
    });

    if (!deleteResponse.ok) {
      throw new Error(`Failed to delete enrollment: ${deleteResponse.status}`);
    }

    return new Response(JSON.stringify({
      message: 'Enrollment deleted successfully',
      courseId,
      userId
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error unenrolling student:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
