<script>
  import { onMount } from 'svelte';
  import { ENDPOINTS } from '$lib/config.js';

  /**
   * @typedef {Object} Faculty
   * @property {string} faculty_id
   * @property {string} faculty_name
   */

  /** @type {Faculty[]} */
  let faculties = [];
  let isLoading = true;
  let error = '';

  onMount(async () => {
    try {
      const response = await fetch('/api/faculties');

      if (!response.ok) {
        throw new Error('Failed to load faculties');
      }

      faculties = await response.json();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  });
</script>

<svelte:head>
  <title>Faculties - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 page-title">Faculties</div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading faculties...</div>
    </div>
  {:else}
    <div class="faculties-grid">
      {#each faculties as faculty}
        <div class="mdc-card faculty-card">
          <div class="mdc-card__content">
            <h2 class="mdc-typography--headline6">{faculty.faculty_name}</h2>
            <div class="faculty-details">
              <p class="mdc-typography--body2">
                <span class="detail-label">Faculty ID:</span> {faculty.faculty_id}
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

  .faculties-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .faculty-card {
    margin-bottom: 1rem;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  }

  .faculty-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .faculty-details {
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
