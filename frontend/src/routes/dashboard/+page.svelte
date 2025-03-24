<script>
  import { user } from '$lib/stores';
  import CourseCard from '$lib/CourseCard.svelte';
  import { onMount } from 'svelte';

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

  /**
   * @typedef {Object} EnrolledCourse
   * @property {string} id
   * @property {string} title
   * @property {string} description
   * @property {string} instructor
   * @property {number} seats
   * @property {string} enrollmentDate
   * @property {string|null} grade
   */

  /** @type {Student[]} */
  let students = [];
  /** @type {string} */
  let selectedStudentId = '';
  /** @type {Enrollment[]} */
  let enrollments = [];
  /** @type {CourseOffering[]} */
  let courseOfferings = [];
  /** @type {EnrolledCourse[]} */
  let enrolledCourses = [];
  let isLoading = true;
  let error = '';
  let unenrollSuccess = '';

  /**
   * Load all data from the backend
   */
  async function loadData() {
    isLoading = true;
    error = '';

    try {
      // Load all data in parallel
      const [studentsResponse, enrollmentsResponse, offeringsResponse] = await Promise.all([
        fetch('/api/students/'),
        fetch('/api/enrollments/'),
        fetch('/api/course_offerings/')
      ]);

      // Check responses
      if (!studentsResponse.ok) throw new Error('Failed to load students');
      if (!enrollmentsResponse.ok) throw new Error('Failed to load enrollments');
      if (!offeringsResponse.ok) throw new Error('Failed to load course offerings');

      // Parse responses
      students = await studentsResponse.json();
      enrollments = await enrollmentsResponse.json();
      courseOfferings = await offeringsResponse.json();

      // Set default selected student if not already set
      if (!selectedStudentId && students.length > 0) {
        selectedStudentId = students[0].student_id;
      }

      // Update enrolled courses for the selected student
      if (selectedStudentId) {
        updateEnrolledCourses();
      }
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  }

  // Initial data load
  onMount(loadData);

  /**
   * Update enrolled courses when student selection changes
   */
  function updateEnrolledCourses() {
    // Filter enrollments for the selected student
    const studentEnrollments = enrollments.filter(
      enrollment => enrollment.student_id === selectedStudentId
    );

    // Map enrollments to course details
    const mappedCourses = studentEnrollments
      .map(enrollment => {
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
      });

    // Filter out null values
    /** @type {EnrolledCourse[]} */
    enrolledCourses = mappedCourses.filter(course => course !== null);
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
      await loadData();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
      isLoading = false;
    }
  }

  // Watch for changes to selectedStudentId
  $: if (selectedStudentId && !isLoading) {
    // Reload data when student selection changes
    loadData();
  }
</script>

<svelte:head>
  <title>Student Dashboard - Course Enrollment</title>
</svelte:head>

<main class="container mx-auto p-4">
  <div class="mb-8">
    <h1 class="text-3xl font-bold mb-2">Admin Dashboard</h1>
    <p class="text-gray-600">Logged in as: {$user.name}</p>
    <div class="mt-4 flex gap-4">
      <a href="/" class="text-blue-500 hover:underline">Home</a>
      <a href="/courses" class="text-blue-500 hover:underline">Manage Enrollments</a>
    </div>
  </div>

  {#if error}
    <div class="bg-red-100 text-red-700 p-4 rounded mb-4">{error}</div>
  {/if}

  {#if unenrollSuccess}
    <div class="bg-green-100 text-green-700 p-4 rounded mb-4">{unenrollSuccess}</div>
  {/if}

  <div class="mb-6">
    <label for="student-select" class="block text-sm font-medium text-gray-700 mb-2">
      Select Student to View Enrollments
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

  <h2 class="text-2xl font-bold mb-4">
    {#if selectedStudentId}
      {students.find(s => s.student_id === selectedStudentId)?.first_name || ''}'s Enrolled Courses
    {:else}
      Student Enrollments
    {/if}
  </h2>

  {#if isLoading}
    <div class="animate-pulse text-gray-500">Loading courses...</div>
  {:else if !selectedStudentId}
    <div class="bg-blue-100 text-blue-700 p-4 rounded">
      Please select a student to view their enrollments
    </div>
  {:else if enrolledCourses.length === 0}
    <div class="bg-blue-100 text-blue-700 p-4 rounded">
      This student is not enrolled in any courses yet.
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each enrolledCourses as course}
        <div class="border rounded-lg p-4 shadow-sm">
          <CourseCard {course} />

          <div class="mt-4 text-sm text-gray-600">
            <div>Enrolled on: {new Date(course.enrollmentDate).toLocaleDateString()}</div>
            {#if course.grade}
              <div class="font-semibold">Grade: {course.grade}</div>
            {/if}

            <button
              on:click={() => handleUnenroll(course.id)}
              class="w-full mt-3 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Unenroll
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</main>
