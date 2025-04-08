<script lang="ts">
  import '../app.css';
  import { user, token } from '$lib/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { resetDatabase } from '$lib/api';

  // Check if the current page is the login page
  $: isLoginPage = $page.url.pathname === '/login';

  // Redirect to login if not authenticated and not already on login page
  onMount(() => {
    if (!$user && !isLoginPage) {
      goto('/login');
    }
  });

  // Handle logout
  function handleLogout() {
    user.set(null);
    token.set(null);
    goto('/login');
  }

  // Handle database reset
  async function handleReset() {
    try {
      if (confirm('Are you sure you want to reset the database? This will delete all current data and replace it with dummy data.')) {
        const result = await resetDatabase();
        alert(result.message || 'Database reset successful');
        // Refresh the page to show updated data
        window.location.reload();
      }
    } catch (e) {
      const error = e instanceof Error ? e : new Error('Unknown error');
      console.error('Reset error:', error);
      alert(`Error resetting database: ${error.message}`);
    }
  }
</script>

<svelte:head>
  <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,600,700" />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Material+Icons&display=block" />
  <link rel="stylesheet" href="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css" />
  <!-- Material theme colors -->
  <style>
    :root {
      --mdc-theme-primary: #1976d2;
      --mdc-theme-secondary: #f50057;
      --mdc-theme-background: #fff;
      --mdc-theme-surface: #fff;
      --mdc-theme-error: #b00020;
      --mdc-theme-on-primary: #fff;
      --mdc-theme-on-secondary: #fff;
      --mdc-theme-on-surface: #000;
      --mdc-theme-on-error: #fff;
      --mdc-typography-font-family: 'Roboto, sans-serif';
    }

    body {
      margin: 0;
      font-family: 'Roboto', sans-serif;
      background-color: #f5f5f5;
    }
  </style>
</svelte:head>

<div class="app-container">
  {#if $user || isLoginPage}
    {#if !isLoginPage}
      <header class="app-header" style="background-color: var(--mdc-theme-primary); color: var(--mdc-theme-on-primary); padding: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
          <h1 style="margin: 0; font-size: 1.5rem;">Course Enrollment System</h1>
          <nav style="display: flex; align-items: center;">
            <a href="/" style="color: white; text-decoration: none; margin-right: 1rem;">Home</a>
            <a href="/courses" style="color: white; text-decoration: none; margin-right: 1rem;">Courses</a>
            <a href="/dashboard" style="color: white; text-decoration: none; margin-right: 1rem;">Dashboard</a>
            <a href="/departments" style="color: white; text-decoration: none; margin-right: 1rem;">Departments</a>
            <a href="/faculties" style="color: white; text-decoration: none; margin-right: 1rem;">Faculties</a>
            <a href="/instructors" style="color: white; text-decoration: none; margin-right: 1rem;">Instructors</a>
            <a href="/locations" style="color: white; text-decoration: none; margin-right: 1rem;">Locations</a>
            <a href="/programs" style="color: white; text-decoration: none; margin-right: 1rem;">Programs</a>
            <button
              on:click={handleReset}
              style="background: none; border: none; color: white; cursor: pointer; display: flex; align-items: center; margin-right: 1rem;"
            >
              <span class="material-icons" style="margin-right: 4px;">restart_alt</span>
              Reset
            </button>
            <button
              on:click={handleLogout}
              style="background: none; border: none; color: white; cursor: pointer; display: flex; align-items: center;"
            >
              <span class="material-icons" style="margin-right: 4px;">logout</span>
              Logout
            </button>
          </nav>
        </div>
      </header>
    {/if}

    <main style="max-width: 1200px; margin: 2rem auto; padding: 0 1rem;">
      <slot />
    </main>

    <footer style="background-color: #f5f5f5; padding: 1rem; text-align: center; margin-top: 2rem; border-top: 1px solid #e0e0e0;">
      <p style="margin: 0; color: #757575;">© 2025 Course Enrollment System</p>
    </footer>
  {/if}
</div>
