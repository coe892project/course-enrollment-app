<script>
  import { onMount } from 'svelte';
  import { ENDPOINTS } from '$lib/config.js';
  import { getLocations } from '$lib/api.js';
  import { token } from '$lib/stores.js';

  /**
   * @typedef {Object} Location
   * @property {string} room_id
   * @property {string} room_name
   * @property {number} available_seats
   * @property {string[]} available_times
   */

  /** @type {Location[]} */
  let locations = [];
  let isLoading = true;
  let error = '';

  onMount(async () => {
    try {
      // Use the getLocations function that includes the token
      locations = await getLocations();
    } catch (error_) {
      error = error_ instanceof Error ? error_.message : String(error_);
    } finally {
      isLoading = false;
    }
  });
</script>

<svelte:head>
  <title>Locations - Course Enrollment</title>
</svelte:head>

<main>
  <div class="mdc-typography--headline4 page-title">Locations</div>

  {#if error}
    <div class="mdc-card error-card">
      <div class="mdc-card__content">
        <p class="mdc-typography--body2">{error}</p>
      </div>
    </div>
  {/if}

  {#if isLoading}
    <div class="loading-indicator">
      <div class="mdc-typography--body1 animate-pulse">Loading locations...</div>
    </div>
  {:else}
    <div class="locations-grid">
      {#each locations as location}
        <div class="mdc-card location-card">
          <div class="mdc-card__content">
            <h2 class="mdc-typography--headline6">{location.room_name}</h2>
            <div class="location-details">
              <p class="mdc-typography--body2">
                <span class="detail-label">Room ID:</span> {location.room_id}
              </p>
              <p class="mdc-typography--body2">
                <span class="detail-label">Available Seats:</span> {location.available_seats}
              </p>
              <div class="available-times">
                <p class="mdc-typography--body2 detail-label">Available Times:</p>
                <ul class="times-list">
                  {#each location.available_times as time}
                    <li class="mdc-typography--body2">{time}</li>
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

  .locations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .location-card {
    margin-bottom: 1rem;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  }

  .location-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  }

  .mdc-card__content {
    padding: 1rem;
  }

  .location-details {
    margin-top: 1rem;
  }

  .detail-label {
    font-weight: 500;
    color: var(--mdc-theme-primary);
  }

  .available-times {
    margin-top: 0.5rem;
  }

  .times-list {
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
