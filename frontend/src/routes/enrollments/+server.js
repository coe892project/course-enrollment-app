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
 * @param {URL} params.url
 */
export async function GET({ url }) {
  try {
    // Fetch all enrollments
    const enrollmentsResponse = await fetch(ENDPOINTS.ENROLLMENTS);

    if (!enrollmentsResponse.ok) {
      throw new Error(`API error: ${enrollmentsResponse.status}`);
    }

    /** @type {ApiEnrollment[]} */
    const allEnrollments = await enrollmentsResponse.json();

    // If userId is provided, filter enrollments for that user
    const userId = url.searchParams.get('userId');
    if (userId) {
      // Filter enrollments for the specific user
      const userEnrollments = allEnrollments.filter(
        enrollment => enrollment.student_id === userId
      );

      if (userEnrollments.length === 0) {
        // No enrollments found for this user
        return new Response(JSON.stringify([]), {
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Fetch course offerings to get course details
      const offeringsResponse = await fetch(ENDPOINTS.COURSE_OFFERINGS);

      if (!offeringsResponse.ok) {
        throw new Error(`API error: ${offeringsResponse.status}`);
      }

      /** @type {ApiCourseOffering[]} */
      const courseOfferings = await offeringsResponse.json();

      // Map enrollments to course details
      const enrolledCourses = userEnrollments.map(enrollment => {
        const offering = courseOfferings.find(
          offering => offering.offering_id === enrollment.offering_id
        );

        if (!offering) {
          return null;
        }

        return {
          id: offering.course_code,
          title: offering.course_name,
          description: `${offering.course_code} - ${offering.semester} ${offering.year}`,
          instructor: offering.instructor,
          seats: offering.available_seats,
          enrollmentDate: enrollment.enrollment_date,
          grade: enrollment.grade
        };
      }).filter(Boolean); // Remove any null entries

      return new Response(JSON.stringify(enrolledCourses), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // If no userId is provided, return all enrollments
    return new Response(JSON.stringify(allEnrollments), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error fetching enrollments:', error);
    return new Response(JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
