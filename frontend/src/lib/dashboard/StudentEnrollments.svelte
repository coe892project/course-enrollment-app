<script lang="ts">
  import CourseCard from '$lib/CourseCard.svelte';
  import { token } from '$lib/stores';
  import { get } from 'svelte/store';
  import { getStudents, getEnrollments, getCourseOfferings } from '$lib/api';
  import type { Student, Enrollment, CourseOffering, EnrolledCourse } from '$lib/types';

  export let selectedStudentId = '';

  let students: Student[] = [];
  let enrollments: Enrollment[] = [];
  let courseOfferings: CourseOffering[] = [];
  let enrolledCourses: EnrolledCourse[] = [];
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
        getStudents(),
        getEnrollments(),
        getCourseOfferings()
      ]);

      students = studentsResponse;
      enrollments = enrollmentsResponse;
      courseOfferings = offeringsResponse;

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
    enrolledCourses = mappedCourses.filter((course): course is EnrolledCourse => course !== null);
  }

  /**
   * Handle unenrolling a student from a course
   * @param {string} courseId - The course ID to unenroll from
   */
  async function handleUnenroll(courseId: string) {
    if (!selectedStudentId) {
      error = 'No student selected';
      return;
    }

    unenrollSuccess = '';
    error = '';
    isLoading = true;

    try {
      const authToken = get(token);
      const response = await fetch('/api/unenroll', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
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

  // Initial data load
  loadData();

  // This function will be called when the user manually selects a student
  function handleStudentChange() {
    if (selectedStudentId && !isLoading) {
      loadData();
    }
  }
</script>

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

<style>
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
</style>
