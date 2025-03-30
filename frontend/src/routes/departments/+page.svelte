<script>
  import { onMount } from 'svelte';
  import { ENDPOINTS } from '$lib/config.js';
  import { getDepartments, getFaculties } from '$lib/api.js';
  import { token } from '$lib/stores.js';

  /**
   * @typedef {Object} Department
   * @property {string} department_id
   * @property {string} department_name
   * @property {string} faculty_id
   */

  /**
   * @typedef {Object} Faculty
   * @property {string} faculty_id
   * @property {string} faculty_name
   */

  /** @type {Department[]} */
  let departments = [];
  /** @type {Faculty[]} */
  let faculties = [];
  let isLoading = true;
  let error = '';

  onMount(async () => {
    try {
      // Load departments and faculties in parallel using API functions that include the token
      const [departmentsData, facultiesData] = await Promise.all([
        getDepartments(),
        getFaculties()
      ]);

      // Set the data
      departments = departmentsData;
      faculties = facultiesData;
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  });

  /**
   * Get faculty name by ID
   * @param {string} facultyId - The faculty ID
   * @returns {string} - The faculty name or "Unknown Faculty" if not found
   */
  function getFacultyName(facultyId) {
    const faculty = faculties.find(f => f.faculty_id === facultyId);
    return faculty ? faculty.faculty_name : 'Unknown Faculty';
  }
</script>

<svelte:head>
  <title>Departments - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 page-title">Departments</div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading departments...</div>
    </div>
  {:else}
    <div class="departments-grid">
      {#each departments as department}
        <div class="mdc-card department-card">
          <div class="mdc-card__content">
            <h2 class="mdc-typography--headline6">{department.department_name}</h2>
            <div class="department-details">
              <p class="mdc-typography--body2">
                <span class="detail-label">Department ID:</span> {department.department_id}
              </p>
              <p class="mdc-typography--body2">
                <span class="detail-label">Faculty:</span> {getFacultyName(department.faculty_id)}
              </p>
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

  .departments-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .department-card {
    margin-bottom: 1rem;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  }

  .department-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .department-details {
    margin-top: 1rem;
  }

  .detail-label {
    font-weight: 500;
    color: var(--mdc-theme-primary);
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
