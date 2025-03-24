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

<main>
  <div class="mdc-typography--headline4 page-title">Available Courses</div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if enrollmentSuccess}
    <div class="mdc-card success-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{enrollmentSuccess}</p>
      </div>
    </div>
  {/if}

  {#if unenrollSuccess}
    <div class="mdc-card success-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{unenrollSuccess}</p>
      </div>
    </div>
  {/if}

  <div class="student-select-container">
    <label class="mdc-typography--subtitle1" for="student-select">
      Select Student to Enroll
    </label>
    <div class="mdc-select">
      <select
        id="student-select"
        class="mdc-select__native-control"
        bind:value={selectedStudentId}
      >
        {#each students as student}
          <option value={student.student_id}>
            {student.first_name} {student.last_name} ({student.student_id})
          </option>
        {/each}
      </select>
      <div class="mdc-select__dropdown-icon"></div>
      <div class="mdc-line-ripple"></div>
    </div>
  </div>

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading courses...</div>
    </div>
  {:else}
    <div class="courses-grid">
      {#each courses as course}
        <div class="course-container">
          <CourseCard {course} />

          <div class="course-actions">
            <div class="course-details">
              <span class="mdc-typography--caption">Seats available: {course.seats}</span>
              <span class="mdc-typography--caption">{course.instructor}</span>
            </div>

            {#if selectedStudentId && isEnrolled(selectedStudentId, course.id)}
              <div class="enrollment-status">
                <span class="mdc-typography--body2 enrolled-status">✓ Student already enrolled</span>
              </div>
              <button
                class="mdc-button mdc-button--raised mdc-button--danger"
                on:click={() => handleUnenroll(course.id)}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Unenroll Student</span>
              </button>
            {:else}
              <button
                class="mdc-button mdc-button--raised"
                class:mdc-button--disabled={course.seats <= 0 || !selectedStudentId}
                on:click={() => handleEnrollment(course.id)}
                disabled={course.seats <= 0 || !selectedStudentId}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">
                  {course.seats > 0 ? 'Enroll Student' : 'Course Full'}
                </span>
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</main>

<style>
  main {
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-title {
    margin-bottom: 1.5rem;
    color: var(--mdc-theme-primary);
  }

  .student-select-container {
    margin: 1.5rem 0;
  }

  .courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .course-container {
    margin-bottom: 1rem;
  }

  .course-actions {
    margin-top: 0.5rem;
    padding: 0.5rem;
  }

  .course-details {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .enrollment-status {
    margin-bottom: 0.5rem;
    text-align: center;
  }

  .enrolled-status {
    color: var(--mdc-theme-secondary);
    font-weight: 500;
  }

  .error-card {
    background-color: #ffebee;
    margin-bottom: 1rem;
  }

  .success-card {
    background-color: #e8f5e9;
    margin-bottom: 1rem;
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .loading-indicator {
    padding: 1rem;
    text-align: center;
  }

  .mdc-button--danger {
    background-color: var(--mdc-theme-error);
    color: white;
  }

  .mdc-button {
    width: 100%;
  }

  .mdc-button--disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
    cursor: not-allowed;
  }

  /* Add Material Design ripple effect to buttons */
  .mdc-button__ripple {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }
</style>
