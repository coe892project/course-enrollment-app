<script>
    import { user } from '$lib/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';
  
    let email = '';
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
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
  
        if (response.ok) {
          const userData = await response.json();
          user.set(userData);
          goto('/dashboard');
        } else {
          error = 'Invalid email or password';
        }
      } catch (err) {
        error = 'Connection error. Please try again.';
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
        <label class="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          bind:value={email}
          required
          class="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
          placeholder="student@example.com"
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
      Don't have an account? 
      <a href="/register" class="text-blue-500 hover:underline">Register here</a>
    </div>
  </main>
  