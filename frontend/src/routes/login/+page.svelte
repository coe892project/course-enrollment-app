<script>
    import { user, token } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
    import { login } from '$lib/api';
    import { ENDPOINTS } from '$lib/config';

    let username = '';
    let password = '';
    let error = '';
    let isLoading = false;

    // Redirect if already logged in
    onMount(() => {
      if ($user) {
        goto('/dashboard');
      }
    });

    async function handleLogin() {
      isLoading = true;
      error = '';

      try {
        // Use the login function from api.js
        const tokenData = await login(username, password);

        // Store the token
        token.set(tokenData.access_token);

        // Create a simple user object since we don't have a real user API
        // In a real app, you would fetch user data from the backend
        user.set({
          id: username,
          name: username,
          role: 'user'
        });

        goto('/dashboard');
      } catch (err) {
        console.error(err);
        error = err instanceof Error ? err.message : 'Invalid username or password';
      } finally {
        isLoading = false;
      }
    }
  </script>

  <svelte:head>
    <title>Login - Course Enrollment</title>
  </svelte:head>

  <main class="max-w-md mx-auto mt-20 p-6 bg-white rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-6 text-center">Course Enrollment Login</h1>

    {#if error}
      <div class="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
    {/if}

    <form on:submit|preventDefault={handleLogin} class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Username</label>
        <input
          type="text"
          bind:value={username}
          required
          class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="username"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1">Password</label>
        <input
          type="password"
          bind:value={password}
          required
          class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="••••••••"
        />
      </div>

      <button
        type="submit"
        class="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
        disabled={isLoading}
      >
        {#if isLoading}
          <span class="animate-pulse">Logging in...</span>
        {:else}
          Login
        {/if}
      </button>
    </form>

    <div class="mt-4 text-center text-sm">
      <p>Use the credentials provided by your administrator.</p>
      <p class="mt-2">Default admin account: admin / password</p>
    </div>
  </main>
