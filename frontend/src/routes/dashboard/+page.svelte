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

  // This function will be called when the user manually selects a student
  function handleStudentChange() {
    if (selectedStudentId && !isLoading) {
      loadData();
    }
  }
</script>

<svelte:head>
  <title>Student Dashboard - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 dashboard-title">Admin Dashboard</div>
  <p class="mdc-typography--body1">Logged in as: {$user.name}</p>

  <div class="dashboard-nav">
    <a href="/" class="mdc-button">
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">Home</span>
    </a>
    <a href="/courses" class="mdc-button">
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">Manage Enrollments</span>
    </a>
  </div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
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
      Select Student to View Enrollments
    </label>
    <div class="mdc-select">
      <select
        id="student-select"
        class="mdc-select__native-control"
        bind:value={selectedStudentId}
        on:change={handleStudentChange}
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

  <h2 class="mdc-typography--headline5 courses-title">
    {#if selectedStudentId}
      {students.find(s => s.student_id === selectedStudentId)?.first_name || ''}'s Enrolled Courses
    {:else}
      Student Enrollments
    {/if}
  </h2>

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading courses...</div>
    </div>
  {:else if !selectedStudentId}
    <div class="mdc-card info-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body1">Please select a student to view their enrollments</p>
      </div>
    </div>
  {:else if enrolledCourses.length === 0}
    <div class="mdc-card info-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body1">This student is not enrolled in any courses yet.</p>
      </div>
    </div>
  {:else}
    <div class="courses-grid">
      {#each enrolledCourses as course}
        <div class="course-container">
          <CourseCard {course} />

          <div class="enrollment-details">
            <div class="mdc-typography--caption">
              Enrolled on: {new Date(course.enrollmentDate).toLocaleDateString()}
            </div>
            {#if course.grade}
              <div class="mdc-typography--subtitle2">Grade: {course.grade}</div>
            {/if}

            <button
              class="mdc-button mdc-button--raised mdc-button--danger"
              on:click={() => handleUnenroll(course.id)}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Unenroll</span>
            </button>
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

  .dashboard-title {
    margin-bottom: 0.5rem;
    color: var(--mdc-theme-primary);
  }

  .dashboard-nav {
    margin: 1rem 0;
    display: flex;
    gap: 1rem;
  }

  .student-select-container {
    margin: 1.5rem 0;
  }

  .courses-title {
    margin: 1.5rem 0 1rem;
    color: var(--mdc-theme-primary);
  }

  .courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .course-container {
    margin-bottom: 1rem;
  }

  .enrollment-details {
    margin-top: 0.5rem;
    padding: 0.5rem;
  }

  .error-card {
    background-color: #ffebee;
    margin-bottom: 1rem;
  }

  .success-card {
    background-color: #e8f5e9;
    margin-bottom: 1rem;
  }

  .info-card {
    background-color: #e3f2fd;
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
    width: 100%;
    margin-top: 0.5rem;
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
