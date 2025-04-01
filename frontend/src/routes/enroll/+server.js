import { ENDPOINTS } from "$lib/config.js";
import { token } from "$lib/stores.js";
import { get } from "svelte/store";

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
    const authHeader = request.headers.get("Authorization");
    const authToken = authHeader || (get(token) ? `Bearer ${get(token)}` : "");

    if (!userId || !courseId) {
      return new Response(
        JSON.stringify({ error: "User ID and Course ID are required" }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // First, fetch course offerings to find the offering ID for this course
    const offeringsResponse = await fetch(ENDPOINTS.COURSE_OFFERINGS, {
      headers: {
        "Content-Type": "application/json",
        Authorization: authToken,
      },
    });

    if (!offeringsResponse.ok) {
      throw new Error(`API error: ${offeringsResponse.status}`);
    }

    /** @type {ApiCourseOffering[]} */
    const courseOfferings = await offeringsResponse.json();

    // Find the offering for this course
    const offering = courseOfferings.find(
      (offering) => offering.course_code === courseId
    );

    if (!offering) {
      return new Response(JSON.stringify({ error: "Course not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (offering.available_seats <= 0) {
      return new Response(JSON.stringify({ error: "Course is full" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Create a new enrollment
    const enrollmentData = {
      enrollment_id: `E${Date.now()}`, // Generate a unique ID
      student_id: userId,
      offering_id: offering.offering_id,
      enrollment_date: new Date().toISOString().split("T")[0], // Format as YYYY-MM-DD
      grade: null,
    };

    // Post the new enrollment to the API
    const enrollResponse = await fetch(ENDPOINTS.ENROLLMENTS, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: authToken },
      body: JSON.stringify(enrollmentData),
    });

    if (!enrollResponse.ok) {
      throw new Error(`Enrollment failed: ${enrollResponse.status}`);
    }

    // Return the course details with enrollment date
    return new Response(
      JSON.stringify({
        id: offering.course_code,
        title: offering.course_name,
        description: `${offering.course_code} - ${offering.semester} ${offering.year}`,
        instructor: offering.instructor,
        seats: offering.available_seats,
        enrollmentDate: enrollmentData.enrollment_date,
      }),
      {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Error enrolling in course:", error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
