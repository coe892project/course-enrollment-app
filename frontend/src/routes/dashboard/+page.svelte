<script lang="ts">
  import { user, token } from '$lib/stores';
  import { get } from 'svelte/store';
  import StudentEnrollments from '$lib/dashboard/StudentEnrollments.svelte';
  import InstructorCreationForm from '$lib/dashboard/InstructorCreationForm.svelte';
  import type { Instructor } from '$lib/types';
  import { getDepartments } from '$lib/api';

  interface CourseForm {
    course_code: string;
    course_name: string;
    section: string;
    semester: 'Fall' | 'Winter' | 'Spring' | 'Summer';
    prerequisites: string[];
    corequisites: string[];
    available_seats: number;
    instructor: string;
    course_time: string[];
  }

  let showInstructorForm = false;
  let showCourseForm = false;
  let showLocationForm = false;

  // Form state for creating a new course
  let newCourse: CourseForm = {
    course_code: '',
    course_name: '',
    section: '',
    semester: 'Fall',
    prerequisites: [],
    corequisites: [],
    available_seats: 30,
    instructor: '',
    course_time: []
  };
  let prerequisiteInput = '';
  let corequisiteInput = '';
  let courseTimeInput = '';
  let courseCreationSuccess = '';
  let courseCreationError = '';

  /**
   * Add a prerequisite to the new course
   */
  function addPrerequisite() {
    if (prerequisiteInput.trim()) {
      newCourse.prerequisites = [...newCourse.prerequisites, prerequisiteInput.trim()];
      prerequisiteInput = '';
    }
  }

  /**
   * Remove a prerequisite from the new course
   * @param {string} prereq - The prerequisite to remove
   */
  function removePrerequisite(prereq: string) {
    newCourse.prerequisites = newCourse.prerequisites.filter((p: string) => p !== prereq);
  }

  /**
   * Add a corequisite to the new course
   */
  function addCorequisite() {
    if (corequisiteInput.trim()) {
      newCourse.corequisites = [...newCourse.corequisites, corequisiteInput.trim()];
      corequisiteInput = '';
    }
  }

  /**
   * Remove a corequisite from the new course
   * @param {string} coreq - The corequisite to remove
   */
  function removeCorequisite(coreq: string) {
    newCourse.corequisites = newCourse.corequisites.filter((c: string) => c !== coreq);
  }

  /**
   * Add a course time to the new course
   */
  function addCourseTime() {
    if (courseTimeInput.trim()) {
      newCourse.course_time = [...newCourse.course_time, courseTimeInput.trim()];
      courseTimeInput = '';
    }
  }

  /**
   * Remove a course time from the new course
   * @param {string} time - The course time to remove
   */
  function removeCourseTime(time: string) {
    newCourse.course_time = newCourse.course_time.filter((t: string) => t !== time);
  }

  /**
   * Reset the course creation form
   */
  function resetCourseForm() {
    newCourse = {
      course_code: '',
      course_name: '',
      section: '',
      semester: 'Fall',
      prerequisites: [],
      corequisites: [],
      available_seats: 30,
      instructor: '',
      course_time: []
    };
    prerequisiteInput = '';
    corequisiteInput = '';
    courseTimeInput = '';
    courseCreationError = '';
    courseCreationSuccess = '';
  }

  /**
   * Submit the course creation form
   */
  async function createCourse() {
    courseCreationError = '';
    courseCreationSuccess = '';

    try {
      // Validate required fields
      if (!newCourse.course_code || !newCourse.course_name || !newCourse.section ||
        !newCourse.semester || !newCourse.instructor) {
        courseCreationError = 'Please fill in all required fields';
        return;
      }

      const authToken = get(token);
      // Send the course data to the API
      const response = await fetch('/api/courses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(newCourse)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create course');
      }

      // Get the created course
      const createdCourse = await response.json();

      // Show success message
      courseCreationSuccess = `Successfully created course: ${createdCourse.course_code} - ${createdCourse.course_name}`;

      // Reset the form
      resetCourseForm();
    } catch (error_) {
      courseCreationError = error_ instanceof Error ? error_.message : String(error_);
    }
  }

  /**
   * Handle instructor creation
   * @param {Instructor} instructor - The newly created instructor
   */
  function handleInstructorCreated(instructor: Instructor) {
    // Optionally, you can add any additional logic here after an instructor is created
    console.log('Instructor created:', instructor);
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
    <button class="mdc-button" on:click={() => showCourseForm = !showCourseForm}>
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">{showCourseForm ? 'Hide Course Form' : 'Create New Course'}</span>
    </button>
    <button class="mdc-button" on:click={() => showInstructorForm = !showInstructorForm}>
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">{showInstructorForm ? 'Hide Instructor Form' : 'Create New Instructor'}</span>
    </button>
    <button class="mdc-button" on:click={() => showLocationForm = !showLocationForm}>
      <span class="mdc-button__ripple"></span>
      <span class="mdc-button__label">{showLocationForm ? 'Hide Location Form' : 'Create New Location'}</span>
    </button>
  </div>

  <InstructorCreationForm
    bind:showInstructorForm
    onInstructorCreated={handleInstructorCreated}
  />

  {#if showCourseForm}
    <div class="mdc-card course-form-card">
      <div class="mdc-card__content">
        <h2 class="mdc-typography--headline6">Create New Course</h2>

        {#if courseCreationSuccess}
          <div class="success-message">
            <p class="mdc-typography--body2">{courseCreationSuccess}</p>
          </div>
        {/if}

        {#if courseCreationError}
          <div class="error-message">
            <p class="mdc-typography--body2">{courseCreationError}</p>
          </div>
        {/if}

        <form on:submit|preventDefault={createCourse}>
          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="course-code">Course Code*</label>
              <input
                id="course-code"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.course_code}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="course-name">Course Name*</label>
              <input
                id="course-name"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.course_name}
                required
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="section">Section*</label>
              <input
                id="section"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.section}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="semester">Semester*</label>
              <select
                id="semester"
                class="mdc-select__native-control"
                bind:value={newCourse.semester}
                required
              >
                <option value="Fall">Fall</option>
                <option value="Winter">Winter</option>
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="instructor">Instructor*</label>
              <input
                id="instructor"
                class="mdc-text-field__input"
                type="text"
                bind:value={newCourse.instructor}
                required
              />
            </div>

            <div class="form-field">
              <label class="mdc-typography--subtitle2" for="available-seats">Available Seats*</label>
              <input
                id="available-seats"
                class="mdc-text-field__input"
                type="number"
                min="1"
                bind:value={newCourse.available_seats}
                required
              />
            </div>
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Prerequisites</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter prerequisite course code"
                bind:value={prerequisiteInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addPrerequisite}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newCourse.prerequisites.length > 0}
              <div class="array-items">
                {#each newCourse.prerequisites as prereq}
                  <div class="array-item">
                    <span>{prereq}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removePrerequisite(prereq)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Corequisites</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter corequisite course code"
                bind:value={corequisiteInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addCorequisite}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newCourse.corequisites.length > 0}
              <div class="array-items">
                {#each newCourse.corequisites as coreq}
                  <div class="array-item">
                    <span>{coreq}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removeCorequisite(coreq)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-section">
            <label class="mdc-typography--subtitle2">Course Times</label>
            <div class="array-input">
              <input
                class="mdc-text-field__input"
                type="text"
                placeholder="Enter course time (e.g., 'Mon 10:00-11:30')"
                bind:value={courseTimeInput}
              />
              <button
                type="button"
                class="mdc-button mdc-button--raised"
                on:click={addCourseTime}
              >
                <span class="mdc-button__ripple"></span>
                <span class="mdc-button__label">Add</span>
              </button>
            </div>

            {#if newCourse.course_time.length > 0}
              <div class="array-items">
                {#each newCourse.course_time as time}
                  <div class="array-item">
                    <span>{time}</span>
                    <button
                      type="button"
                      class="mdc-button mdc-button--small"
                      on:click={() => removeCourseTime(time)}
                    >
                      <span class="mdc-button__ripple"></span>
                      <span class="mdc-button__label">Remove</span>
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="mdc-button"
              on:click={resetCourseForm}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Reset</span>
            </button>

            <button
              type="submit"
              class="mdc-button mdc-button--raised"
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Create Course</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <StudentEnrollments />
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

  /* Reusable form styles */
  .course-form-card {
    margin-bottom: 1.5rem;
  }

  .form-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .form-field {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .form-field label {
    margin-bottom: 0.25rem;
  }

  .form-section {
    margin-bottom: 1rem;
  }

  .array-input {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .array-input input {
    flex: 1;
  }

  .array-items {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .array-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background-color: #f5f5f5;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .mdc-button--small {
    padding: 0 0.5rem;
    min-width: auto;
    height: 24px;
    line-height: 24px;
    font-size: 0.75rem;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .success-message {
    background-color: #e8f5e9;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .error-message {
    background-color: #ffebee;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style>
