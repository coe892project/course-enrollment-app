<script>
  import { user } from '$lib/stores';
  import CourseCard from '$lib/CourseCard.svelte';
  import { onMount } from 'svelte';

  /**
   * @typedef {Object} Course
   * @property {string} id
   * @property {string} title
   * @property {string} description
   * @property {string} instructor
   * @property {number} seats
   */

  /**
   * @typedef {Object} Student
   * @property {string} student_id
   * @property {string} first_name
   * @property {string} last_name
   * @property {string} status
   * @property {string} program_id
   * @property {string[]} enrolled_courses
   * @property {string[]} completed_courses
   */

  /**
   * @typedef {Object} Enrollment
   * @property {string} enrollment_id
   * @property {string} student_id
   * @property {string} offering_id
   * @property {string} enrollment_date
   * @property {string|null} grade
   */

  /**
   * @typedef {Object} CourseOffering
   * @property {string} offering_id
   * @property {string} course_code
   * @property {string} course_name
   * @property {string} instructor
   * @property {string} semester
   * @property {number} year
   * @property {number} available_seats
   */

  /** @type {Course[]} */
  let courses = [];
  /** @type {Student[]} */
  let students = [];
  /** @type {Enrollment[]} */
  let enrollments = [];
  let isLoading = true;
  let error = '';
  /** @type {string} */
  let selectedStudentId = '';
  let enrollmentSuccess = '';
  let unenrollSuccess = '';

  // Get course offerings
  /** @type {CourseOffering[]} */
  let courseOfferings = [];

  /**
   * Check if a student is enrolled in a course
   * @param {string} studentId - The student ID
   * @param {string} courseId - The course ID
   * @returns {boolean} - Whether the student is enrolled in the course
   */
  function isEnrolled(studentId, courseId) {
    try {
      // Find the course offering for this course
      const offering = courseOfferings.find(o => o.course_code === courseId);
      if (!offering) return false;

      // Check if there's an enrollment for this student and offering
      return enrollments.some(e =>
        e.student_id === studentId &&
        e.offering_id === offering.offering_id
      );
    } catch (error) {
      console.error('Error checking enrollment:', error);
      return false;
    }
  }

  onMount(async () => {
    try {
      // Load all data in parallel
      const [coursesResponse, studentsResponse, enrollmentsResponse, offeringsResponse] = await Promise.all([
        fetch('/api/courses'),
        fetch('/api/students/'),
        fetch('/api/enrollments/'),
        fetch('/api/course_offerings/')
      ]);

      // Check responses
      if (!coursesResponse.ok) throw new Error('Failed to load courses');
      if (!studentsResponse.ok) throw new Error('Failed to load students');
      if (!enrollmentsResponse.ok) throw new Error('Failed to load enrollments');
      if (!offeringsResponse.ok) throw new Error('Failed to load course offerings');

      // Parse responses
      courses = await coursesResponse.json();
      students = await studentsResponse.json();
      enrollments = await enrollmentsResponse.json();
      courseOfferings = await offeringsResponse.json();

      // Set default selected student
      if (students.length > 0) {
        selectedStudentId = students[0].student_id;
      }
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  });

  /**
   * Find the course offering for a course
   * @param {string} courseId - The course ID
   * @returns {CourseOffering|undefined} - The course offering or undefined if not found
   */
  function findCourseOffering(courseId) {
    return courseOfferings.find(o => o.course_code === courseId);
  }

  /**
   * Reload all data from the backend
   */
  async function reloadData() {
    try {
      isLoading = true;

      // Load all data in parallel
      const [coursesResponse, enrollmentsResponse, offeringsResponse] = await Promise.all([
        fetch('/api/courses'),
        fetch('/api/enrollments/'),
        fetch('/api/course_offerings/')
      ]);

      // Check responses
      if (!coursesResponse.ok) throw new Error('Failed to load courses');
      if (!enrollmentsResponse.ok) throw new Error('Failed to load enrollments');
      if (!offeringsResponse.ok) throw new Error('Failed to load course offerings');

      // Parse responses
      courses = await coursesResponse.json();
      enrollments = await enrollmentsResponse.json();
      courseOfferings = await offeringsResponse.json();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  }

  /**
   * Handle enrollment of a student in a course
   * @param {string} courseId - The course ID
   */
  async function handleEnrollment(courseId) {
    if (!selectedStudentId) {
      error = 'Please select a student';
      return;
    }

    enrollmentSuccess = '';
    unenrollSuccess = '';
    error = '';

    try {
      const response = await fetch('/api/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: selectedStudentId,
          courseId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Enrollment failed');
      }

      // Get the enrollment result
      await response.json();

      // Show success message
      enrollmentSuccess = `Successfully enrolled student ${selectedStudentId} in ${courseId}`;

      // Reload data from the backend to get the updated state
      await reloadData();

    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    }
  }

  /**
   * Handle unenrolling a student from a course
   * @param {string} courseId - The course ID to unenroll from
   */
  async function handleUnenroll(courseId) {
    if (!selectedStudentId) {
      error = 'No student selected';
      return;
    }

    unenrollSuccess = '';
    enrollmentSuccess = '';
    error = '';
    isLoading = true;

    try {
      const response = await fetch('/api/unenroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: selectedStudentId,
          courseId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to unenroll student');
      }

      // Show success message
      unenrollSuccess = `Successfully unenrolled student from ${courseId}`;

      // Reload data to update the UI
      await reloadData();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
      isLoading = false;
    }
  }
</script>

<svelte:head>
  <title>All Courses - Course Enrollment</title>
</svelte:head>

<main class="container mx-auto p-4">
  <h1 class="text-3xl font-bold mb-6">Available Courses</h1>

  {#if error}
    <div class="bg-red-100 text-red-700 p-4 rounded mb-4">{error}</div>
  {/if}

  {#if enrollmentSuccess}
    <div class="bg-green-100 text-green-700 p-4 rounded mb-4">{enrollmentSuccess}</div>
  {/if}

  {#if unenrollSuccess}
    <div class="bg-green-100 text-green-700 p-4 rounded mb-4">{unenrollSuccess}</div>
  {/if}

  <div class="mb-6">
    <label for="student-select" class="block text-sm font-medium text-gray-700 mb-2">
      Select Student to Enroll
    </label>
    <select
      id="student-select"
      bind:value={selectedStudentId}
      class="w-full p-2 border rounded"
    >
      {#each students as student}
        <option value={student.student_id}>
          {student.first_name} {student.last_name} ({student.student_id})
        </option>
      {/each}
    </select>
  </div>

  {#if isLoading}
    <div class="animate-pulse space-y-4">
      <div class="h-16 bg-gray-200 rounded"></div>
      <div class="h-16 bg-gray-200 rounded"></div>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each courses as course}
        <div class="border rounded-lg p-4 shadow-sm">
          <CourseCard {course} />

          <div class="mt-4 text-sm text-gray-600">
            <div class="flex justify-between items-center mb-2">
              <span>Seats available: {course.seats}</span>
              <span class="text-xs">
                {course.instructor}
              </span>
            </div>

            {#if selectedStudentId && isEnrolled(selectedStudentId, course.id)}
              <div class="text-green-600 font-medium mb-2">
                ✓ Student already enrolled
              </div>
              <button
                on:click={() => handleUnenroll(course.id)}
                class="w-full bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                Unenroll Student
              </button>
            {:else}
              <button
                on:click={() => handleEnrollment(course.id)}
                class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                disabled={course.seats <= 0 || !selectedStudentId}
              >
                {course.seats > 0 ? 'Enroll Student' : 'Course Full'}
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</main>
