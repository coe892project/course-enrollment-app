<script lang="ts">
  import { token } from '$lib/stores';
  import { get } from 'svelte/store';
  import { getDepartments } from '$lib/api';
  import type { Department, Instructor } from '$lib/types';

  export let onInstructorCreated: (instructor: Instructor) => void = () => {};

  let departments: Department[] = [];
  export let showInstructorForm = false;
  let newInstructor: Instructor = {
    instructor_id: '',
    first_name: '',
    last_name: '',
    department_id: '',
    title: '',
    courses_teachable: []
  };
  let courseTeachableInput = '';
  let instructorCreationSuccess = '';
  let instructorCreationError = '';

  // Load departments on component initialization
  async function loadDepartments() {
    try {
      departments = await getDepartments();
    } catch (error) {
      instructorCreationError = error instanceof Error ? error.message : String(error);
    }
  }

  // Call loadDepartments when the component is created
  loadDepartments();

  /**
   * Add a course teachable to the new instructor
   */
  function addCourseTeachable() {
    if (courseTeachableInput.trim()) {
      newInstructor.courses_teachable = [...newInstructor.courses_teachable, courseTeachableInput.trim()];
      courseTeachableInput = '';
    }
  }

  /**
   * Remove a course teachable from the new instructor
   * @param {string} course - The course to remove
   */
  function removeCourseTeachable(course: string) {
    newInstructor.courses_teachable = newInstructor.courses_teachable.filter(c => c !== course);
  }

  /**
   * Reset the instructor creation form
   */
  function resetInstructorForm() {
    newInstructor = {
      instructor_id: '',
      first_name: '',
      last_name: '',
      department_id: '',
      title: '',
      courses_teachable: []
    };
    courseTeachableInput = '';
    instructorCreationError = '';
    instructorCreationSuccess = '';
  }

  /**
   * Submit the instructor creation form
   */
  async function createInstructor() {
    instructorCreationError = '';
    instructorCreationSuccess = '';

    try {
      // Validate required fields
      if (!newInstructor.instructor_id || !newInstructor.first_name ||
          !newInstructor.last_name || !newInstructor.department_id ||
          !newInstructor.title) {
        instructorCreationError = 'Please fill in all required fields';
        return;
      }

      const authToken = get(token);
      // Send the instructor data to the API
      const response = await fetch('/api/instructors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(newInstructor)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create instructor');
      }

      // Get the created instructor
      const createdInstructor: Instructor = await response.json();

      // Show success message
      instructorCreationSuccess = `Successfully created instructor: ${createdInstructor.first_name} ${createdInstructor.last_name}`;

      // Call the callback function with the created instructor
      onInstructorCreated(createdInstructor);

      // Reset the form
      resetInstructorForm();
    } catch (error_) {
      instructorCreationError = error_ instanceof Error ? error_.message : String(error_);
    }
  }
</script>

{#if showInstructorForm}
  <div class="mdc-card course-form-card">
    <div class="mdc-card__content">
      <h2 class="mdc-typography--headline6">Create New Instructor</h2>

      {#if instructorCreationSuccess}
        <div class="success-message">
          <p class="mdc-typography--body2">{instructorCreationSuccess}</p>
        </div>
      {/if}

      {#if instructorCreationError}
        <div class="error-message">
          <p class="mdc-typography--body2">{instructorCreationError}</p>
        </div>
      {/if}

      <form on:submit|preventDefault={createInstructor}>
        <div class="form-row">
          <div class="form-field">
            <label class="mdc-typography--subtitle2" for="instructor-id">Instructor ID*</label>
            <input
              id="instructor-id"
              class="mdc-text-field__input"
              type="text"
              bind:value={newInstructor.instructor_id}
              required
            />
          </div>

          <div class="form-field">
            <label class="mdc-typography--subtitle2" for="title">Title*</label>
            <input
              id="title"
              class="mdc-text-field__input"
              type="text"
              bind:value={newInstructor.title}
              required
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label class="mdc-typography--subtitle2" for="first-name">First Name*</label>
            <input
              id="first-name"
              class="mdc-text-field__input"
              type="text"
              bind:value={newInstructor.first_name}
              required
            />
          </div>

          <div class="form-field">
            <label class="mdc-typography--subtitle2" for="last-name">Last Name*</label>
            <input
              id="last-name"
              class="mdc-text-field__input"
              type="text"
              bind:value={newInstructor.last_name}
              required
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-field">
            <label class="mdc-typography--subtitle2" for="department">Department*</label>
            <select
              id="department"
              class="mdc-select__native-control"
              bind:value={newInstructor.department_id}
              required
            >
              <option value="">Select a department</option>
              {#each departments as department}
                <option value={department.department_id}>{department.department_name}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-section">
          <label class="mdc-typography--subtitle2">Courses Teachable</label>
          <div class="array-input">
            <input
              class="mdc-text-field__input"
              type="text"
              placeholder="Enter course code"
              bind:value={courseTeachableInput}
            />
            <button
              type="button"
              class="mdc-button mdc-button--raised"
              on:click={addCourseTeachable}
            >
              <span class="mdc-button__ripple"></span>
              <span class="mdc-button__label">Add</span>
            </button>
          </div>

          {#if newInstructor.courses_teachable.length > 0}
            <div class="array-items">
              {#each newInstructor.courses_teachable as course}
                <div class="array-item">
                  <span>{course}</span>
                  <button
                    type="button"
                    class="mdc-button mdc-button--small"
                    on:click={() => removeCourseTeachable(course)}
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
            on:click={resetInstructorForm}
          >
            <span class="mdc-button__ripple"></span>
            <span class="mdc-button__label">Reset</span>
          </button>

          <button
            type="submit"
            class="mdc-button mdc-button--raised"
          >
            <span class="mdc-button__ripple"></span>
            <span class="mdc-button__label">Create Instructor</span>
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<style>
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
