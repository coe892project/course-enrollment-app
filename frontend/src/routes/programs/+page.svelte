<script>
  import { onMount } from 'svelte';
  import { ENDPOINTS } from '$lib/config.js';
  import { getPrograms, getDepartments } from '$lib/api.js';
  import { token } from '$lib/stores.js';

  /**
   * @typedef {Object} Program
   * @property {string} program_id
   * @property {string} program_name
   * @property {string} degree_type
   * @property {string} department_id
   */

  /**
   * @typedef {Object} Department
   * @property {string} department_id
   * @property {string} department_name
   * @property {string} faculty_id
   */

  /** @type {Program[]} */
  let programs = [];
  /** @type {Department[]} */
  let departments = [];
  let isLoading = true;
  let error = '';

  onMount(async () => {
    try {
      // Load programs and departments in parallel using API functions that include the token
      const [programsData, departmentsData] = await Promise.all([
        getPrograms(),
        getDepartments()
      ]);

      // Set the data
      programs = programsData;
      departments = departmentsData;
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
  <title>Programs - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 page-title">Programs</div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading programs...</div>
    </div>
  {:else}
    <div class="programs-grid">
      {#each programs as program}
        <div class="mdc-card program-card">
          <div class="mdc-card__content">
            <h2 class="mdc-typography--headline6">{program.program_name}</h2>
            <div class="program-details">
              <p class="mdc-typography--body2">
                <span class="detail-label">Program ID:</span> {program.program_id}
              </p>
              <p class="mdc-typography--body2">
                <span class="detail-label">Degree Type:</span> {program.degree_type}
              </p>
              <p class="mdc-typography--body2">
                <span class="detail-label">Department:</span> {getDepartmentName(program.department_id)}
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

  .programs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .program-card {
    margin-bottom: 1rem;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  }

  .program-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .program-details {
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
