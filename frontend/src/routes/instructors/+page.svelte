<script>
  import { onMount } from 'svelte';
  import { ENDPOINTS } from '$lib/config.js';

  /**
   * @typedef {Object} Instructor
   * @property {string} instructor_id
   * @property {string} first_name
   * @property {string} last_name
   * @property {string} department_id
   * @property {string} title
   * @property {string[]} courses_teachable
   */

  /**
   * @typedef {Object} Department
   * @property {string} department_id
   * @property {string} department_name
   * @property {string} faculty_id
   */

  /** @type {Instructor[]} */
  let instructors = [];
  /** @type {Department[]} */
  let departments = [];
  let isLoading = true;
  let error = '';

  onMount(async () => {
    try {
      // Load instructors and departments in parallel
      const [instructorsResponse, departmentsResponse] = await Promise.all([
        fetch('/api/instructors'),
        fetch('/api/departments')
      ]);

      // Check responses
      if (!instructorsResponse.ok) throw new Error('Failed to load instructors');
      if (!departmentsResponse.ok) throw new Error('Failed to load departments');

      // Parse responses
      instructors = await instructorsResponse.json();
      departments = await departmentsResponse.json();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  });

  /**
   * Get department name by ID
   * @param {string} departmentId - The department ID
   * @returns {string} - The department name or "Unknown Department" if not found
   */
  function getDepartmentName(departmentId) {
    const department = departments.find(d => d.department_id === departmentId);
    return department ? department.department_name : 'Unknown Department';
  }
</script>

<svelte:head>
  <title>Instructors - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 page-title">Instructors</div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading instructors...</div>
    </div>
  {:else}
    <div class="instructors-grid">
      {#each instructors as instructor}
        <div class="mdc-card instructor-card">
          <div class="mdc-card__content">
            <h2 class="mdc-typography--headline6">{instructor.title} {instructor.first_name} {instructor.last_name}</h2>
            <div class="instructor-details">
              <p class="mdc-typography--body2">
                <span class="detail-label">Instructor ID:</span> {instructor.instructor_id}
              </p>
              <p class="mdc-typography--body2">
                <span class="detail-label">Department:</span> {getDepartmentName(instructor.department_id)}
              </p>
              <div class="courses-teachable">
                <p class="mdc-typography--body2 detail-label">Courses Teachable:</p>
                <ul class="courses-list">
                  {#each instructor.courses_teachable as course}
                    <li class="mdc-typography--body2">{course}</li>
                  {/each}
                </ul>
              </div>
            </div>
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

  .instructors-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .instructor-card {
    margin-bottom: 1rem;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  }

  .instructor-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .instructor-details {
    margin-top: 1rem;
  }

  .detail-label {
    font-weight: 500;
    color: var(--mdc-theme-primary);
  }

  .courses-teachable {
    margin-top: 0.5rem;
  }

  .courses-list {
    margin-top: 0.25rem;
    padding-left: 1.5rem;
  }

  .error-card {
    background-color: #ffebee;
    margin-bottom: 1rem;
  }

  .loading-indicator {
    padding: 1rem;
    text-align: center;
  }

  .animate-pulse {
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }
</style>
