<script>
  import { courses, user } from '$lib/stores';
  import CourseCard from '$lib/CourseCard.svelte';
  import { onMount } from 'svelte';

  // Fetch courses on component mount
  onMount(async () => {
    try {
      const response = await fetch('/api/courses');
      const data = await response.json();
      courses.set(data);
    } catch (error) {
      console.error('Error loading courses:', error);
    }
  });
</script>

<svelte:head>
  <title>Course Enrollment</title>
</svelte:head>

<main>
  <div class="header-container">
    <a href="/courses" class="mdc-typography--headline4 page-title">Available Courses</a>
    <div class="user-section">
      <span class="mdc-typography--body1 welcome-text">Welcome, {$user.name}!</span>
      <a href="/dashboard" class="mdc-button mdc-button--raised">
        <span class="mdc-button__ripple"></span>
        <span class="mdc-button__label">My Dashboard</span>
      </a>
    </div>
  </div>

  <div class="courses-grid">
    {#each $courses as course}
      <CourseCard {course} />
    {:else}
      <div class="mdc-card info-card">
        <div class="mdc-card__content">
          <p class="mdc-typography--body1">No courses available at the moment</p>
        </div>
      </div>
    {/each}
  </div>
</main>

<style>
  main {
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .page-title {
    color: var(--mdc-theme-primary);
    text-decoration: none;
  }

  .user-section {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .welcome-text {
    color: var(--mdc-theme-on-surface);
  }

  .courses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .info-card {
    background-color: #e3f2fd;
    grid-column: 1 / -1;
  }

  .mdc-card__content {
    padding: 1rem;
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
